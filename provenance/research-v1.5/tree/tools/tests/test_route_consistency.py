from research_tools.parse.source_registry import parse_source_registry, source_registry_index
from research_tools.paths import get_paths
from research_tools.validate.route_consistency import validate_nz_route, validate_taiwan_route
from research_tools.validate.status_surfaces import validate_status_surfaces


def test_nz_route_consistency_matches_current_docs() -> None:
    paths = get_paths()
    entries = parse_source_registry(paths.source_registry)
    results = validate_nz_route(paths.nz_route_root, source_registry_index(entries))

    assert not any(result.status == "fail" for result in results)


def test_taiwan_route_consistency_matches_current_docs() -> None:
    paths = get_paths()
    entries = parse_source_registry(paths.source_registry)
    results = validate_taiwan_route(paths.taiwan_route_root, source_registry_index(entries))

    assert not any(result.status == "fail" for result in results)


def test_status_surfaces_match_current_docs() -> None:
    results = validate_status_surfaces(get_paths())

    assert not any(result.status == "fail" for result in results)


def test_status_surfaces_missing_file_fails_cleanly(tmp_path) -> None:
    import shutil
    from research_tools.paths import get_paths

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    (repo / "structured-unity-framework" / "docs" / "audit" / "OBJECTIONS_AND_EVIDENCE_STATUS.md").unlink()

    from research_tools.paths import RepoPaths
    nz_root = repo / "structured-unity-framework" / "applications" / "demonstrated-routes" / "states-and-societies" / "institutional-coordination-under-perturbation"
    paths = RepoPaths(
        repo_root=repo.parent,
        research_root=repo,
        tools_root=repo / "tools",
        suf_root=repo / "structured-unity-framework",
        knowledge_root=repo / "knowledge",
        out_root=repo / "tools" / "out",
        source_registry=repo / "structured-unity-framework" / "references" / "source-registry.md",
        nz_route_root=nz_root,
        taiwan_route_root=nz_root,
    )

    results = validate_status_surfaces(paths)

    assert any(result.status == "fail" and "unavailable" in result.message for result in results)


def test_status_surfaces_malformed_citation_version_fails_cleanly(tmp_path) -> None:
    import shutil
    from research_tools.paths import get_paths, RepoPaths

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    (repo / "CITATION.cff").write_text("title: test\n", encoding="utf-8")

    nz_root = repo / "structured-unity-framework" / "applications" / "demonstrated-routes" / "states-and-societies" / "institutional-coordination-under-perturbation"
    paths = RepoPaths(
        repo_root=repo.parent,
        research_root=repo,
        tools_root=repo / "tools",
        suf_root=repo / "structured-unity-framework",
        knowledge_root=repo / "knowledge",
        out_root=repo / "tools" / "out",
        source_registry=repo / "structured-unity-framework" / "references" / "source-registry.md",
        nz_route_root=nz_root,
        taiwan_route_root=nz_root,
    )

    results = validate_status_surfaces(paths)

    assert any(result.check_name == "status-citation-version-readable" and result.status == "fail" for result in results)



def test_validate_versions_malformed_citation_fails_cleanly(tmp_path) -> None:
    import shutil
    from research_tools.paths import get_paths, RepoPaths
    from research_tools.validate.versions import validate_versions

    source = get_paths().research_root
    repo = tmp_path / "repo"
    shutil.copytree(source, repo)
    (repo / "CITATION.cff").write_text("title: test\n", encoding="utf-8")

    nz_root = repo / "structured-unity-framework" / "applications" / "demonstrated-routes" / "states-and-societies" / "institutional-coordination-under-perturbation"
    paths = RepoPaths(
        repo_root=repo.parent,
        research_root=repo,
        tools_root=repo / "tools",
        suf_root=repo / "structured-unity-framework",
        knowledge_root=repo / "knowledge",
        out_root=repo / "tools" / "out",
        source_registry=repo / "structured-unity-framework" / "references" / "source-registry.md",
        nz_route_root=nz_root,
        taiwan_route_root=nz_root,
    )

    results = validate_versions(paths)

    assert any(result.check_name == "versions-umbrella-citation-version" and result.status == "fail" for result in results)
