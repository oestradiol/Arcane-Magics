"""Parser for GOVERNANCE_CORE_v0_2.json consolidated governance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CurrentSurfaces:
    root_entrypoints: tuple[str, ...]
    root_governance: tuple[str, ...]
    package_entrypoints: dict[str, str]
    assisted_use: str


@dataclass(frozen=True)
class SubsystemSpec:
    subsystem_id: str
    owner: str
    purpose: str
    visibility: str
    scope_prefixes: tuple[str, ...]
    entry: str | None
    state_surface: str | None
    validation_policy: str | None
    surfaces: tuple[str, ...]


@dataclass(frozen=True)
class ActorClass:
    actor_id: str
    authority: str
    reads_first: tuple[str, ...]


@dataclass(frozen=True)
class GovernanceCore:
    version: str
    updated: str
    principles: dict[str, str]
    current_surfaces: CurrentSurfaces
    subsystems: dict[str, SubsystemSpec]
    actor_classes: dict[str, ActorClass]
    trust_order: tuple[str, ...]
    edit_scope_policy: dict[str, Any]
    renewal_cycle: dict[str, Any]


def _parse_current_surfaces(raw: dict) -> CurrentSurfaces:
    return CurrentSurfaces(
        root_entrypoints=tuple(raw["root_entrypoints"]),
        root_governance=tuple(raw["root_governance"]),
        package_entrypoints=raw["package_entrypoints"],
        assisted_use=raw["assisted_use"],
    )


def _parse_subsystem(subsystem_id: str, raw: dict) -> SubsystemSpec:
    return SubsystemSpec(
        subsystem_id=subsystem_id,
        owner=raw["owner"],
        purpose=raw["purpose"],
        visibility=raw["visibility"],
        scope_prefixes=tuple(raw["scope_prefixes"]),
        entry=raw.get("entry"),
        state_surface=raw.get("state_surface"),
        validation_policy=raw.get("validation_policy"),
        surfaces=tuple(raw.get("surfaces", [])),
    )


def _parse_actor_class(actor_id: str, raw: dict) -> ActorClass:
    return ActorClass(
        actor_id=actor_id,
        authority=raw["authority"],
        reads_first=tuple(raw["reads_first"]),
    )


def parse_governance_core(path: Path) -> GovernanceCore:
    """Parse GOVERNANCE_CORE_v0_2.json into typed structure."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    
    return GovernanceCore(
        version=raw["version"],
        updated=raw["updated"],
        principles=raw["principles"],
        current_surfaces=_parse_current_surfaces(raw["current_surfaces"]),
        subsystems={
            sid: _parse_subsystem(sid, sdata)
            for sid, sdata in raw["subsystems"].items()
        },
        actor_classes={
            aid: _parse_actor_class(aid, adata)
            for aid, adata in raw["actor_classes"].items()
        },
        trust_order=tuple(raw["trust_order"]),
        edit_scope_policy=raw["edit_scope_policy"],
        renewal_cycle=raw["renewal_cycle"],
    )


def derive_subsystem_validation_cluster(
    subsystem: SubsystemSpec,
    governance_core_path: Path,
) -> list[str] | None:
    """Derive validation cluster source files from subsystem spec.
    
    For v0.2, validation cluster is derived from:
    - subsystem.entry (if exists)
    - subsystem.state_surface (if exists) 
    - subsystem.validation_policy (if exists)
    - subsystem.surfaces (if exists)
    
    Returns None if subsystem has no validation-relevant surfaces.
    """
    sources = []
    
    if subsystem.entry:
        sources.append(subsystem.entry)
    if subsystem.state_surface:
        sources.append(subsystem.state_surface)
    if subsystem.validation_policy:
        sources.append(subsystem.validation_policy)
    sources.extend(subsystem.surfaces)
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for s in sources:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    
    return unique if unique else None


def get_all_current_surface_paths(governance: GovernanceCore) -> list[str]:
    """Return all paths that should be in integrity manifest."""
    paths = []
    paths.extend(governance.current_surfaces.root_entrypoints)
    paths.extend(governance.current_surfaces.root_governance)
    paths.extend(governance.current_surfaces.package_entrypoints.values())
    paths.append(governance.current_surfaces.assisted_use)
    
    # Add subsystem state surfaces
    for subsys in governance.subsystems.values():
        if subsys.state_surface:
            paths.append(subsys.state_surface)
        if subsys.entry:
            paths.append(subsys.entry)
    
    # Deduplicate
    seen = set()
    unique = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    
    return unique
