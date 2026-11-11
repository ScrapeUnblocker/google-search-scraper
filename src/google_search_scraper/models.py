"""Typed, JSON-serialisable models for a Google SERP."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrganicResult:
    """A single organic (non-paid) Google result."""

    position: int
    title: str
    url: str | None
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "title": self.title,
            "url": self.url,
            "description": self.description,
        }


@dataclass
class AdResult:
    """A paid result. ``placement`` is ``"top"`` or ``"bottom"``."""

    placement: str
    position: int
    title: str
    url: str | None
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "placement": self.placement,
            "position": self.position,
            "title": self.title,
            "url": self.url,
            "description": self.description,
        }


@dataclass
class AiOverview:
    """Google's AI Overview block, when present."""

    text: str
    sources: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "sources": self.sources}


@dataclass
class SearchResults:
    """A normalised Google Search response for a single query."""

    query: str
    country: str | None
    total_results: int | None
    organic: list[OrganicResult] = field(default_factory=list)
    ads: list[AdResult] = field(default_factory=list)
    ai_overview: AiOverview | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self, *, include_raw: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "query": self.query,
            "country": self.country,
            "total_results": self.total_results,
            "organic": [r.to_dict() for r in self.organic],
            "ads": [a.to_dict() for a in self.ads],
            "ai_overview": self.ai_overview.to_dict() if self.ai_overview else None,
        }
        if include_raw:
            out["raw"] = self.raw
        return out

    def to_json(self, *, indent: int | None = 2, include_raw: bool = False) -> str:
        return json.dumps(self.to_dict(include_raw=include_raw), ensure_ascii=False, indent=indent)
