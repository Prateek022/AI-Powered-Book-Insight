from django.db import transaction

from books.models import Book
from .insights import (
    analyze_sentiment,
    classify_genre,
    extract_themes,
    pick_highlight_quote,
    recommendation_pitch,
    summarize_book,
)
from .rag import RagEngine
from .scraper import BookScraper


class BookIngestionPipeline:
    def __init__(self):
        self.scraper = BookScraper()
        self.rag_engine = RagEngine()

    @transaction.atomic
    def scrape_and_process(self, source_url: str, max_books: int, use_selenium: bool = False):
        scraped_books = self.scraper.scrape_books(source_url=source_url, max_books=max_books, use_selenium=use_selenium)
        processed_ids = []

        for item in scraped_books:
            genre = classify_genre(item.description, item.category)
            themes = extract_themes(item.description)
            sentiment_label, sentiment_score = analyze_sentiment(item.description)
            book, _created = Book.objects.update_or_create(
                source_id=item.source_id,
                defaults={
                    "title": item.title,
                    "author": item.author,
                    "category": item.category,
                    "description": item.description,
                    "rating": item.rating,
                    "review_count": item.review_count,
                    "price": item.price,
                    "stock_status": item.stock_status,
                    "book_url": item.book_url,
                    "image_url": item.image_url,
                    "summary": summarize_book(item.title, item.description, item.category),
                    "genre_prediction": genre,
                    "recommendation_pitch": recommendation_pitch(item.title, genre, themes, sentiment_label),
                    "sentiment_label": sentiment_label,
                    "sentiment_score": sentiment_score,
                    "key_themes": themes,
                    "highlight_quote": pick_highlight_quote(item.description),
                    "processing_notes": "Processed with local insight engine, overlap chunking, and Chroma-backed retrieval.",
                    "is_processed": True,
                },
            )
            self.rag_engine.index_book(book)
            processed_ids.append(book.id)

        return {
            "source_url": source_url,
            "processed_count": len(processed_ids),
            "book_ids": processed_ids,
            "message": "Books scraped, enriched, chunked, and indexed successfully.",
        }
