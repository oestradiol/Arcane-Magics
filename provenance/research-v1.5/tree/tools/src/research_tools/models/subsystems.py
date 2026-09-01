from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubsystemValidationCluster:
    cluster_id: str
    source_files: tuple[str, ...]


@dataclass(frozen=True)
class SubsystemSpec:
    subsystem_id: str
    owner: str
    purpose: str
    visibility: str
    scope_prefixes: tuple[str, ...]
    entry_surface: str
    authoritative_surface: str
    validation_cluster: SubsystemValidationCluster | None
