from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.paths import get_paths
from research_tools.reports.nz_summary import compute_route_summary


def test_taiwan_ledger_parser_matches_current_public_counts() -> None:
    events = parse_taiwan_ledger(get_paths().taiwan_route_root / "taiwan-event-ledger-seed.md")
    summary = compute_route_summary("taiwan", events)

    assert summary.event_count == 15
    assert summary.active_units == 6
    assert summary.active_edges == 20
    assert summary.public_information_receiving_count == 15
