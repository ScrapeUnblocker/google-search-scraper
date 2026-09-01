"""Scrape Google Search results as clean, typed JSON.

``google_search_scraper`` wraps the official `ScrapeUnblocker
<https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos>`_
``serpApi`` endpoint and normalises Google's SERP into JSON-serialisable
dataclasses: organic listings, ads, the AI Overview block, and total counts,
with country targeting and multi-page collection.

Basic usage::

    from google_search_scraper import GoogleSearchScraper

    with GoogleSearchScraper() as scraper:           # reads SCRAPEUNBLOCKER_KEY
        results = scraper.search("web scraping tools", country="us")
        for hit in results.organic:
            print(hit.position, hit.title, hit.url)
"""

from __future__ import annotations

from .models import AdResult, AiOverview, OrganicResult, SearchResults
from .scraper import GoogleSearchScraper

__all__ = [
    "GoogleSearchScraper",
    "SearchResults",
    "OrganicResult",
    "AdResult",
    "AiOverview",
    "__version__",
]

__version__ = "0.1.0"
