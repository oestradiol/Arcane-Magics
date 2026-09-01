from __future__ import annotations

import json
from pathlib import Path

from research_tools.models.subsystems import SubsystemSpec, SubsystemValidationCluster


def parse_subsystem_registry(path: Path) -> list[SubsystemSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    subsystems: list[SubsystemSpec] = []
    for item in raw["subsystems"]:
        raw_cluster = item.get("validation_cluster")
        validation_cluster = None
        if raw_cluster is not None:
            validation_cluster = SubsystemValidationCluster(
                cluster_id=raw_cluster["cluster_id"],
                source_files=tuple(raw_cluster["source_files"]),
            )
        subsystems.append(
            SubsystemSpec(
                subsystem_id=item["id"],
                owner=item["owner"],
                purpose=item["purpose"],
                visibility=item["visibility"],
                scope_prefixes=tuple(item["scope_prefixes"]),
                entry_surface=item["entry_surface"],
                authoritative_surface=item["authoritative_surface"],
                validation_cluster=validation_cluster,
            )
        )
    return subsystems
