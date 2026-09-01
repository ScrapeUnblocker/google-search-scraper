"""Print Google's AI Overview block for a query, when one is shown.

Usage:
    export SCRAPEUNBLOCKER_KEY=your_key_here
    python examples/ai_overview.py "how does solar power work"
"""

from __future__ import annotations

import sys

from google_search_scraper import GoogleSearchScraper


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "how does solar power work"

    with GoogleSearchScraper() as scraper:
        results = scraper.search(query, country="us")

    if results.ai_overview:
        print("AI Overview:\n")
        print(results.ai_overview.text)
    else:
        print("No AI Overview was shown for this query.")


if __name__ == "__main__":
    main()
