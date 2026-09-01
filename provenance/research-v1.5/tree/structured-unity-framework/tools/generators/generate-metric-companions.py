#!/usr/bin/env python3
"""
Generate I/C/L/U metric companions from ledger corpus.

Usage:
    python generate-metric-companions.py --corpus corpus.json --output metrics.json
    python generate-metric-companions.py --corpus corpus.json --format md --output metrics.md

Produces route-local and cross-case metrics for integration (I), continuity (C),
lag (L), and unity-like organization (U) dimensions.
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any, Tuple


@dataclass
class IMetrics:
    """Integration metrics."""
    active_directed_edges: int = 0
    possible_edges: int = 0
    occupied_edge_ratio: float = 0.0
    sigma1_units_active: int = 0
    sigma1_units_total: int = 7  # Default sigma1 set
    participation_breadth: float = 0.0
    cross_cluster_edges_unique: int = 0
    cross_cluster_edges_total: int = 0
    cross_cluster_ratio: float = 0.0
    issuing_concentration: Dict[str, int] = field(default_factory=dict)
    hub_issuer: str = ""
    hub_issuer_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CMetrics:
    """Continuity metrics."""
    total_events: int = 0
    events_with_implementation_observed: int = 0
    events_with_decision_announced: int = 0
    implementation_ratio: float = 0.0
    temporal_span_days: int = 0
    first_event_date: str = ""
    last_event_date: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LMetrics:
    """Lag metrics (placeholder - requires lag pair identification)."""
    lag_pairs_identified: int = 0
    average_lag_days: float = 0.0
    notes: str = "Lag measurement requires manual event pairing"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UMetrics:
    """Unity-like organization metrics (derived from I/C/L)."""
    integration_continuity_product: float = 0.0  # I * C proxy
    cross_case_comparability: bool = False
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RouteMetrics:
    """Complete metrics for a single route."""
    route_id: str = ""
    route_name: str = ""
    I: IMetrics = field(default_factory=IMetrics)
    C: CMetrics = field(default_factory=CMetrics)
    L: LMetrics = field(default_factory=LMetrics)
    U: UMetrics = field(default_factory=UMetrics)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'route_id': self.route_id,
            'route_name': self.route_name,
            'I': self.I.to_dict(),
            'C': self.C.to_dict(),
            'L': self.L.to_dict(),
            'U': self.U.to_dict(),
        }


# Cluster definitions for cross-cluster routing
CLUSTERS = {
    'strategic coordination': [
        'strategic executive coordination',
        'public-service system coordination'
    ],
    'response operations': [
        'public-health policy and command',
        'emergency-management coordination',
        'border-control coordination',
        'enforcement and compliance'
    ],
    'public alignment': [
        'public-information coordination'
    ]
}


def get_cluster(unit: str) -> str:
    """Determine which cluster a unit belongs to."""
    for cluster, units in CLUSTERS.items():
        if unit in units:
            return cluster
    return 'other'


def parse_date(date_str: str) -> Tuple[int, int, int]:
    """Parse YYYY-MM-DD format."""
    try:
        parts = date_str.split('-')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return (0, 0, 0)


def days_between(date1: str, date2: str) -> int:
    """Calculate days between two dates (simplified)."""
    # This is a simplified calculation - for precise results use datetime
    y1, m1, d1 = parse_date(date1)
    y2, m2, d2 = parse_date(date2)
    
    # Rough approximation: ignore month length differences
    days1 = y1 * 365 + m1 * 30 + d1
    days2 = y2 * 365 + m2 * 30 + d2
    return abs(days2 - days1)


def compute_i_metrics(events: List[Dict], route_id: str) -> IMetrics:
    """Compute Integration metrics from events."""
    m = IMetrics()
    
    # Collect all sigma1 units (issuing and receiving)
    all_units = set()
    directed_edges = set()  # (issuer, receiver) pairs
    edge_weights = defaultdict(int)  # Count occurrences
    
    for event in events:
        issuing = event.get('issuing_unit', '')
        receiving = event.get('receiving_units', [])
        
        if issuing:
            all_units.add(issuing)
            m.issuing_concentration[issuing] = m.issuing_concentration.get(issuing, 0) + 1
        
        for r in receiving:
            all_units.add(r)
            if issuing:
                edge = (issuing, r)
                directed_edges.add(edge)
                edge_weights[edge] += 1
    
    # Active directed edges
    m.active_directed_edges = len(directed_edges)
    
    # Possible edges (n * (n-1) for n units, excluding self-links)
    n = len(all_units)
    m.possible_edges = n * (n - 1) if n > 1 else 0
    m.occupied_edge_ratio = m.active_directed_edges / m.possible_edges if m.possible_edges > 0 else 0
    
    # Participation breadth
    m.sigma1_units_active = len(all_units)
    m.participation_breadth = m.sigma1_units_active / m.sigma1_units_total if m.sigma1_units_total > 0 else 0
    
    # Cross-cluster routing
    cross_cluster_edges = 0
    total_weighted = 0
    cross_cluster_weighted = 0
    
    for (issuer, receiver), weight in edge_weights.items():
        total_weighted += weight
        if get_cluster(issuer) != get_cluster(receiver):
            cross_cluster_edges += 1
            cross_cluster_weighted += weight
    
    m.cross_cluster_edges_unique = cross_cluster_edges
    m.cross_cluster_edges_total = len(directed_edges)
    m.cross_cluster_ratio = cross_cluster_weighted / total_weighted if total_weighted > 0 else 0
    
    # Hub issuer (most frequent)
    if m.issuing_concentration:
        m.hub_issuer = max(m.issuing_concentration, key=m.issuing_concentration.get)
        m.hub_issuer_count = m.issuing_concentration[m.hub_issuer]
    
    return m


def compute_c_metrics(events: List[Dict]) -> CMetrics:
    """Compute Continuity metrics from events."""
    m = CMetrics()
    m.total_events = len(events)
    
    dates = []
    for event in events:
        impl_marker = event.get('implementation_marker', '').lower()
        if 'implementation observed' in impl_marker:
            m.events_with_implementation_observed += 1
        elif 'decision announced' in impl_marker:
            m.events_with_decision_announced += 1
        
        date = event.get('timestamp_or_date', '')
        if date and date != 'unknown':
            dates.append(date)
    
    m.implementation_ratio = (
        m.events_with_implementation_observed / m.total_events 
        if m.total_events > 0 else 0
    )
    
    if dates:
        m.first_event_date = min(dates)
        m.last_event_date = max(dates)
        m.temporal_span_days = days_between(m.first_event_date, m.last_event_date)
    
    return m


def compute_l_metrics(events: List[Dict]) -> LMetrics:
    """Compute Lag metrics (placeholder - requires manual pairing)."""
    m = LMetrics()
    # Lag metrics require identifying lag pairs (announcement -> implementation events)
    # This is complex and may require manual annotation or pattern matching
    m.notes = "Lag measurement requires manual event pair identification (announcement → implementation)"
    return m


def compute_u_metrics(i: IMetrics, c: CMetrics, l: LMetrics, route_id: str) -> UMetrics:
    """Compute Unity-like organization metrics (derived)."""
    m = UMetrics()
    
    # Simple proxy: I * C product
    m.integration_continuity_product = i.occupied_edge_ratio * c.implementation_ratio
    
    # Cross-case comparability check
    # Route is comparable if it has sufficient I and C metrics
    m.cross_case_comparability = (
        i.active_directed_edges >= 5 and 
        c.total_events >= 10 and
        c.implementation_ratio > 0
    )
    
    m.notes = f"Unity-like organization proxy = I_ratio({i.occupied_edge_ratio:.3f}) * C_ratio({c.implementation_ratio:.3f}) = {m.integration_continuity_product:.3f}"
    
    return m


def generate_route_metrics(route_id: str, route_data: Dict) -> RouteMetrics:
    """Generate complete metrics for a route."""
    metrics = RouteMetrics()
    metrics.route_id = route_id
    metrics.route_name = route_data.get('metadata', {}).get('route_name', route_id)
    
    events = route_data.get('events', [])
    
    # Compute I/C/L/U
    metrics.I = compute_i_metrics(events, route_id)
    metrics.C = compute_c_metrics(events)
    metrics.L = compute_l_metrics(events)
    metrics.U = compute_u_metrics(metrics.I, metrics.C, metrics.L, route_id)
    
    return metrics


def export_json(metrics: Dict[str, RouteMetrics], output_path: Path) -> None:
    """Export metrics to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'metadata': {
            'generated_by': 'generate-metric-companions.py',
            'routes': list(metrics.keys()),
            'total_routes': len(metrics)
        },
        'routes': {rid: m.to_dict() for rid, m in metrics.items()}
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_markdown(metrics: Dict[str, RouteMetrics], output_path: Path) -> None:
    """Export metrics as human-readable Markdown."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        "# I/C/L/U Metric Companions",
        "",
        "Auto-generated from corpus data.",
        "",
        "## Summary",
        "",
    ]
    
    # Summary table
    lines.append("| Route | Events | I_ratio | C_ratio | U_proxy |")
    lines.append("|-------|--------|---------|---------|---------|")
    
    for rid, m in sorted(metrics.items()):
        lines.append(
            f"| {m.route_name} | {m.C.total_events} | "
            f"{m.I.occupied_edge_ratio:.3f} | {m.C.implementation_ratio:.3f} | "
            f"{m.U.integration_continuity_product:.3f} |"
        )
    
    lines.append("")
    
    # Detailed per-route sections
    for rid, m in sorted(metrics.items()):
        lines.extend([
            f"## {m.route_name} ({rid})",
            "",
            "### Integration (I)",
            "",
            f"- **Active directed edges**: {m.I.active_directed_edges}",
            f"- **Possible edges**: {m.I.possible_edges}",
            f"- **Occupied edge ratio**: {m.I.occupied_edge_ratio:.3f}",
            f"- **Participation breadth**: {m.I.sigma1_units_active}/{m.I.sigma1_units_total} ({m.I.participation_breadth:.1%})",
            f"- **Cross-cluster ratio**: {m.I.cross_cluster_ratio:.3f}",
            f"- **Hub issuer**: {m.I.hub_issuer} ({m.I.hub_issuer_count} events)",
            "",
            "### Continuity (C)",
            "",
            f"- **Total events**: {m.C.total_events}",
            f"- **Implementation observed**: {m.C.events_with_implementation_observed} ({m.C.implementation_ratio:.1%})",
            f"- **Decision announced**: {m.C.events_with_decision_announced}",
            f"- **Temporal span**: {m.C.temporal_span_days} days ({m.C.first_event_date} to {m.C.last_event_date})",
            "",
            "### Lag (L)",
            "",
            f"- **Status**: {m.L.notes}",
            "",
            "### Unity-like Organization (U)",
            "",
            f"- **Integration × Continuity proxy**: {m.U.integration_continuity_product:.3f}",
            f"- **Cross-case comparable**: {m.U.cross_case_comparability}",
            f"- **Notes**: {m.U.notes}",
            "",
        ])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(
        description='Generate I/C/L/U metric companions from ledger corpus'
    )
    parser.add_argument('--corpus', '-c', required=True, help='Corpus JSON file')
    parser.add_argument('--output', '-o', required=True, help='Output file')
    parser.add_argument('--format', '-f', choices=['json', 'md'], default='json',
                        help='Output format')
    args = parser.parse_args()
    
    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f"Error: Corpus file not found: {args.corpus}", file=sys.stderr)
        sys.exit(1)
    
    # Load corpus
    with open(corpus_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    # Generate metrics for each route
    routes = corpus.get('routes', {})
    metrics = {}
    
    for route_id, route_data in routes.items():
        metrics[route_id] = generate_route_metrics(route_id, route_data)
    
    # Export
    output_path = Path(args.output)
    if args.format == 'json':
        export_json(metrics, output_path)
    else:
        export_markdown(metrics, output_path)
    
    print(f"Generated metric companions for {len(metrics)} routes: {', '.join(metrics.keys())}")
    print(f"Output: {output_path}")
    
    # Print summary
    print("\nI/C/L/U Summary:")
    for rid, m in sorted(metrics.items()):
        print(f"  {m.route_name}: I={m.I.occupied_edge_ratio:.3f}, C={m.C.implementation_ratio:.3f}, U_proxy={m.U.integration_continuity_product:.3f}")


if __name__ == '__main__':
    main()
