"""Unit tests for GoogleSearchScraper - the SDK client is fully mocked."""

from __future__ import annotations

import pytest
from scrapeunblocker import BlockedError, RateLimitError, UpstreamOutageError

from google_search_scraper import GoogleSearchScraper
from google_search_scraper.models import SearchResults


def make_scraper(client, **kwargs):
    kwargs.setdefault("retry_backoff", 0)  # never sleep in tests
    return GoogleSearchScraper(client=client, **kwargs)


def test_normalize_shapes_results(fake_client_factory, sample_serp):
    scraper = make_scraper(fake_client_factory(sample_serp))
    results = scraper.search("web scraping tools", country="us")

    assert isinstance(results, SearchResults)
    assert results.query == "web scraping tools"
    assert results.country == "us"
    assert results.total_results == 124000
    assert len(results.organic) == 2

    first = results.organic[0]
    assert first.position == 1
    assert first.url == "https://www.example.com/blog/best-web-scrapers"

    # Relative Google redirect links are resolved to absolute URLs.
    assert results.organic[1].url == "https://www.google.com/goto?url=abc123"

    # Ads are flattened with a placement tag.
    assert [a.placement for a in results.ads] == ["top"]
    assert results.ads[0].title == "Enterprise Scraping API"

    assert results.ai_overview is not None
    assert "automate" in results.ai_overview.text


def test_search_passes_arguments(fake_client_factory, sample_serp):
    client = fake_client_factory(sample_serp)
    make_scraper(client).search("pizza", country="it", pages=3)
    call = client.calls[0]
    assert call["keyword"] == "pizza"
    assert call["proxy_country"] == "it"
    assert call["pages_to_check"] == 3


def test_to_dict_and_json_roundtrip(fake_client_factory, sample_serp):
    results = make_scraper(fake_client_factory(sample_serp)).search("q")
    as_dict = results.to_dict()
    assert set(as_dict) == {
        "query",
        "country",
        "total_results",
        "organic",
        "ads",
        "ai_overview",
    }
    assert "raw" not in as_dict
    assert "raw" in results.to_dict(include_raw=True)
    assert results.to_json().startswith("{")


@pytest.mark.parametrize("bad", ["", "   "])
def test_empty_query_rejected(fake_client_factory, sample_serp, bad):
    with pytest.raises(ValueError):
        make_scraper(fake_client_factory(sample_serp)).search(bad)


def test_zero_pages_rejected(fake_client_factory, sample_serp):
    with pytest.raises(ValueError):
        make_scraper(fake_client_factory(sample_serp)).search("q", pages=0)


def test_retries_transient_then_succeeds(fake_client_factory, sample_serp):
    responses = [
        UpstreamOutageError("upstream down", status_code=503),
        RateLimitError("slow down", status_code=429),
        sample_serp,
    ]
    client = fake_client_factory(responses)
    results = make_scraper(client, max_retries=3).search("q")
    assert len(client.calls) == 3
    assert results.total_results == 124000


def test_retries_exhausted_reraises(fake_client_factory):
    err = UpstreamOutageError("still down", status_code=503)
    client = fake_client_factory([err, err, err])
    with pytest.raises(UpstreamOutageError):
        make_scraper(client, max_retries=3).search("q")
    assert len(client.calls) == 3


def test_client_errors_not_retried(fake_client_factory):
    client = fake_client_factory(BlockedError("blocked", status_code=403))
    with pytest.raises(BlockedError):
        make_scraper(client).search("q")
    assert len(client.calls) == 1  # no retry on a hard client error


def test_close_only_closes_owned_client(fake_client_factory, sample_serp):
    client = fake_client_factory(sample_serp)
    # Injected clients are not owned, so the scraper must not close them.
    scraper = make_scraper(client)
    scraper.close()
    assert client.closed is False


def test_api_key_and_client_are_mutually_exclusive(fake_client_factory, sample_serp):
    with pytest.raises(ValueError):
        GoogleSearchScraper(api_key="x", client=fake_client_factory(sample_serp))
