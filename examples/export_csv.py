"""Search Google and export the results to a CSV file.

Usage:
    export SCRAPEUNBLOCKER_KEY=your_key_here
    python examples/export_csv.py "best running shoes" results.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

from google_search_scraper import GoogleSearchScraper
from google_search_scraper.export import results_to_csv


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "best running shoes"
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "results.csv")

    with GoogleSearchScraper() as scraper:
        results = scraper.search(query, country="us", pages=2)

    out_path.write_text(results_to_csv(results, include_ads=True), encoding="utf-8")
    print(f"Wrote {len(results.organic)} organic result(s) to {out_path}")


if __name__ == "__main__":
    main()
