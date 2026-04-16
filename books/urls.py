from django.urls import path

from .views import AskQuestionView, BookDetailView, BookListView, BookRecommendationsView, BookScrapeView, OverviewView, QueryHistoryView


urlpatterns = [
    path("overview/", OverviewView.as_view(), name="overview"),
    path("books/", BookListView.as_view(), name="book-list"),
    path("books/upload/", BookScrapeView.as_view(), name="book-scrape"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/recommendations/", BookRecommendationsView.as_view(), name="book-recommendations"),
    path("books/<int:pk>/ask/", AskQuestionView.as_view(), name="book-ask"),
    path("books/<int:pk>/queries/", QueryHistoryView.as_view(), name="book-query-history"),
]
