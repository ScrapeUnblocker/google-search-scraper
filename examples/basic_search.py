"""Run a single Google search and print the organic results.

Usage:
    export SCRAPEUNBLOCKER_KEY=your_key_here
    python examples/basic_search.py "web scraping tools"
"""

from __future__ import annotations

import sys

from google_search_scraper import GoogleSearchScraper


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "web scraping tools"

    with GoogleSearchScraper() as scraper:
        results = scraper.search(query, country="us")

    print(f"Query: {results.query!r}  (~{results.total_results} total results)\n")
    for hit in results.organic:
        print(f"{hit.position:>2}. {hit.title}")
        print(f"    {hit.url}")


if __name__ == "__main__":
    main()
