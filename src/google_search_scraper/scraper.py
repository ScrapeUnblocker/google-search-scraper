"""The :class:`GoogleSearchScraper` high-level client."""

from __future__ import annotations

import time
from typing import Any

from scrapeunblocker import (
    Client,
    RateLimitError,
    ScrapeUnblockerError,
    ServerError,
    UpstreamOutageError,
)

from .models import AdResult, AiOverview, OrganicResult, SearchResults

_GOOGLE_BASE = "https://www.google.com"

# Transient conditions worth retrying with backoff. Client errors (bad request,
# auth, blocked) are raised straight through - a retry would not help.
_RETRYABLE = (UpstreamOutageError, ServerError, RateLimitError)


def _abs_url(url: str | None) -> str | None:
    """Resolve Google's relative ``/goto?...`` and ``/url?...`` links to absolute."""
    if not url:
        return url
    if url.startswith("/"):
        return _GOOGLE_BASE + url
    return url


class GoogleSearchScraper:
    """Scrape Google Search results via the ScrapeUnblocker ``serpApi`` endpoint.

    Wraps the official ``scrapeunblocker`` SDK and normalises each response into a
    :class:`~google_search_scraper.models.SearchResults` instance.

    The API key is read from the ``SCRAPEUNBLOCKER_KEY`` environment variable by
    the underlying SDK; pass ``api_key`` to override, or inject your own
    ``client`` (handy for testing).
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: Client | None = None,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ) -> None:
        if client is not None and api_key is not None:
            raise ValueError("pass either api_key or client, not both")
        self._client = client if client is not None else Client(api_key=api_key)
        self._owns_client = client is None
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

    # -- context manager -------------------------------------------------
    def __enter__(self) -> GoogleSearchScraper:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying SDK client (only if this instance created it)."""
        if self._owns_client:
            self._client.close()

    # -- public API ------------------------------------------------------
    def search(
        self,
        query: str,
        *,
        country: str | None = None,
        pages: int = 1,
        wait_after_load: int = 0,
    ) -> SearchResults:
        """Run a Google search and return normalised results.

        :param query: the search query.
        :param country: two-letter proxy country code (e.g. ``"us"``, ``"de"``)
            for geo-targeted results, or ``None`` for the default.
        :param pages: number of result pages to collect (``>= 1``).
        :param wait_after_load: extra seconds to wait after the page loads, for
            slow-rendering SERP features.
        """
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string")
        if pages < 1:
            raise ValueError("pages must be >= 1")

        raw = self._call_with_retries(
            query,
            proxy_country=country,
            pages_to_check=pages,
            wait_after_load=wait_after_load,
        )
        return self._normalize(query, country, raw)

    # -- internals -------------------------------------------------------
    def _call_with_retries(self, query: str, **kwargs: Any) -> dict[str, Any]:
        attempt = 0
        while True:
            try:
                result = self._client.serp(query, **kwargs)
                if not isinstance(result, dict):
                    raise ScrapeUnblockerError(
                        f"unexpected serp response type: {type(result).__name__}"
                    )
                return result
            except _RETRYABLE:
                attempt += 1
                if attempt >= self.max_retries:
                    raise
                if self.retry_backoff:
                    time.sleep(self.retry_backoff * attempt)

    @staticmethod
    def _normalize(
        query: str, country: str | None, raw: dict[str, Any]
    ) -> SearchResults:
        organic = [
            OrganicResult(
                position=int(item.get("position", idx + 1)),
                title=item.get("title", "") or "",
                url=_abs_url(item.get("url")),
                description=item.get("description", "") or "",
            )
            for idx, item in enumerate(raw.get("organic") or [])
        ]

        ads: list[AdResult] = []
        for placement, key in (("top", "topAds"), ("bottom", "bottomAds")):
            for item in raw.get(key) or []:
                ads.append(
                    AdResult(
                        placement=placement,
                        position=int(item.get("position", 0)),
                        title=item.get("title", "") or "",
                        url=_abs_url(item.get("url")),
                        description=item.get("description", "") or "",
                    )
                )

        ai_overview = None
        ai_raw = raw.get("aiOverview")
        if isinstance(ai_raw, dict) and (ai_raw.get("text") or ai_raw.get("sources")):
            ai_overview = AiOverview(
                text=ai_raw.get("text", "") or "",
                sources=list(ai_raw.get("sources") or []),
            )

        total = raw.get("totalResults")
        return SearchResults(
            query=query,
            country=country,
            total_results=int(total) if isinstance(total, (int, float)) else total,
            organic=organic,
            ads=ads,
            ai_overview=ai_overview,
            raw=raw,
        )
