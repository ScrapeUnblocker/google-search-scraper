"""Shared test fixtures and a sample serpApi payload."""

from __future__ import annotations

import pytest

SAMPLE_SERP = {
    "totalResults": 124000,
    "keyword": "web scraping tools",
    "proxyCountry": "us",
    "topAds": [
        {
            "title": "Enterprise Scraping API",
            "url": "https://example-ad.com/",
            "description": "Scale your data collection.",
            "position": 1,
        }
    ],
    "bottomAds": [],
    "aiOverview": {
        "text": "Web scraping tools automate extracting data from websites.",
        "sources": [],
    },
    "organic": [
        {
            "title": "5 best web scraper tools",
            "url": "https://www.example.com/blog/best-web-scrapers",
            "description": "A round-up of scraping tools.",
            "position": 1,
        },
        {
            # A relative Google redirect link - should be made absolute.
            "title": "Reddit thread on scraping",
            "url": "/goto?url=abc123",
            "description": "Community picks.",
            "position": 2,
        },
    ],
}


class FakeClient:
    """Stand-in for ``scrapeunblocker.Client`` that returns canned data.

    ``responses`` may contain dicts (returned) or exception instances (raised),
    consumed in order; a single value is reused for every call.
    """

    def __init__(self, responses):
        if not isinstance(responses, list):
            responses = [responses]
        self._responses = responses
        self.calls: list[dict] = []
        self.closed = False

    def serp(self, keyword, **kwargs):
        self.calls.append({"keyword": keyword, **kwargs})
        item = self._responses[min(len(self.calls) - 1, len(self._responses) - 1)]
        if isinstance(item, Exception):
            raise item
        return item

    def close(self):
        self.closed = True


@pytest.fixture
def sample_serp():
    return dict(SAMPLE_SERP)


@pytest.fixture
def fake_client_factory():
    return FakeClient
