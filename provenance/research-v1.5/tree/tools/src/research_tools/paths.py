from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class RepoPaths:
    repo_root: Path
    research_root: Path
    tools_root: Path
    suf_root: Path
    knowledge_root: Path
    out_root: Path
    governance_core: Path  # v0.2 - canonical consolidated governance
    source_registry: Path
    nz_route_root: Path
    taiwan_route_root: Path
    australia_route_root: Path
    suf_project_status: Path  # canonical status surface for ground-truth validation


@lru_cache(maxsize=1)
def get_paths() -> RepoPaths:
    module_path = Path(__file__).resolve()
    tools_root = module_path.parents[2]
    research_root = module_path.parents[3]
    repo_root = module_path.parents[4]
    suf_root = research_root / "structured-unity-framework"
    nz_route_root = (
        suf_root
        / "applications"
        / "demonstrated-routes"
        / "states-and-societies"
        / "institutional-coordination-under-perturbation"
    )
    return RepoPaths(
        repo_root=repo_root,
        research_root=research_root,
        tools_root=tools_root,
        suf_root=suf_root,
        knowledge_root=research_root / "knowledge",
        out_root=tools_root / "out",
        governance_core=research_root / "governance" / "GOVERNANCE_CORE_v0_2.json",
        source_registry=suf_root / "references" / "source-registry.md",
        nz_route_root=nz_route_root,
        taiwan_route_root=nz_route_root,
        australia_route_root=nz_route_root,
        suf_project_status=suf_root / "docs" / "project-status.md",
    )


def format_report_path(path: Path) -> str:
    resolved = path.resolve()
    repo_root = get_paths().repo_root.resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def format_optional_report_path(path_value: str | None) -> str | None:
    if not path_value:
        return None
    if "/" not in path_value and "\\" not in path_value:
        return path_value
    return format_report_path(Path(path_value))
