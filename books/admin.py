from django.contrib import admin

from .models import Book, BookChunk, QueryLog


class BookChunkInline(admin.TabularInline):
    model = BookChunk
    extra = 0
    readonly_fields = ("chunk_index", "heading", "token_count", "content", "created_at")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "rating", "genre_prediction", "is_processed")
    list_filter = ("category", "genre_prediction", "sentiment_label", "is_processed")
    search_fields = ("title", "author", "description")
    inlines = [BookChunkInline]


@admin.register(BookChunk)
class BookChunkAdmin(admin.ModelAdmin):
    list_display = ("book", "chunk_index", "heading", "token_count")
    list_filter = ("book",)
    search_fields = ("book__title", "content")


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("book", "cache_hit", "latency_ms", "created_at")
    list_filter = ("cache_hit", "book")
    search_fields = ("book__title", "question", "answer")
