"""Unit tests for the CLI - the scraper is patched, no network is used."""

from __future__ import annotations

import json

import pytest

from google_search_scraper import cli
from google_search_scraper.models import AdResult, OrganicResult, SearchResults


def sample_results():
    return SearchResults(
        query="q",
        country="us",
        total_results=42,
        organic=[OrganicResult(1, "Title", "https://ex.com", "desc")],
        ads=[AdResult("top", 1, "Ad", "https://ad.com", "buy")],
        ai_overview=None,
    )


class FakeScraper:
    last_kwargs: dict = {}

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def search(self, query, **kwargs):
        FakeScraper.last_kwargs = {"query": query, **kwargs}
        return sample_results()


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    monkeypatch.setenv("SCRAPEUNBLOCKER_KEY", "test-key")
    monkeypatch.setattr(cli, "GoogleSearchScraper", FakeScraper)


def test_parser_defaults():
    args = cli.build_parser().parse_args(["hello world"])
    assert args.query == "hello world"
    assert args.pages == 1
    assert args.format == "json"
    assert args.country is None


def test_parser_flags():
    args = cli.build_parser().parse_args(
        ["q", "-c", "de", "-p", "2", "-f", "csv", "--include-ads"]
    )
    assert args.country == "de"
    assert args.pages == 2
    assert args.format == "csv"
    assert args.include_ads is True


def test_main_json_stdout(capsys):
    rc = cli.main(["python tools", "-c", "us"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["organic"][0]["title"] == "Title"
    assert FakeScraper.last_kwargs["country"] == "us"


def test_main_csv_output_file(tmp_path):
    dest = tmp_path / "out.csv"
    rc = cli.main(["q", "-f", "csv", "--include-ads", "-o", str(dest)])
    assert rc == 0
    text = dest.read_text(encoding="utf-8")
    assert "kind,placement,position,title,url,description" in text
    assert "organic" in text and "ad" in text


def test_main_requires_api_key(monkeypatch, capsys):
    monkeypatch.delenv("SCRAPEUNBLOCKER_KEY", raising=False)
    rc = cli.main(["q"])
    assert rc == 2
    assert "SCRAPEUNBLOCKER_KEY" in capsys.readouterr().err
