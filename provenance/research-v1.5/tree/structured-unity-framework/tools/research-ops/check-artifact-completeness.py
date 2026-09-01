#!/usr/bin/env python3
"""
Check artifact completeness — verify all referenced artifacts exist.

Usage:
    python check-artifact-completeness.py --monograph-dir ../../monograph/

Scans monograph support package and evidence map for:
- Broken internal links
- Missing referenced artifacts
- Orphaned files not linked from evidence map
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple


def extract_markdown_links(text: str) -> List[str]:
    """Extract all [text](path.md) links from markdown."""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)
    return [path for _, path in matches]


def check_file_exists(base_dir: Path, referenced_path: str) -> Tuple[bool, Path]:
    """Check if a referenced file exists (handles relative paths)."""
    # Clean up path
    clean_path = referenced_path.split('#')[0]  # Remove anchors
    if clean_path.endswith('.md'):
        full_path = base_dir / clean_path
        return full_path.exists(), full_path
    return True, Path(clean_path)  # Non-md references we skip


def scan_directory_for_md_files(base_dir: Path) -> Set[Path]:
    """Get all markdown files in directory."""
    return set(base_dir.rglob('*.md'))


def check_monograph_completeness(monograph_dir: Path) -> dict:
    """Check monograph directory for completeness issues."""
    results = {
        'broken_links': [],
        'orphaned_files': [],
        'missing_artifacts': [],
        'referenced_count': 0,
        'existing_count': 0,
    }
    
    # Get all markdown files
    all_md_files = scan_directory_for_md_files(monograph_dir)
    results['existing_count'] = len(all_md_files)
    
    # Track which files are referenced
    referenced_files = set()
    
    # Check main support package for links
    support_package = monograph_dir / 'SUPPORT_PACKAGE.md'
    if support_package.exists():
        content = support_package.read_text(encoding='utf-8')
        links = extract_markdown_links(content)
        
        for link in links:
            results['referenced_count'] += 1
            exists, full_path = check_file_exists(monograph_dir.parent, link)
            
            if link.endswith('.md'):
                referenced_files.add(full_path.resolve())
                
                if not exists:
                    results['broken_links'].append({
                        'source': str(support_package),
                        'link': link,
                        'resolved': str(full_path)
                    })
    
    # Find orphaned files (existing but not referenced)
    for md_file in all_md_files:
        if md_file.resolve() not in referenced_files and md_file.name != 'SUPPORT_PACKAGE.md':
            results['orphaned_files'].append(str(md_file.relative_to(monograph_dir)))
    
    return results


def check_evidence_map_completeness(applications_dir: Path) -> dict:
    """Check evidence maps in applications for broken artifact references."""
    results = {
        'evidence_maps_found': [],
        'broken_artifact_refs': [],
    }
    
    evidence_maps = list(applications_dir.rglob('*evidence-map*.md'))
    results['evidence_maps_found'] = [str(f) for f in evidence_maps]
    
    for ev_map in evidence_maps:
        content = ev_map.read_text(encoding='utf-8')
        links = extract_markdown_links(content)
        
        for link in links:
            if not link.endswith('.md'):
                continue
                
            # Resolve relative to evidence map location
            base_dir = ev_map.parent
            full_path = base_dir / link
            
            if not full_path.exists():
                # Try relative to applications dir
                full_path = applications_dir / link
                
            if not full_path.exists():
                results['broken_artifact_refs'].append({
                    'evidence_map': str(ev_map),
                    'missing_ref': link,
                })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Check artifact completeness in monograph and evidence maps'
    )
    parser.add_argument('--monograph-dir', type=Path,
                        default=Path('../../monograph/'),
                        help='Monograph directory path')
    parser.add_argument('--applications-dir', type=Path,
                        default=Path('../../applications/'),
                        help='Applications directory path')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error if issues found')
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print("Artifact Completeness Check (v1.6 research-ops)")
    print(f"{'='*70}\n")
    
    issues_found = False
    
    # Check monograph
    print("Checking monograph/...")
    mono_results = check_monograph_completeness(args.monograph_dir)
    
    print(f"  Markdown files found: {mono_results['existing_count']}")
    print(f"  Links checked: {mono_results['referenced_count']}")
    
    if mono_results['broken_links']:
        issues_found = True
        print(f"\n  ❌ Broken links ({len(mono_results['broken_links'])}):")
        for bl in mono_results['broken_links']:
            print(f"    - {bl['link']} (from {bl['source']})")
    else:
        print("  ✅ No broken links")
    
    if mono_results['orphaned_files']:
        issues_found = True
        print(f"\n  ⚠️  Orphaned files ({len(mono_results['orphaned_files'])}):")
        for of in mono_results['orphaned_files'][:10]:  # Show first 10
            print(f"    - {of}")
        if len(mono_results['orphaned_files']) > 10:
            print(f"    ... and {len(mono_results['orphaned_files']) - 10} more")
    else:
        print("  ✅ No orphaned files")
    
    # Check evidence maps
    print(f"\nChecking applications/ evidence maps...")
    ev_results = check_evidence_map_completeness(args.applications_dir)
    
    print(f"  Evidence maps found: {len(ev_results['evidence_maps_found'])}")
    
    if ev_results['broken_artifact_refs']:
        issues_found = True
        print(f"\n  ❌ Broken artifact references ({len(ev_results['broken_artifact_refs'])}):")
        for bar in ev_results['broken_artifact_refs']:
            print(f"    - {bar['missing_ref']} (from {bar['evidence_map']})")
    else:
        print("  ✅ All artifact references valid")
    
    # Summary
    print(f"\n{'='*70}")
    if issues_found:
        print("Result: ISSUES FOUND")
        if args.strict:
            sys.exit(1)
    else:
        print("Result: ✅ ALL CHECKS PASSED")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
