from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .serializers import (
    AskQuestionSerializer,
    BookDetailSerializer,
    BookListSerializer,
    BookScrapeRequestSerializer,
    QueryLogSerializer,
)
from .services.pipeline import BookIngestionPipeline
from .services.rag import RagEngine


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all().order_by("-rating", "title")
    serializer_class = BookListSerializer


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer


class BookRecommendationsView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        recommendations = RagEngine().recommend_related_books(book, limit=4)
        return Response({"book_id": book.id, "recommendations": recommendations})


class BookScrapeView(APIView):
    def post(self, request):
        serializer = BookScrapeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pipeline = BookIngestionPipeline()
        result = pipeline.scrape_and_process(**serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)


class AskQuestionView(APIView):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        engine = RagEngine()
        answer = engine.answer_book_question(book, serializer.validated_data["question"])
        return Response(answer)


class QueryHistoryView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = QueryLogSerializer(book.queries.all()[:10], many=True)
        return Response({"book_id": book.id, "history": serializer.data})


class OverviewView(APIView):
    def get(self, request):
        books = Book.objects.all()
        categories = {}
        for book in books:
            key = book.genre_prediction or book.category or "Unknown"
            categories[key] = categories.get(key, 0) + 1
        top_genres = sorted(
            [{"genre": genre, "count": count} for genre, count in categories.items()],
            key=lambda item: item["count"],
            reverse=True,
        )[:5]
        return Response(
            {
                "total_books": books.count(),
                "processed_books": books.filter(is_processed=True).count(),
                "top_genres": top_genres,
                "average_rating": round(sum(book.rating for book in books) / books.count(), 2) if books else 0,
            }
        )
