from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.paths import get_paths
from research_tools.reports.nz_summary import compute_nz_window_summaries, compute_route_summary


def test_nz_ledger_parser_matches_current_public_counts() -> None:
    events = parse_nz_ledger(get_paths().nz_route_root / "event-ledger-seed.md")
    summary = compute_route_summary("nz", events)
    windows = compute_nz_window_summaries(events)

    assert summary.event_count == 38
    assert summary.main_interval_count == 29
    assert summary.active_edges == 24
    assert summary.public_information_receiving_count == 33
    assert windows["Main perturbation interval"].event_count == 29
    assert windows["Main perturbation interval"].sigma3_event_count == 27
