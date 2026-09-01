from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    check_name: str
    status: str
    message: str
    path: str | None = None
    expected: str | None = None
    found: str | None = None


@dataclass(frozen=True)
class RouteSummary:
    route_name: str
    event_count: int
    main_interval_count: int | None
    active_units: int
    active_edges: int
    occupied_edge_ratio: float
    weighted_cross_cluster_numerator: int
    weighted_cross_cluster_denominator: int
    weighted_cross_cluster_share: float
    top_issuer: str
    top_issuers: tuple[str, ...]
    top_issuer_count: int
    public_information_receiving_count: int
    mean_receiving_breadth: float


@dataclass(frozen=True)
class WindowSummary:
    label: str
    event_count: int
    sigma3_event_count: int
    public_information_marked_count: int
    mean_receiving_breadth: float
    active_units: int
    sec_issuing_count: int
    sec_issuing_denominator: int
    weighted_cross_cluster_numerator: int
    weighted_cross_cluster_denominator: int
