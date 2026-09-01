"""CSV export helpers for :class:`SearchResults`."""

from __future__ import annotations

import csv
import io

from .models import SearchResults

_ORGANIC_FIELDS = ["kind", "placement", "position", "title", "url", "description"]


def results_to_csv(results: SearchResults, *, include_ads: bool = False) -> str:
    """Render a SERP as CSV text (one row per result).

    Organic results are always included; ads are added when ``include_ads`` is set.
    The ``kind`` column is ``"organic"`` or ``"ad"`` and ``placement`` is empty for
    organic rows.
    """
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_ORGANIC_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for hit in results.organic:
        writer.writerow(
            {
                "kind": "organic",
                "placement": "",
                "position": hit.position,
                "title": hit.title,
                "url": hit.url,
                "description": hit.description,
            }
        )
    if include_ads:
        for ad in results.ads:
            writer.writerow(
                {
                    "kind": "ad",
                    "placement": ad.placement,
                    "position": ad.position,
                    "title": ad.title,
                    "url": ad.url,
                    "description": ad.description,
                }
            )
    return buf.getvalue()
