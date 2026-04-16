import re
from collections import Counter


GENRE_KEYWORDS = {
    "Fantasy": ["magic", "dragon", "kingdom", "quest", "sword", "myth"],
    "Mystery": ["murder", "secret", "detective", "clue", "crime", "mystery"],
    "Romance": ["love", "heart", "relationship", "passion", "marriage", "romance"],
    "Science Fiction": ["future", "technology", "space", "alien", "science", "robot"],
    "Historical Fiction": ["war", "empire", "history", "century", "royal", "victorian"],
    "Thriller": ["danger", "conspiracy", "escape", "survival", "spy", "threat"],
    "Philosophy": ["meaning", "ethics", "truth", "mind", "society", "reason"],
}

POSITIVE_WORDS = {"brilliant", "moving", "beautiful", "hope", "joy", "love", "wonder", "inspiring", "charming"}
NEGATIVE_WORDS = {"dark", "grim", "tragic", "fear", "loss", "sad", "pain", "betrayal", "violent"}
STOPWORDS = {
    "the", "and", "with", "that", "from", "into", "their", "about", "after", "before", "where", "there",
    "have", "this", "will", "your", "book", "story", "novel", "reader", "into", "been", "over", "when",
}


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]


def summarize_book(title: str, description: str, category: str) -> str:
    sentences = split_sentences(description)
    if not sentences:
        return f"{title} is a {category or 'fiction'} title with limited source description, positioned as an intriguing discovery in the collection."
    summary_core = " ".join(sentences[:2])
    return f"{summary_core} This title sits in the {category or 'general'} lane and stands out for its concise but vivid setup."


def classify_genre(description: str, category: str) -> str:
    haystack = f"{category} {description}".lower()
    scores = {
        genre: sum(1 for keyword in keywords if keyword in haystack)
        for genre, keywords in GENRE_KEYWORDS.items()
    }
    best_genre = max(scores, key=scores.get)
    return best_genre if scores[best_genre] > 0 else (category.title() if category else "General Fiction")


def analyze_sentiment(description: str) -> tuple[str, float]:
    tokens = re.findall(r"[a-z']+", description.lower())
    positives = sum(1 for token in tokens if token in POSITIVE_WORDS)
    negatives = sum(1 for token in tokens if token in NEGATIVE_WORDS)
    score = positives - negatives
    if score > 1:
        return "optimistic", min(1.0, score / 5)
    if score < -1:
        return "dark", max(-1.0, score / 5)
    return "balanced", 0.0


def extract_themes(description: str) -> list[str]:
    tokens = [
        token for token in re.findall(r"[a-z']+", description.lower())
        if len(token) > 4 and token not in STOPWORDS
    ]
    counts = Counter(tokens)
    return [word.title() for word, _count in counts.most_common(4)]


def recommendation_pitch(title: str, genre: str, themes: list[str], sentiment_label: str) -> str:
    theme_text = ", ".join(themes[:3]) if themes else "character tension and atmosphere"
    return (
        f"If you enjoy {genre.lower()} shaped by {theme_text}, {title} is a strong next pick. "
        f"Its overall tone reads as {sentiment_label}, which makes it useful for mood-based discovery as well as genre browsing."
    )


def pick_highlight_quote(description: str) -> str:
    sentences = split_sentences(description)
    if not sentences:
        return "No descriptive quote was available from the source page."
    return max(sentences, key=len)
