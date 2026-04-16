import hashlib
import math
import re
import time
from collections import Counter
from pathlib import Path

import chromadb

from books.models import Book, BookChunk, QueryLog
from .cache import MemoryAnswerCache


class LocalHashEmbeddingFunction:
    @staticmethod
    def name():
        return "local-hash-embedding"

    def __call__(self, input):
        return [self.embed_text(text) for text in input]

    def embed_documents(self, input):
        return [self.embed_text(text) for text in input]

    def embed_query(self, input):
        if isinstance(input, list):
            input = " ".join(str(item) for item in input)
        return [self.embed_text(input)]

    def embed_text(self, text: str, dimensions: int = 128):
        vector = [0.0] * dimensions
        tokens = re.findall(r"[a-z0-9']+", text.lower())
        if not tokens:
            return vector
        counts = Counter(tokens)
        for token, weight in counts.items():
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            slot = int(digest[:8], 16) % dimensions
            sign = -1.0 if int(digest[8:10], 16) % 2 else 1.0
            vector[slot] += sign * float(weight)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class RagEngine:
    def __init__(self):
        self.embedding = LocalHashEmbeddingFunction()
        self.use_chroma = True
        self.collection = None
        chroma_path = Path(__file__).resolve().parents[2] / "runtime" / "chroma"
        chroma_path.mkdir(parents=True, exist_ok=True)
        try:
            self.client = chromadb.PersistentClient(path=str(chroma_path))
            self.collection = self.client.get_or_create_collection(
                name="book_chunks",
                embedding_function=self.embedding,
            )
        except Exception:
            self.use_chroma = False
            self.client = None

    @staticmethod
    def chunk_text(book: Book) -> list[dict]:
        source = "\n".join(
            [
                f"Title: {book.title}",
                f"Author: {book.author}",
                f"Category: {book.category}",
                f"Description: {book.description}",
                f"Summary: {book.summary}",
                f"Genre: {book.genre_prediction}",
                f"Recommendation: {book.recommendation_pitch}",
                f"Sentiment: {book.sentiment_label}",
            ]
        )
        words = source.split()
        window = 60
        overlap = 18
        chunks = []
        start = 0
        index = 0
        while start < len(words):
            segment = words[start : start + window]
            if not segment:
                break
            content = " ".join(segment)
            chunks.append(
                {
                    "chunk_index": index,
                    "heading": f"{book.title} context {index + 1}",
                    "content": content,
                    "token_count": len(segment),
                }
            )
            if start + window >= len(words):
                break
            start += window - overlap
            index += 1
        return chunks

    def index_book(self, book: Book):
        chunk_records = self.chunk_text(book)
        existing_chunk_ids = [f"book-{book.id}-chunk-{chunk.chunk_index}" for chunk in book.chunks.all()]
        if existing_chunk_ids and self.use_chroma and self.collection is not None:
            self.collection.delete(ids=existing_chunk_ids)
        if existing_chunk_ids:
            book.chunks.all().delete()

        chunk_models = [
            BookChunk(book=book, chunk_index=item["chunk_index"], heading=item["heading"], content=item["content"], token_count=item["token_count"])
            for item in chunk_records
        ]
        BookChunk.objects.bulk_create(chunk_models)
        stored_chunks = list(book.chunks.all())

        if self.use_chroma and self.collection is not None:
            self.collection.add(
                ids=[f"book-{book.id}-chunk-{chunk.chunk_index}" for chunk in stored_chunks],
                documents=[chunk.content for chunk in stored_chunks],
                metadatas=[
                    {
                        "book_id": book.id,
                        "book_title": book.title,
                        "chunk_index": chunk.chunk_index,
                        "heading": chunk.heading,
                    }
                    for chunk in stored_chunks
                ],
            )

    def answer_book_question(self, book: Book, question: str):
        cache_key = f"{book.id}:{question.strip().lower()}"
        cached = MemoryAnswerCache.get(cache_key)
        if cached:
            cached["cache_hit"] = True
            QueryLog.objects.create(
                book=book,
                question=question,
                answer=cached["answer"],
                citations=cached["citations"],
                latency_ms=0,
                cache_hit=True,
            )
            return cached

        started = time.perf_counter()
        if self.use_chroma and self.collection is not None:
            result = self.collection.query(
                query_texts=[question],
                n_results=3,
                where={"book_id": book.id},
            )
            documents = result["documents"][0] if result["documents"] else []
            metadatas = result["metadatas"][0] if result["metadatas"] else []
        else:
            documents, metadatas = self.local_similarity_query(book, question, n_results=3)
        answer = self.compose_answer(book, question, documents, metadatas)
        elapsed = int((time.perf_counter() - started) * 1000)
        payload = {
            "book_id": book.id,
            "question": question,
            "answer": answer["answer"],
            "citations": answer["citations"],
            "context_windows": answer["context_windows"],
            "cache_hit": False,
            "latency_ms": elapsed,
        }
        MemoryAnswerCache.set(cache_key, payload.copy())
        QueryLog.objects.create(
            book=book,
            question=question,
            answer=payload["answer"],
            citations=payload["citations"],
            latency_ms=payload["latency_ms"],
            cache_hit=False,
        )
        return payload

    def local_similarity_query(self, book: Book, question: str, n_results: int = 3):
        question_embedding = self.embedding.embed_text(question)
        scored = []
        for chunk in book.chunks.all():
            chunk_embedding = self.embedding.embed_text(chunk.content)
            similarity = sum(a * b for a, b in zip(question_embedding, chunk_embedding))
            scored.append(
                (
                    similarity,
                    chunk.content,
                    {
                        "book_id": book.id,
                        "book_title": book.title,
                        "chunk_index": chunk.chunk_index,
                        "heading": chunk.heading,
                    },
                )
            )
        top_chunks = sorted(scored, key=lambda item: item[0], reverse=True)[:n_results]
        return [item[1] for item in top_chunks], [item[2] for item in top_chunks]

    def compose_answer(self, book: Book, question: str, documents: list[str], metadatas: list[dict]):
        context_lines = documents[:3]
        context = " ".join(context_lines)
        answer = (
            f"Based on the indexed material for {book.title}, the strongest answer is: "
            f"{self.extract_relevant_sentence(context, question)} "
            f"This interpretation is grounded in the book summary, description, and derived insight layers."
        )
        citations = [
            {
                "chunk": item.get("chunk_index", 0),
                "heading": item.get("heading", ""),
                "label": f"{item.get('book_title')} chunk {item.get('chunk_index', 0) + 1}",
            }
            for item in metadatas
        ]
        return {
            "answer": answer.strip(),
            "citations": citations,
            "context_windows": context_lines,
        }

    @staticmethod
    def extract_relevant_sentence(context: str, question: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", context)
        question_terms = set(re.findall(r"[a-z0-9']+", question.lower()))
        if not sentences:
            return "The source text is limited, but the indexed context still points to the core themes and positioning of the book."
        ranked = sorted(
            sentences,
            key=lambda sentence: sum(1 for token in re.findall(r"[a-z0-9']+", sentence.lower()) if token in question_terms),
            reverse=True,
        )
        return ranked[0].strip()

    def recommend_related_books(self, book: Book, limit: int = 4):
        other_books = Book.objects.exclude(id=book.id)
        scored = []
        book_terms = set(re.findall(r"[a-z0-9']+", f"{book.genre_prediction} {book.description} {' '.join(book.key_themes)}".lower()))
        for candidate in other_books:
            candidate_terms = set(
                re.findall(r"[a-z0-9']+", f"{candidate.genre_prediction} {candidate.description} {' '.join(candidate.key_themes)}".lower())
            )
            overlap = len(book_terms & candidate_terms)
            score = overlap + max(0, 5 - abs(candidate.rating - book.rating))
            scored.append(
                {
                    "id": candidate.id,
                    "title": candidate.title,
                    "author": candidate.author,
                    "genre_prediction": candidate.genre_prediction,
                    "summary": candidate.summary,
                    "book_url": candidate.book_url,
                    "why": f"Shares thematic overlap around {', '.join((book.key_themes or candidate.key_themes)[:2]) or 'character-driven tension'} and sits near the same mood/quality band.",
                    "score": score,
                }
            )
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]
