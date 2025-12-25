import argparse
import json
import os
import time
from datetime import datetime

from src.scraper.g2 import G2Scraper
from src.scraper.capterra import CapterraScraper


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Review Scraper for G2 and Capterra"
    )

    parser.add_argument(
        "--company",
        required=True,
        help="Company name (e.g., Chargebee)"
    )

    parser.add_argument(
        "--source",
        required=True,
        choices=["g2", "capterra"],
        help="Review source: g2 or capterra"
    )

    parser.add_argument(
        "--start_date",
        required=True,
        help="Start date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--end_date",
        required=True,
        help="End date (YYYY-MM-DD)"
    )

    # Dry-run mode (safe execution)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run scraper for a single page without pagination"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")

    # Choose scraper
    if args.source == "g2":
        scraper = G2Scraper(args.company, start_date, end_date)
    else:
        scraper = CapterraScraper(args.company, start_date, end_date)

    # Pass dry-run flag safely
    scraper.dry_run = args.dry_run

    # Run scraper with execution timing
    start_time = time.time()
    reviews = scraper.scrape()
    end_time = time.time()

    # Use runtime-detected outcome from BaseScraper
    scrape_status = (
        scraper.last_outcome.value
        if hasattr(scraper, "last_outcome") and scraper.last_outcome
        else "UNKNOWN"
    )

    # Metadata + results payload
    output_payload = {
        "metadata": {
            "company": args.company,
            "source": args.source,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "total_reviews": len(reviews),
            "scrape_status": scrape_status,
            "execution_time_sec": round(end_time - start_time, 2),
            "scraped_at": datetime.utcnow().isoformat() + "Z"
        },
        "reviews": reviews
    }

    # Prepare output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_file = f"{args.company.lower().replace(' ', '_')}_{args.source}_reviews.json"
    output_path = os.path.join(output_dir, output_file)

    # Save JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    # Console summary
    print("\n Scraping completed successfully!")
    print(f" Reviews saved to: {output_path}")
    print(f" Total reviews collected: {len(reviews)}")
    print(f" Scrape status: {scrape_status}")


if __name__ == "__main__":
    main()
