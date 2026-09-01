"""Sync governance state for v0_2 consolidated governance.

Per ADR-0003 and COMPRESSION_MIGRATION_PLAN_v0_2:
- REGISTRY_MANIFEST_v0_2.json contains full file catalog with SHA256
- INTEGRITY_MANIFEST is derived at validation time from GOVERNANCE_CORE.current_surfaces
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools" / "src"))

from research_tools.repo_files import iter_truth_files
from research_tools.generate.integrity_manifest import generate_integrity_manifest_v2


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _actual_files(repo_root: Path, scope_prefix: str = "") -> list[str]:
    files = iter_truth_files(repo_root)
    if scope_prefix:
        files = [rel for rel in files if rel.startswith(scope_prefix)]
    return sorted(files)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sync_registry_manifest_v2(registry_path: Path, repo_root: Path) -> None:
    """Sync REGISTRY_MANIFEST_v0_2.json with current file tree state."""
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    
    # Build full file catalog with SHA256
    files = _actual_files(repo_root, "")
    registry['files'] = [
        {
            'path': rel,
            'sha256': _sha(repo_root / rel),
            'size_bytes': (repo_root / rel).stat().st_size
        }
        for rel in files
    ]
    registry['file_count'] = len(files)
    registry['updated'] = hashlib.sha256(str(Path().stat()).encode()).hexdigest()[:8]  # Simple timestamp proxy
    
    _write_json(registry_path, registry)
    print(f"Synced {registry['file_count']} files to {registry_path.name}")


def derive_integrity_manifest_v2(
    governance_core_path: Path,
    registry_manifest_path: Path,
    output_path: Path | None = None,
) -> dict:
    """Derive integrity manifest from the canonical generator path."""
    repo_root = governance_core_path.parent.parent
    integrity = generate_integrity_manifest_v2(
        repo_root=repo_root,
        governance_core_path=governance_core_path,
        registry_manifest_path=registry_manifest_path,
        output_path=output_path,
    )
    if output_path:
        print(
            f"Derived integrity manifest: {integrity['file_count']} current surfaces -> {output_path.name}"
        )
    return integrity


def main() -> None:
    parser = argparse.ArgumentParser(description='Sync v0_2 governance state')
    parser.add_argument('--derive-integrity', action='store_true',
                        help='Derive integrity manifest from current surfaces')
    parser.add_argument('--output-integrity', type=Path, default=None,
                        help='Output path for derived integrity manifest')
    args = parser.parse_args()

    gov_core = BASE / 'governance/GOVERNANCE_CORE_v0_2.json'
    reg_manifest = BASE / 'governance/REGISTRY_MANIFEST_v0_2.json'
    
    # Sync registry manifest
    sync_registry_manifest_v2(reg_manifest, BASE)
    
    # Derive integrity if requested
    if args.derive_integrity:
        derive_integrity_manifest_v2(
            gov_core,
            reg_manifest,
            args.output_integrity or BASE / 'governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json'
        )
        print('Governance state synced and integrity manifest derived.')
    else:
        print('Governance state synced. Use --derive-integrity to compute current surface integrity.')


if __name__ == '__main__':
    main()
