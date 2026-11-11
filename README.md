# google-search-scraper

[![CI](https://github.com/ScrapeUnblocker/google-search-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/ScrapeUnblocker/google-search-scraper/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Scrape Google Search results as clean, typed JSON — organic listings, ads, the AI Overview block, and total counts — with country targeting and multi-page collection.**

Powered by [ScrapeUnblocker](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos): Google gets rendered and unblocked on the server side, so you get structured results back instead of a CAPTCHA page. No proxies, browsers, or headless infrastructure to run yourself.

## Features

- 🔎 **Organic results** — title, URL, description, and position.
- 💸 **Ads** — top and bottom paid placements, tagged by placement.
- 🤖 **AI Overview** — Google's generative answer block, when present.
- 🌍 **Country targeting** — pass a two-letter country code for geo-specific results.
- 📄 **Multi-page collection** — pull several result pages in one call.
- 🧱 **Typed models** — dataclasses with `to_dict()` / `to_json()`, plus CSV export.
- 🔁 **Automatic retries** on transient upstream errors, with backoff.
- 🖥️ **CLI + library** — use it from the shell or import it into your code.

## Install

```bash
pip install .
# or, for development:
pip install -e ".[dev]"
```

Set your API key (get one at [scrapeunblocker.com](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos)):

```bash
cp .env.example .env
export SCRAPEUNBLOCKER_KEY=your_key_here
```

The key is read from the `SCRAPEUNBLOCKER_KEY` environment variable — it is never
hard-coded and never committed.

## CLI usage

```bash
# Print organic results as JSON
google-search-scraper "web scraping tools" --country us

# Collect two pages and export to CSV, including ads
google-search-scraper "best running shoes" --pages 2 --format csv --include-ads -o shoes.csv

# See the full options
google-search-scraper --help
```

## Library usage

```python
from google_search_scraper import GoogleSearchScraper

with GoogleSearchScraper() as scraper:  # reads SCRAPEUNBLOCKER_KEY
    results = scraper.search("web scraping tools", country="us", pages=1)

print(results.total_results)  # ~124000
for hit in results.organic:
    print(hit.position, hit.title, hit.url)

if results.ai_overview:
    print(results.ai_overview.text)

data = results.to_dict()  # JSON-ready dict
```

### Example output

```json
{
  "query": "web scraping tools",
  "country": "us",
  "total_results": 124000,
  "organic": [
    {
      "position": 1,
      "title": "5 best web scraper tools",
      "url": "https://www.example.com/blog/best-web-scrapers",
      "description": "A round-up of scraping tools."
    }
  ],
  "ads": [
    {
      "placement": "top",
      "position": 1,
      "title": "Enterprise Scraping API",
      "url": "https://example-ad.com/",
      "description": "Scale your data collection."
    }
  ],
  "ai_overview": {
    "text": "Web scraping tools automate extracting data from websites.",
    "sources": []
  }
}
```

## Project layout

```
src/google_search_scraper/
  __init__.py     # package exports + version
  models.py       # OrganicResult / AdResult / AiOverview / SearchResults
  scraper.py      # GoogleSearchScraper: search + normalise + retries
  export.py       # CSV export helper
  cli.py          # argparse command-line interface
examples/         # runnable scripts: basic search, CSV export, AI Overview
tests/            # offline unit tests (SDK mocked, no API credit spent)
```

## Development

```bash
make install      # editable install with dev extras
make lint         # ruff check
make format       # ruff format
make test         # pytest (fully offline / mocked)
```

Tests mock the ScrapeUnblocker SDK, so `make test` spends no API credit and needs
no network access.

## How it works

This package calls ScrapeUnblocker's `serpApi` endpoint through the official
[`scrapeunblocker`](https://docs.scrapeunblocker.com/sdks/python?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
Python SDK and normalises the response into typed dataclasses. Google's
anti-bot handling, rendering, and geo-routing all happen on ScrapeUnblocker's
side — you just get structured data.

## Links

- 🌐 Product: <https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos>
- 📚 Docs: <https://docs.scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos>
- 🔧 SERP guide: <https://docs.scrapeunblocker.com/guides/serp-scraping?utm_source=github&utm_medium=integration&utm_campaign=example-repos>

## License

[MIT](LICENSE) © 2026 ScrapeUnblocker
