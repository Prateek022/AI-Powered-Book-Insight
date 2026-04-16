from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse(
        {
            "service": "Libriscope Document Intelligence API",
            "version": "v1",
            "endpoints": {
                "books": "/api/books/",
                "scrape": "/api/books/upload/",
                "detail": "/api/books/<id>/",
                "recommendations": "/api/books/<id>/recommendations/",
                "ask": "/api/books/<id>/ask/",
            },
        }
    )

urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/", include("books.urls")),
]
