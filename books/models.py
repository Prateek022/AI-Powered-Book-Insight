from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Book(TimeStampedModel):
    source_id = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock_status = models.CharField(max_length=120, blank=True)
    book_url = models.URLField(unique=True)
    image_url = models.URLField(blank=True)
    scraped_from = models.CharField(max_length=120, default="books.toscrape.com")
    summary = models.TextField(blank=True)
    genre_prediction = models.CharField(max_length=120, blank=True)
    recommendation_pitch = models.TextField(blank=True)
    sentiment_label = models.CharField(max_length=40, blank=True)
    sentiment_score = models.FloatField(default=0.0)
    key_themes = models.JSONField(default=list, blank=True)
    highlight_quote = models.TextField(blank=True)
    processing_notes = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class BookChunk(TimeStampedModel):
    book = models.ForeignKey(Book, related_name="chunks", on_delete=models.CASCADE)
    chunk_index = models.PositiveIntegerField()
    heading = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["book_id", "chunk_index"]
        unique_together = ("book", "chunk_index")

    def __str__(self):
        return f"{self.book.title} :: chunk {self.chunk_index}"


class QueryLog(TimeStampedModel):
    book = models.ForeignKey(Book, related_name="queries", on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    citations = models.JSONField(default=list, blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    cache_hit = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Q&A for {self.book.title}"
