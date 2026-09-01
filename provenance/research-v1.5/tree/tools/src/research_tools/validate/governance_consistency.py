"""
Governance consistency validator.

Checks that governance files are internally consistent and reference only existing files.
This closes the self-coverage gap where the system can validate others but not itself.
"""

from pathlib import Path
from typing import List, Dict, Set, Tuple
import json
import re

from research_tools.models.reports import ValidationResult


# Category drift detection patterns
CATEGORY_DRIFT_PATTERNS = {
    'consciousness_inflation': {
        'risk_terms': ['consciousness', 'conscious', 'aware', 'subjectivity'],
        'allowed_contexts': [
            'unity-like organization',
            'structural description',
            'modeling vocabulary',
            'not a claim of'
        ],
        'severity': 'warn',
        'message': 'Potential consciousness language inflation: use "unity-like organization" unless interpretive extension is intended'
    },
    'proof_claims': {
        'risk_terms': ['proves', 'proof that', 'proven', 'demonstrates conclusively'],
        'allowed_contexts': [
            'not established',
            'deferred',
            'does not claim'
        ],
        'severity': 'fail',
        'message': 'Category drift: strong proof language in interpretive/speculative context'
    },
    'ontology_hardening': {
        'risk_terms': ['is', 'are', 'exists', 'reality is', 'the world is'],
        'blocked_sections': ['epistemic', 'givenness', 'bracket'],
        'severity': 'warn',
        'message': 'Potential ontological hardening: epistemic claims treated as ontological'
    }
}


def load_json(path: Path) -> Dict:
    """Load JSON file safely."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def check_file_exists(path: Path, repo_root: Path) -> Tuple[bool, str]:
    """Check if a file exists in the repository."""
    full_path = repo_root / path
    exists = full_path.exists()
    return exists, str(full_path)


def check_current_surfaces_registry(registry_path: Path, repo_root: Path) -> List[Tuple[str, str]]:
    """
    Check CURRENT_SURFACES_REGISTRY for:
    - All listed files actually exist
    - No stale references to deleted files
    """
    issues = []
    registry = load_json(registry_path)
    
    current_files = registry.get('current_files', [])
    
    for file_ref in current_files:
        exists, full_path = check_file_exists(file_ref, repo_root)
        if not exists:
            issues.append(('missing_file', f"File listed in CURRENT_SURFACES_REGISTRY does not exist: {file_ref}"))
    
    return issues


def check_integrity_manifest(manifest_path: Path, repo_root: Path) -> List[Tuple[str, str]]:
    """
    Check AUTHORITATIVE_INTEGRITY_MANIFEST for:
    - All listed files actually exist
    - No stale references to deleted files
    """
    issues = []
    manifest = load_json(manifest_path)
    
    files = manifest.get('files', [])
    
    for entry in files:
        file_path = entry.get('path')
        if file_path:
            exists, full_path = check_file_exists(file_path, repo_root)
            if not exists:
                issues.append(('missing_file', f"File listed in INTEGRITY_MANIFEST does not exist: {file_path}"))
    
    return issues


def check_repository_file_registry(registry_path: Path, repo_root: Path) -> List[Tuple[str, str]]:
    """
    Check REPOSITORY_FILE_REGISTRY for:
    - All live_files actually exist
    - No stale references to deleted files
    """
    issues = []
    registry = load_json(registry_path)
    
    live_files = registry.get('live_files', [])
    
    for file_ref in live_files:
        exists, full_path = check_file_exists(file_ref, repo_root)
        if not exists:
            issues.append(('missing_file', f"File listed in REPOSITORY_FILE_REGISTRY live_files does not exist: {file_ref}"))
    
    return issues


def check_category_drift(file_path: Path, content: str) -> List[Tuple[str, str]]:
    """
    Check a markdown file for category drift patterns.
    
    Returns list of (issue_type, message) tuples.
    """
    issues = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        
        # Skip code blocks and quotes for some checks
        is_code_block = line.strip().startswith('```') or line.strip().startswith('>')
        
        for pattern_name, pattern_config in CATEGORY_DRIFT_PATTERNS.items():
            risk_terms = pattern_config.get('risk_terms', [])
            allowed_contexts = pattern_config.get('allowed_contexts', [])
            
            # Check if any risk term appears
            for term in risk_terms:
                if term.lower() in line_lower:
                    # Check if allowed context is present
                    has_allowed_context = any(ctx.lower() in line_lower for ctx in allowed_contexts)
                    
                    if not has_allowed_context:
                        # Check for blocked sections (epistemic sections shouldn't have strong ontology claims)
                        blocked_sections = pattern_config.get('blocked_sections', [])
                        section_context = False
                        
                        # Look at surrounding lines for section context
                        context_start = max(0, line_num - 5)
                        context_end = min(len(lines), line_num + 2)
                        context_text = ' '.join(lines[context_start:context_end]).lower()
                        
                        for blocked in blocked_sections:
                            if blocked.lower() in context_text:
                                section_context = True
                                break
                        
                        if section_context or not is_code_block:
                            severity = pattern_config.get('severity', 'warn')
                            message = pattern_config.get('message', f'Potential category drift: {term}')
                            issues.append((
                                f'category_drift_{pattern_name}',
                                f"Line {line_num}: {message} | Content: {line[:80]}..."
                            ))
                            break  # Only report once per line per pattern
    
    return issues


def validate_framework_files_for_category_drift(repo_root: Path) -> List[Tuple[str, str]]:
    """
    Validate framework markdown files for category drift.
    
    Checks:
    - structural-phenomenology.md for ontology hardening in epistemic sections
    - informational-awareness.md for proof claims
    - unity-dynamics.md for consciousness inflation
    """
    issues = []
    
    framework_files = [
        'Research/structured-unity-framework/framework/structural-phenomenology.md',
        'Research/structured-unity-framework/framework/informational-awareness.md',
        'Research/structured-unity-framework/framework/unity-dynamics.md',
    ]
    
    for file_ref in framework_files:
        file_path = repo_root / file_ref
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                drift_issues = check_category_drift(file_path, content)
                issues.extend(drift_issues)
            except Exception as e:
                issues.append(('read_error', f"Could not read {file_ref}: {e}"))
    
    return issues


def check_version_consistency(
    surfaces_path: Path,
    integrity_path: Path,
    file_registry_path: Path
) -> List[Tuple[str, str]]:
    """
    Check that registry versions are consistent.
    After changes, all registries should have matching version numbers.
    """
    issues = []
    
    surfaces = load_json(surfaces_path)
    integrity = load_json(integrity_path)
    file_registry = load_json(file_registry_path)
    
    surfaces_version = surfaces.get('registry_version')
    integrity_version = integrity.get('version')
    file_registry_version = file_registry.get('version')
    
    versions = {
        'CURRENT_SURFACES_REGISTRY': surfaces_version,
        'AUTHORITATIVE_INTEGRITY_MANIFEST': integrity_version,
        'REPOSITORY_FILE_REGISTRY': file_registry_version
    }
    
    # Check if all versions match
    unique_versions = set(v for v in versions.values() if v is not None)
    
    if len(unique_versions) > 1:
        issues.append((
            'version_mismatch',
            f"Registry versions are inconsistent: {versions}"
        ))
    
    return issues


def _issues_to_validation_results(check_name: str, issues: List[Tuple[str, str]], repo_root: Path) -> List[ValidationResult]:
    """Convert internal issue tuples to ValidationResult objects."""
    if not issues:
        return [ValidationResult(
            check_name=f"governance-consistency-{check_name}",
            status="pass",
            message=f"Governance consistency check '{check_name}' passed.",
            path=str(repo_root / 'governance'),
        )]
    
    results = []
    for issue_type, message in issues:
        status = "warn" if issue_type in ('skip',) else "fail"
        results.append(ValidationResult(
            check_name=f"governance-consistency-{check_name}",
            status=status,
            message=message,
            path=str(repo_root / 'governance'),
            expected="no issues",
            found=f"{issue_type}: {message[:50]}..." if len(message) > 50 else f"{issue_type}: {message}",
        ))
    return results


def validate_governance_consistency(repo_root: Path) -> List[ValidationResult]:
    """
    Run all governance consistency checks.
    
    Returns list of ValidationResult objects.
    """
    all_issues: Dict[str, List[Tuple[str, str]]] = {}
    
    governance_dir = repo_root / 'governance'
    
    # Check CURRENT_SURFACES_REGISTRY (v0.1 - optional during migration)
    surfaces_path = governance_dir / 'CURRENT_SURFACES_REGISTRY_v0_1.json'
    if surfaces_path.exists():
        all_issues['current_surfaces_registry'] = check_current_surfaces_registry(surfaces_path, repo_root)
    else:
        # v0.2 migration: this is expected to be missing
        all_issues['current_surfaces_registry'] = []
    
    # Check AUTHORITATIVE_INTEGRITY_MANIFEST (v0.1 - optional during migration)
    integrity_path = governance_dir / 'AUTHORITATIVE_INTEGRITY_MANIFEST_v0_1.json'
    if integrity_path.exists():
        all_issues['integrity_manifest'] = check_integrity_manifest(integrity_path, repo_root)
    else:
        # v0.2 migration: integrity is now derived, not stored
        all_issues['integrity_manifest'] = []
    
    # Check REPOSITORY_FILE_REGISTRY (v0.1 - optional during migration)
    file_registry_path = governance_dir / 'REPOSITORY_FILE_REGISTRY_v0_1.json'
    if file_registry_path.exists():
        all_issues['file_registry'] = check_repository_file_registry(file_registry_path, repo_root)
    else:
        # v0.2 migration: replaced by REGISTRY_MANIFEST_v0_2.json
        all_issues['file_registry'] = []
    
    # Check version consistency (only if v0.1 files exist)
    v0_1_files_exist = surfaces_path.exists() and integrity_path.exists() and file_registry_path.exists()
    if v0_1_files_exist:
        all_issues['version_consistency'] = check_version_consistency(
            surfaces_path,
            integrity_path,
            file_registry_path
        )
    else:
        all_issues['version_consistency'] = []
    
    # Convert all issues to ValidationResults
    results: List[ValidationResult] = []
    for check_name, issues in all_issues.items():
        results.extend(_issues_to_validation_results(check_name, issues, repo_root))
    
    # Category drift validation
    drift_issues = validate_framework_files_for_category_drift(repo_root)
    if drift_issues:
        for issue_type, message in drift_issues:
            results.append(ValidationResult(
                check_name=f"governance-consistency-category-drift",
                status="warn" if "warn" in issue_type else "fail",
                message=message,
                path=str(repo_root / 'framework'),
                expected="no category drift",
                found=message[:100],
            ))
    else:
        results.append(ValidationResult(
            check_name="governance-consistency-category-drift",
            status="pass",
            message="No category drift detected in framework files.",
            path=str(repo_root / 'framework'),
        ))
    
    # If no v0.1 files exist, add a pass result for v0.2 migration
    if not v0_1_files_exist and not results:
        results.append(ValidationResult(
            check_name="governance-consistency-v0.2-migration",
            status="pass",
            message="v0.1 governance files not present (v0.2 migration in progress).",
            path=str(repo_root / 'governance'),
        ))
    
    return results


def format_results(results: Dict[str, List[Tuple[str, str]]]) -> str:
    """Format validation results for human reading."""
    lines = []
    
    total_issues = 0
    for check_name, issues in results.items():
        if issues:
            lines.append(f"\n{check_name}:")
            for issue_type, message in issues:
                lines.append(f"  [{issue_type}] {message}")
                total_issues += 1
    
    if total_issues == 0:
        lines.append("✓ All governance consistency checks passed.")
    else:
        lines.insert(0, f"✗ Found {total_issues} governance consistency issue(s):")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    
    # Default to repository root
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    
    results = validate_governance_consistency(repo_root)
    
    # Print results
    fail_count = sum(1 for r in results if r.status == 'fail')
    warn_count = sum(1 for r in results if r.status == 'warn')
    pass_count = sum(1 for r in results if r.status == 'pass')
    
    for r in results:
        icon = "✓" if r.status == 'pass' else ("⚠" if r.status == 'warn' else "✗")
        print(f"{icon} [{r.status.upper()}] {r.check_name}: {r.message}")
    
    print(f"\nResults: {pass_count} passed, {warn_count} warnings, {fail_count} failed")
    
    # Exit with error if any failures
    sys.exit(1 if fail_count > 0 else 0)
