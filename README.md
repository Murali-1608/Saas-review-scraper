# SaaS Review Scraper (G2 & Capterra)

## Overview
This project is a **CLI-based Python script** designed to scrape SaaS product reviews from **G2** and **Capterra** for a given company and time period.  
The script accepts user inputs via command-line arguments and outputs the collected reviews in a structured **JSON format**.

The project is implemented with a focus on **clean architecture**, **robust error handling**, and **real-world data ingestion behavior**.

---

## Features
- Scrape reviews from **G2** or **Capterra**
- Accepts dynamic inputs:
  - Company name
  - Start date
  - End date
  - Review source
- Handles pagination safely
- Detects and handles access restrictions gracefully
- Outputs structured JSON with execution metadata
- Supports **dry-run mode** for safe execution

---

## Input Parameters

| Argument | Description |
|--------|-------------|
| `company` | Company name (e.g., Chargebee) |
| `source` | Review source (`g2` or `capterra`) |
| `start_date` | Start date (YYYY-MM-DD) |
| `end_date` | End date (YYYY-MM-DD) |
| `dry-run` | (Optional) Fetch only one page without pagination |

### Example Command and JSON Output
```bash
python -m src.main --company "Chargebee" --source g2 --start_date 2024-06-01 --end_date 2024-07-31

Output

{
  "metadata": {
    "company": "Chargebee",
    "source": "g2",
    "start_date": "2024-06-01",
    "end_date": "2024-07-31",
    "total_reviews": 0,
    "scrape_status": "RESTRICTED",
    "execution_time_sec": 0.14,
    "scraped_at": "2025-12-25T12:50:28Z"
  },
  "reviews": []
}

