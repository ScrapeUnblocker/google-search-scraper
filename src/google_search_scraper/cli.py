"""Command-line interface for google-search-scraper."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .export import results_to_csv
from .scraper import GoogleSearchScraper

_ENV_KEY = "SCRAPEUNBLOCKER_KEY"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="google-search-scraper",
        description="Scrape Google Search results as clean JSON or CSV, "
        "powered by ScrapeUnblocker.",
    )
    parser.add_argument("query", help="the search query")
    parser.add_argument(
        "-c",
        "--country",
        default=None,
        metavar="CC",
        help="two-letter proxy country code for geo-targeting (e.g. us, de)",
    )
    parser.add_argument(
        "-p",
        "--pages",
        type=int,
        default=1,
        help="number of result pages to collect (default: 1)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="output format (default: json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="write output to a file instead of stdout",
    )
    parser.add_argument(
        "--include-ads",
        action="store_true",
        help="include paid results in CSV output",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="include the raw upstream payload in JSON output",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not os.environ.get(_ENV_KEY):
        print(
            f"error: set {_ENV_KEY} to your ScrapeUnblocker API key (see .env.example).",
            file=sys.stderr,
        )
        return 2

    if args.pages < 1:
        print("error: --pages must be >= 1", file=sys.stderr)
        return 2

    with GoogleSearchScraper() as scraper:
        results = scraper.search(args.query, country=args.country, pages=args.pages)

    if args.format == "csv":
        text = results_to_csv(results, include_ads=args.include_ads)
    else:
        text = results.to_json(include_raw=args.raw)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {len(results.organic)} organic result(s) to {args.output}")
    else:
        sys.stdout.write(text + ("\n" if not text.endswith("\n") else ""))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
