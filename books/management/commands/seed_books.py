from django.core.management.base import BaseCommand

from books.services.pipeline import BookIngestionPipeline


class Command(BaseCommand):
    help = "Scrape and process a starter set of books for the demo."

    def add_arguments(self, parser):
        parser.add_argument("--max-books", type=int, default=12)
        parser.add_argument("--use-selenium", action="store_true")

    def handle(self, *args, **options):
        pipeline = BookIngestionPipeline()
        result = pipeline.scrape_and_process(
            source_url="https://books.toscrape.com/",
            max_books=options["max_books"],
            use_selenium=options["use_selenium"],
        )
        self.stdout.write(self.style.SUCCESS(str(result)))
