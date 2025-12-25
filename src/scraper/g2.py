from bs4 import BeautifulSoup
from datetime import datetime
import logging

from src.scraper.base import BaseScraper

class G2Scraper(BaseScraper):
    """
    Scraper for G2 reviews
    """

    BASE_URL = "https://www.g2.com/products"

    def __init__(self, company_name: str, start_date, end_date):
        super().__init__(company_name, start_date, end_date)
        self.company_slug = self.company_name.lower().replace(" ", "-")

    def build_review_url(self, page: int) -> str:
        """
        Build paginated G2 review URL
        """
        return (
            f"{self.BASE_URL}/{self.company_slug}/reviews"
            f"?page={page}"
        )

    def parse_reviews(self, html: str) -> list:
        """
        Parse reviews from G2 HTML
        """
        soup = BeautifulSoup(html, "html.parser")
        review_blocks = soup.find_all("div", class_="paper")

        reviews = []

        for block in review_blocks:
            try:
                title_tag = block.find("h3")
                body_tag = block.find("p")
                rating_tag = block.find("span", class_="fw-semibold")
                date_tag = block.find("time")

                title = title_tag.get_text(strip=True) if title_tag else None
                body = body_tag.get_text(strip=True) if body_tag else None
                rating = float(rating_tag.get_text(strip=True)) if rating_tag else None

                review_date = None
                if date_tag and date_tag.has_attr("datetime"):
                    review_date = datetime.fromisoformat(
                        date_tag["datetime"].replace("Z", "")
                    )

                # Date filtering
                if review_date:
                    if review_date < self.start_date:
                        logging.info("Reached reviews older than start date. Stopping.")
                        return []

                    if review_date > self.end_date:
                        continue

                reviews.append({
                    "source": "g2",
                    "company": self.company_name,
                    "title": title,
                    "review_text": body,
                    "rating": rating,
                    "review_date": review_date.isoformat() if review_date else None
                })

            except Exception as e:
                logging.warning(f"Failed to parse a review block: {e}")
                continue

        return reviews