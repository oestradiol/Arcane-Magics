from __future__ import annotations

SIGMA1_UNITS = (
    "strategic executive coordination",
    "public-health policy and command",
    "emergency-management coordination",
    "public-service system coordination",
    "border-control coordination",
    "enforcement and compliance",
    "public-information coordination",
)

UNIT_TO_CLUSTER = {
    "strategic executive coordination": "strategic coordination",
    "public-health policy and command": "response operations",
    "emergency-management coordination": "response operations",
    "public-service system coordination": "strategic coordination",
    "border-control coordination": "response operations",
    "enforcement and compliance": "response operations",
    "public-information coordination": "public alignment",
}

POSSIBLE_DIRECTED_EDGES = len(SIGMA1_UNITS) * (len(SIGMA1_UNITS) - 1)

NZ_EVENT_PREFIXES = {
    "comparator_a": "nz-a-",
    "main": "nz-p-",
    "comparator_b": "nz-b-",
}

TAIWAN_EVENT_PREFIXES = {
    "architecture": "tw-a-",
    "main": "tw-p-",
}

ARCHIVE_WILDCARD_MARKERS = (
    "web.archive.org/web/*",
    "wayback/available",
    "/save/http",
    "/save/https",
    "web.archive.org/save/",
)

NATIVE_FIXED_ARCHIVE_PREFIXES = (
    "https://plato.stanford.edu/archives/",
)
