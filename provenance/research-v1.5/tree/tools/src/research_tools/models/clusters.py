from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_tools.models.reports import ValidationResult


@dataclass(frozen=True)
class ValidationClusterSpec:
    cluster_id: str
    owner: str
    purpose: str
    entry_surface: str
    source_files: tuple[str, ...]


@dataclass(frozen=True)
class ValidationClusterRun:
    spec: ValidationClusterSpec
    source_files: tuple[Path, ...]
    results: tuple[ValidationResult, ...]
    passed: int
    failed: int
    warned: int
    status: str
