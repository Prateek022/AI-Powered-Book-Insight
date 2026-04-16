from rest_framework import serializers

from .models import Book, BookChunk, QueryLog


class BookChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookChunk
        fields = ("chunk_index", "heading", "content", "token_count")


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "category",
            "rating",
            "review_count",
            "description",
            "book_url",
            "image_url",
            "summary",
            "genre_prediction",
            "recommendation_pitch",
            "sentiment_label",
            "key_themes",
        )


class BookDetailSerializer(serializers.ModelSerializer):
    chunks = BookChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = "__all__"


class BookScrapeRequestSerializer(serializers.Serializer):
    source_url = serializers.URLField(required=False, default="https://books.toscrape.com/")
    max_books = serializers.IntegerField(required=False, min_value=1, max_value=40, default=12)
    use_selenium = serializers.BooleanField(required=False, default=False)


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)


class QueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryLog
        fields = ("id", "question", "answer", "citations", "latency_ms", "cache_hit", "created_at")
