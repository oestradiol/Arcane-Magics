#!/usr/bin/env python3
"""
Check backlog hygiene — detect stale entries, drift, and maintenance needs.

Usage:
    python check-backlog-hygiene.py

Scans pending-inventory.md and project-status.md for:
- Stale deferred items (older than threshold)
- Items marked complete but still in pending
- Surface freshness issues
- Version drift between files
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def extract_pending_items(text: str) -> List[Dict]:
    """Extract pending/deferred items from pending-inventory.md format."""
    items = []
    
    # Pattern: Q[branch]{status:detail}
    pattern = r'Q\[([^\]]+)\]\{([^}]+)\}'
    matches = re.findall(pattern, text)
    
    for branch, status_detail in matches:
        items.append({
            'id': branch,
            'raw_status': status_detail,
            'type': 'deferred'
        })
    
    # Pattern: A[branch]{archived:date|reopen-requires:condition}
    archived_pattern = r'A\[([^\]]+)\]\{archived:([^|]+)\|([^}]+)\}'
    archived_matches = re.findall(archived_pattern, text)
    
    for branch, date, condition in archived_matches:
        items.append({
            'id': branch,
            'archived_date': date,
            'reopen_condition': condition,
            'type': 'archived'
        })
    
    return items


def check_stale_archived(items: List[Dict], threshold_days: int = 90) -> List[Dict]:
    """Check for archived items that might need review."""
    stale = []
    
    for item in items:
        if item.get('type') == 'archived' and 'archived_date' in item:
            try:
                # Parse date like "2026-04-17"
                archived = datetime.strptime(item['archived_date'], '%Y-%m-%d')
                days_ago = (datetime.now() - archived).days
                
                if days_ago > threshold_days:
                    stale.append({
                        **item,
                        'days_ago': days_ago
                    })
            except ValueError:
                pass  # Unparseable date
    
    return stale


def check_status_consistency(pending_text: str, status_text: str) -> List[str]:
    """Check for inconsistencies between pending-inventory and project-status."""
    issues = []
    
    # Extract event counts from both files
    pending_events = re.findall(r'(\d+)-event', pending_text)
    status_events = re.findall(r'(\d+)-event', status_text)
    
    # Simple check: if counts differ significantly, flag it
    if pending_events and status_events:
        pending_max = max(int(x) for x in pending_events)
        status_max = max(int(x) for x in status_events)
        
        if abs(pending_max - status_max) > 5:
            issues.append(f"Event count mismatch: pending shows ~{pending_max}, status shows ~{status_max}")
    
    # Check for completed items still marked pending
    completed_in_status = re.findall(r'`([^`]+)`.*?✓\s*COMPLETE', status_text)
    pending_items = re.findall(r'Q\[([^\]]+)\]', pending_text)
    
    for item in completed_in_status:
        if any(p in item.lower() for p in pending_items):
            issues.append(f"Possible stale pending item: {item} marked complete but in pending queue")
    
    return issues


def check_surface_freshness(files: List[Path]) -> List[Dict]:
    """Check YAML frontmatter last_synced dates for surface freshness."""
    stale_surfaces = []
    
    for f in files:
        if not f.exists():
            continue
            
        text = f.read_text(encoding='utf-8')
        
        # Extract last_synced from YAML frontmatter
        match = re.search(r'^---\s*\n.*?last_synced:\s*"([^"]+)".*?---', text, re.DOTALL)
        if match:
            try:
                synced = datetime.strptime(match.group(1), '%Y-%m-%d')
                days_ago = (datetime.now() - synced).days
                
                if days_ago > 30:  # Consider >30 days stale
                    stale_surfaces.append({
                        'file': str(f),
                        'last_synced': match.group(1),
                        'days_ago': days_ago
                    })
            except ValueError:
                pass
    
    return stale_surfaces


def main():
    parser = argparse.ArgumentParser(
        description='Check backlog hygiene and surface freshness'
    )
    parser.add_argument('--docs-dir', type=Path, default=Path('../../docs/'),
                        help='Docs directory')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error if issues found')
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print("Backlog Hygiene Check (v1.6 research-ops)")
    print(f"{'='*70}\n")
    
    issues_found = False
    
    # Load key files
    pending_file = args.docs_dir / 'pending-inventory.md'
    status_file = args.docs_dir / 'project-status.md'
    
    if pending_file.exists() and status_file.exists():
        pending_text = pending_file.read_text(encoding='utf-8')
        status_text = status_file.read_text(encoding='utf-8')
        
        # Check pending items
        items = extract_pending_items(pending_text)
        print(f"Pending/deferred items found: {len(items)}")
        
        # Check stale archived
        stale = check_stale_archived(items, threshold_days=90)
        if stale:
            issues_found = True
            print(f"\n⚠️  Archived items needing review ({len(stale)}):")
            for s in stale:
                print(f"  - {s['id']}: archived {s['days_ago']} days ago")
        else:
            print("  ✅ No stale archived items")
        
        # Check consistency
        inconsistencies = check_status_consistency(pending_text, status_text)
        if inconsistencies:
            issues_found = True
            print(f"\n❌ Status inconsistencies ({len(inconsistencies)}):")
            for inc in inconsistencies:
                print(f"  - {inc}")
        else:
            print("  ✅ Status files consistent")
    else:
        print("⚠️  Could not load pending-inventory.md or project-status.md")
    
    # Check surface freshness
    print(f"\nChecking surface freshness...")
    freshness_files = [
        args.docs_dir / 'current-execution-order.md',
        args.docs_dir / 'project-status.md',
    ]
    stale_surfaces = check_surface_freshness(freshness_files)
    
    if stale_surfaces:
        issues_found = True
        print(f"  ⚠️  Stale surfaces ({len(stale_surfaces)}):")
        for ss in stale_surfaces:
            print(f"    - {Path(ss['file']).name}: {ss['days_ago']} days since sync")
    else:
        print("  ✅ All surfaces fresh (<30 days)")
    
    # Summary
    print(f"\n{'='*70}")
    if issues_found:
        print("Result: ISSUES FOUND - review recommended")
        if args.strict:
            sys.exit(1)
    else:
        print("Result: ✅ ALL CHECKS PASSED")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
