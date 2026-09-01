from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


class AuthorityError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_manifest(manifest_rel: str) -> dict:
    manifest_path = BASE / manifest_rel
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    mismatches = []
    checked = 0
    for entry in manifest['files']:
        target = BASE / entry['path']
        checked += 1
        if not target.exists():
            mismatches.append({'path': entry['path'], 'reason': 'missing'})
            continue
        actual = _sha256(target)
        if actual != entry['sha256']:
            mismatches.append({'path': entry['path'], 'reason': 'hash-mismatch', 'expected': entry['sha256'], 'found': actual})
    return {
        'manifest': manifest_rel,
        'status': 'PASS' if not mismatches else 'FAIL',
        'verified_files': checked,
        'mismatches': mismatches,
    }


def verify_integrity(strict: bool = True) -> dict:
    reports = [_verify_manifest('governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json'), _verify_manifest('structured-unity-framework/governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_1.json')]
    mismatches = [m for report in reports for m in report['mismatches']]
    status = 'PASS' if not mismatches else 'FAIL'
    summary = {'status': status, 'reports': reports, 'verified_files': sum(report['verified_files'] for report in reports)}
    if strict and mismatches:
        raise AuthorityError(json.dumps(summary, ensure_ascii=False))
    return summary
