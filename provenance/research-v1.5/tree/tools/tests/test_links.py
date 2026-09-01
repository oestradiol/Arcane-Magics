from pathlib import Path

from research_tools.paths import get_paths
from research_tools.validate.links import validate_markdown_links


def test_link_validator_catches_missing_relative_target(tmp_path: Path) -> None:
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "a.md").write_text("[ok](b.md)\n[bad](missing.md)\n", encoding="utf-8")
    (docs_root / "b.md").write_text("hello\n", encoding="utf-8")

    results = validate_markdown_links(docs_root)

    assert any(result.status == "fail" for result in results)
    assert any(result.expected == "missing.md" for result in results if result.status == "fail")


def test_research_markdown_links_resolve() -> None:
    paths = get_paths()
    results = validate_markdown_links(paths.research_root)

    assert not any(result.status == "fail" for result in results)
