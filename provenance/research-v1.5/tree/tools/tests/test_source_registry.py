from research_tools.parse.source_registry import parse_source_registry
from research_tools.paths import get_paths
from research_tools.validate.archives import validate_archive_links
from research_tools.validate.sources import validate_source_registry


def test_source_registry_parses_current_public_registry() -> None:
    entries = parse_source_registry(get_paths().source_registry)

    assert len(entries) > 20
    assert any(entry.source_id == "src-taiwan-cecc-activation-2020" for entry in entries)


def test_source_registry_and_archive_validators_pass_on_current_state() -> None:
    entries = parse_source_registry(get_paths().source_registry)

    source_results = validate_source_registry(entries)
    archive_results = validate_archive_links(entries)

    assert not any(result.status == "fail" for result in source_results)
    assert not any(result.status == "fail" for result in archive_results)


def test_sep_archive_editions_are_accepted_as_fixed_archives() -> None:
    entries = parse_source_registry(get_paths().source_registry)
    archive_results = validate_archive_links(entries)
    sep_failures = [
        result
        for result in archive_results
        if result.path in {
            "src-sep-relational-quantum-mechanics-2025",
            "src-sep-quantum-mechanics-2025",
        }
    ]

    assert not sep_failures
