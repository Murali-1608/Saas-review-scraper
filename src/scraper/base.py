import requests
import time
import logging
from abc import ABC, abstractmethod
from enum import Enum


class ScrapeOutcome(Enum):
    SUCCESS = "SUCCESS"
    EMPTY = "EMPTY"
    RESTRICTED = "RESTRICTED"


class BaseScraper(ABC):
    """
    Abstract base class for all review scrapers
    """

    def __init__(self, company_name: str, start_date, end_date):
        self.company_name = company_name
        self.start_date = start_date
        self.end_date = end_date

        self.session = requests.Session()
        self.session.headers.update(self._default_headers())

        # Track last scrape outcome
        self.last_outcome = None

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _default_headers(self) -> dict:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

    def fetch_page(self, url: str, delay: float = 1.5):
        """
        Fetch page and detect runtime outcome
        """
        try:
            logging.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=10)

            # Explicit access restriction detection
            if response.status_code == 403:
                logging.warning("Access restricted by platform (403).")
                self.last_outcome = ScrapeOutcome.RESTRICTED
                return None

            response.raise_for_status()
            time.sleep(delay)

            self.last_outcome = ScrapeOutcome.SUCCESS
            return response.text

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            self.last_outcome = ScrapeOutcome.EMPTY
            return None

    @abstractmethod
    def build_review_url(self, page: int) -> str:
        pass

    @abstractmethod
    def parse_reviews(self, html: str) -> list:
        pass

    def scrape(self) -> list:
        all_reviews = []
        page = 1
        MAX_PAGES = 10  # Guard rail

        while page <= MAX_PAGES:
            html = self.fetch_page(self.build_review_url(page))

            # Adaptive exit on restriction
            if self.last_outcome == ScrapeOutcome.RESTRICTED:
                logging.info("Stopping scrape due to access restriction.")
                break

            if not html:
                self.last_outcome = ScrapeOutcome.EMPTY
                break

            reviews = self.parse_reviews(html)
            if not reviews:
                self.last_outcome = ScrapeOutcome.EMPTY
                break

            all_reviews.extend(reviews)

            # Dry-run support (optional, if set from main.py)
            if getattr(self, "dry_run", False):
                logging.info("Dry-run enabled. Stopping after first page.")
                break

            page += 1

        logging.info(
            f"Scrape completed | Outcome: {self.last_outcome} | Reviews: {len(all_reviews)}"
        )
        return all_reviews
