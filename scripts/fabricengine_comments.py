"""Shared device-level comments for FabricEngine device types."""
from __future__ import annotations

import re

FE_BASE = "Dual-persona Universal Hardware running Fabric Engine (VOSS)."

SERIES_DATASHEETS: dict[str, tuple[str, str]] = {
    "4000": (
        "4000 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/4000-Series-Data-Sheet",
    ),
    "5120": (
        "5120 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5120-Series-Data-Sheet",
    ),
    "5320": (
        "5320 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5320-Series-Data-Sheet",
    ),
    "5420": (
        "5420 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5420-Series-Data-Sheet",
    ),
    "5520": (
        "5520 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5520-Series-Data-Sheet",
    ),
    "5720": (
        "5720 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5720-Series-Data-Sheet",
    ),
    "7520": (
        "7520 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/7520-Series-Data-Sheet",
    ),
    "7720": (
        "7720 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/7720-Series-Data-Sheet",
    ),
    "7830": (
        "7830 Series",
        "https://extr-p-001.sitecorecontenthub.cloud/api/public/content/7830-series-data-sheet",
    ),
}


def series_key(part_number: str) -> str:
    if re.match(r"^(4120|4220)-", part_number):
        return "4000"
    for prefix in (
        "7830",
        "7720",
        "7520",
        "5720",
        "5520",
        "5420",
        "5320",
        "5120",
    ):
        if part_number.startswith(prefix):
            return prefix
    raise ValueError(f"Unknown FabricEngine series for {part_number!r}")


def build_comments(part_number: str) -> str:
    series_name, url = SERIES_DATASHEETS[series_key(part_number)]
    return f"{FE_BASE} [{series_name} Datasheet]({url})"
