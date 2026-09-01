"""
Generate REPOSITORY_FILE_REGISTRY from directory scan.

This command automates file inventory generation,
eliminating manual synchronization errors.
"""

from pathlib import Path
from typing import Dict, List, Set
import json
import hashlib


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def scan_directory(
    directory: Path,
    gitignore_patterns: List[str] = None
) -> List[Dict]:
    """
    Scan directory for files, respecting gitignore patterns.
    
    Args:
        directory: Root directory to scan
        gitignore_patterns: List of glob patterns to ignore
    
    Returns:
        List of file metadata dictionaries
    """
    if gitignore_patterns is None:
        gitignore_patterns = [
            '.git/*',
            '.gitignore',
            '__pycache__/*',
            '*.pyc',
            '*.pyo',
            '.DS_Store',
            'node_modules/*',
            'out/*',  # Generated reports
        ]
    
    files = []
    
    for file_path in directory.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Check against gitignore patterns
        relative_path = file_path.relative_to(directory)
        path_str = str(relative_path).replace('\\', '/')
        
        skip = False
        for pattern in gitignore_patterns:
            # Simple glob matching
            if pattern.endswith('/*'):
                prefix = pattern[:-2]
                if path_str.startswith(prefix + '/') or path_str == prefix:
                    skip = True
                    break
            elif pattern.startswith('*.'):
                suffix = pattern[1:]
                if path_str.endswith(suffix):
                    skip = True
                    break
            elif pattern == path_str:
                skip = True
                break
        
        if skip:
            continue
        
        # Get file metadata
        stat = file_path.stat()
        sha256 = compute_sha256(file_path)
        
        files.append({
            'path': path_str,
            'sha256': sha256,
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime
        })
    
    # Sort by path for consistent output
    files.sort(key=lambda x: x['path'])
    
    return files


def generate_file_registry(
    repo_root: Path,
    output_path: Path = None,
    scan_dirs: List[str] = None
) -> Dict:
    """
    Generate file registry from directory scan.
    
    Args:
        repo_root: Repository root directory
        output_path: Path to write registry (default: governance/REPOSITORY_FILE_REGISTRY_v0_1.json)
        scan_dirs: List of directories to scan relative to repo_root (default: ['.'])
    
    Returns:
        Generated registry dictionary
    """
    if output_path is None:
        output_path = repo_root / 'governance' / 'REPOSITORY_FILE_REGISTRY_v0_1.json'
    
    if scan_dirs is None:
        scan_dirs = ['.']
    
    all_files = []
    
    for scan_dir in scan_dirs:
        full_scan_path = repo_root / scan_dir
        if not full_scan_path.exists():
            print(f"Warning: Scan directory does not exist: {full_scan_path}")
            continue
        
        files = scan_directory(full_scan_path)
        all_files.extend(files)
    
    # Load existing registry to preserve version
    if output_path.exists():
        with open(output_path, 'r') as f:
            existing = json.load(f)
        version = existing.get('version', '0.1.0')
        # Increment minor version
        parts = version.split('.')
        if len(parts) >= 2:
            parts[1] = str(int(parts[1]) + 1)
            version = '.'.join(parts)
    else:
        version = '0.1.0'
    
    # Build registry
    registry = {
        'version': version,
        'algorithm': 'sha256',
        'generated_from': scan_dirs,
        'file_count': len(all_files),
        'files': all_files
    }
    
    # Write registry
    with open(output_path, 'w') as f:
        json.dump(registry, f, indent=2)
        f.write('\n')
    
    return registry


if __name__ == '__main__':
    import sys
    
    # Default to repository root
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    
    try:
        registry = generate_file_registry(repo_root)
        print(f"✓ Generated file registry with {registry['file_count']} files")
        print(f"  Version: {registry['version']}")
        print(f"  Output: governance/REPOSITORY_FILE_REGISTRY_v0_1.json")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
