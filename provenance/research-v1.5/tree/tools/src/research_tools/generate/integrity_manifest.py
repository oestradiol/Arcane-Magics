"""Generate AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2 from GOVERNANCE_CORE + REGISTRY_MANIFEST.

Per v0.2 design: integrity is derived at validation time, not stored statically.
This command generates the derived manifest for human inspection and auditing.
"""

from pathlib import Path
from typing import Dict, List, Set
import json
import hashlib


def load_json(path: Path) -> Dict:
    """Load JSON file safely."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def collect_current_surfaces(gov: Dict) -> Set[str]:
    """Collect all current surface paths from GOVERNANCE_CORE.
    
    Resolves subsystem surfaces relative to scope_prefixes.
    Filters out paths outside the Research/ repo."""
    paths = set()
    current = gov.get('current_surfaces', {})
    
    # Root surfaces - already full paths
    paths.update(current.get('root_entrypoints', []))
    paths.update(current.get('root_governance', []))
    paths.update(current.get('package_entrypoints', {}).values())
    if current.get('assisted_use'):
        paths.add(current['assisted_use'])
    
    # Subsystem surfaces - resolve relative to scope_prefixes
    for subsys_id, subsys in gov.get('subsystems', {}).items():
        # Get primary scope prefix for resolution
        prefixes = subsys.get('scope_prefixes', [])
        primary_prefix = prefixes[0] if prefixes else ''
        
        # Skip paths outside Research/ repo
        if primary_prefix.startswith('..'):
            continue
        
        # Helper to resolve surface path
        def resolve(path: str) -> str:
            if not path:
                return None
            # Already has prefix
            if any(path.startswith(p.replace('../', '')) for p in prefixes):
                return path
            # Needs prefix
            if primary_prefix and not primary_prefix.startswith('..'):
                return f"{primary_prefix}{path}"
            return path
        
        if subsys.get('entry'):
            resolved = resolve(subsys['entry'])
            if resolved:
                paths.add(resolved)
        if subsys.get('state_surface'):
            resolved = resolve(subsys['state_surface'])
            if resolved:
                paths.add(resolved)
        if subsys.get('validation_policy'):
            resolved = resolve(subsys['validation_policy'])
            if resolved:
                paths.add(resolved)
        if subsys.get('surfaces'):
            for surface in subsys['surfaces']:
                resolved = resolve(surface)
                if resolved:
                    paths.add(resolved)
    
    return paths


def generate_integrity_manifest_v2(
    repo_root: Path,
    governance_core_path: Path = None,
    registry_manifest_path: Path = None,
    output_path: Path = None
) -> Dict:
    """
    Generate v0.2 integrity manifest from GOVERNANCE_CORE + REGISTRY_MANIFEST.
    
    Per v0.2 design: integrity is computed, not stored statically.
    
    Args:
        repo_root: Repository root directory
        governance_core_path: Path to GOVERNANCE_CORE_v0_2.json
        registry_manifest_path: Path to REGISTRY_MANIFEST_v0_2.json
        output_path: Path to write manifest
    
    Returns:
        Generated manifest dictionary
    """
    if governance_core_path is None:
        governance_core_path = repo_root / 'governance' / 'GOVERNANCE_CORE_v0_2.json'
    
    if registry_manifest_path is None:
        registry_manifest_path = repo_root / 'governance' / 'REGISTRY_MANIFEST_v0_2.json'
    
    if output_path is None:
        output_path = repo_root / 'governance' / 'AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json'
    
    # Load source files
    gov = load_json(governance_core_path)
    reg = load_json(registry_manifest_path)
    
    # Collect current surfaces from governance
    current_surfaces = collect_current_surfaces(gov)
    
    if not current_surfaces:
        raise ValueError("No current surfaces found in GOVERNANCE_CORE")
    
    # Generate entries — always hash on disk (per v0.2 design: integrity is
    # computed, not stored statically; registry-cached hashes drift when
    # surface files are edited without a registry regeneration).
    files_with_hashes = []
    missing_files = []
    
    for file_ref in sorted(current_surfaces):
        full_path = repo_root / file_ref
        if full_path.exists():
            sha256 = compute_sha256(full_path)
            files_with_hashes.append({
                'path': file_ref,
                'sha256': sha256,
                'status': 'current'
            })
        else:
            missing_files.append(file_ref)
            files_with_hashes.append({
                'path': file_ref,
                'sha256': '[file-not-found]',
                'status': 'missing'
            })
    
    # Build manifest
    manifest = {
        'version': '0.2.0',
        'algorithm': 'sha256',
        'source': 'Derived from GOVERNANCE_CORE_v0_2 + REGISTRY_MANIFEST_v0_2',
        'file_count': len(current_surfaces),
        'files': files_with_hashes,
        '_meta': {
            'derived_at': '[auto-generated]',
            'missing_files': missing_files if missing_files else []
        }
    }
    
    # Write manifest
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    
    return manifest


if __name__ == '__main__':
    import sys
    
    # Default to repository root
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    
    try:
        manifest = generate_integrity_manifest_v2(repo_root)
        print(f"✓ Generated v0.2 integrity manifest with {manifest['file_count']} current surfaces")
        print(f"  Output: governance/AUTHORITATIVE_INTEGRITY_MANIFEST_v0_2.json")
        if manifest['_meta']['missing_files']:
            print(f"  ⚠ Warning: {len(manifest['_meta']['missing_files'])} files missing")
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
