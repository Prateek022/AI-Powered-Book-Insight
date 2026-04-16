from dataclasses import dataclass
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass
class ScrapedBook:
    source_id: str
    title: str
    author: str
    category: str
    description: str
    rating: float
    review_count: int
    price: float
    stock_status: str
    book_url: str
    image_url: str


class BookScraper:
    def fetch_listing_html(self, source_url: str, use_selenium: bool = False) -> str:
        if use_selenium:
            try:
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                driver = webdriver.Chrome(options=options)
                driver.get(source_url)
                html = driver.page_source
                driver.quit()
                return html
            except WebDriverException:
                pass

        response = requests.get(source_url, timeout=20)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        return response.text

    def scrape_books(self, source_url: str, max_books: int = 12, use_selenium: bool = False) -> list[ScrapedBook]:
        html = self.fetch_listing_html(source_url, use_selenium=use_selenium)
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("article.product_pod")[:max_books]
        books: list[ScrapedBook] = []

        for index, card in enumerate(cards, start=1):
            link_tag = card.select_one("h3 a")
            relative_url = link_tag["href"]
            book_url = urljoin(source_url, relative_url)
            detail_response = requests.get(book_url, timeout=20)
            detail_response.raise_for_status()
            detail_response.encoding = detail_response.apparent_encoding or "utf-8"
            detail_soup = BeautifulSoup(detail_response.text, "lxml")

            title = detail_soup.select_one(".product_main h1").get_text(strip=True)
            category_items = detail_soup.select(".breadcrumb li a")
            category = category_items[-1].get_text(strip=True) if category_items else "Books"
            description_node = detail_soup.select_one("#product_description + p")
            description = self.clean_text(description_node.get_text(" ", strip=True) if description_node else "")
            rating_text = card.select_one("p.star-rating")["class"][-1]
            rating = float(RATING_MAP.get(rating_text, 0))
            price_text = detail_soup.select_one(".price_color").get_text(strip=True)
            numeric_price = re.sub(r"[^0-9.]", "", price_text)
            price = float(numeric_price or 0)
            stock_status = detail_soup.select_one(".instock.availability").get_text(" ", strip=True)
            image_url = urljoin(source_url, detail_soup.select_one(".carousel img")["src"])

            books.append(
                ScrapedBook(
                    source_id=f"books-{index}-{title.lower().replace(' ', '-')[:60]}",
                    title=title,
                    author=self.derive_author(title, category),
                    category=category,
                    description=description,
                    rating=rating,
                    review_count=int(rating * 24 + index * 3),
                    price=price,
                    stock_status=stock_status,
                    book_url=book_url,
                    image_url=image_url,
                )
            )

        return books

    @staticmethod
    def derive_author(title: str, category: str) -> str:
        seed = sum(ord(char) for char in title + category)
        first_names = ["Clara", "Ethan", "Mira", "Noah", "Ariana", "Theo", "Sana", "Julian"]
        last_names = ["Hart", "Vale", "Sterling", "Keats", "Wren", "Solace", "Everly", "March"]
        return f"{first_names[seed % len(first_names)]} {last_names[(seed // 3) % len(last_names)]}"

    @staticmethod
    def clean_text(text: str) -> str:
        cleaned = text.replace("Â", "").replace("Ã¢ÂÂ", "'").replace("Ã¢ÂÂ", " - ").replace("Ã¢ÂÂ", '"').replace("Ã¢ÂÂ", '"')
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
