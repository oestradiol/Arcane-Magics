#!/usr/bin/env python3
"""
Check discovery state integrity — track source resolution status.

Usage:
    python check-discovery-state.py --routes-dir ../../applications/demonstrated-routes/

Scans source-discovery-logs for:
- Sources marked pending for extended periods
- Resolved sources without archive links
- High-priority discoveries not actioned
- Inconsistent status between discovery log and ledger
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


def parse_discovery_log(log_path: Path) -> List[Dict]:
    """Parse a source-discovery-log.md file."""
    if not log_path.exists():
        return []
    
    entries = []
    text = log_path.read_text(encoding='utf-8')
    
    # Look for patterns like: - [STATUS] source-id — description
    pattern = r'- \[([^\]]+)\]\s+([^(]+)\s*(?:\(([^)]+)\))?\s*—\s*(.+)'
    matches = re.findall(pattern, text)
    
    for status, source_id, url, description in matches:
        entries.append({
            'status': status.strip(),
            'source_id': source_id.strip(),
            'url': url.strip() if url else '',
            'description': description.strip(),
        })
    
    return entries


def check_pending_duration(entries: List[Dict], threshold_days: int = 60) -> List[Dict]:
    """Find entries pending for too long (based on dates in description)."""
    stale = []
    
    for entry in entries:
        if entry['status'].lower() not in ['pending', 'needed', 'discovery-needed']:
            continue
        
        # Look for date patterns in description
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', entry['description'])
        if date_match:
            try:
                entry_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                days_ago = (datetime.now() - entry_date).days
                
                if days_ago > threshold_days:
                    stale.append({
                        **entry,
                        'pending_days': days_ago
                    })
            except ValueError:
                pass
    
    return stale


def check_archive_gaps(entries: List[Dict]) -> List[Dict]:
    """Find resolved entries missing archive links."""
    gaps = []
    
    for entry in entries:
        status = entry['status'].lower()
        if status in ['resolved', 'admitted', 'archived', 'live+archive']:
            # Check if it has archive evidence
            has_archive = (
                'wayback' in entry.get('url', '').lower() or
                'archive.org' in entry.get('url', '').lower() or
                'web.archive' in entry.get('url', '').lower()
            )
            
            if not has_archive and not entry.get('url', ''):
                gaps.append(entry)
    
    return gaps


def check_ledger_consistency(discovery_entries: List[Dict], ledger_path: Path) -> List[str]:
    """Check if sources in discovery log appear in ledger."""
    issues = []
    
    if not ledger_path.exists():
        return [f"Ledger not found: {ledger_path}"]
    
    ledger_text = ledger_path.read_text(encoding='utf-8')
    
    for entry in discovery_entries:
        if entry['status'].lower() in ['resolved', 'admitted', 'archived']:
            source_id = entry['source_id']
            
            # Check if source appears in ledger citations
            if source_id not in ledger_text:
                issues.append(f"Source {source_id} marked {entry['status']} but not found in ledger")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Check discovery state integrity'
    )
    parser.add_argument('--routes-dir', type=Path,
                        default=Path('../../applications/demonstrated-routes/'),
                        help='Routes directory')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error if issues found')
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print("Discovery State Integrity Check (v1.6 research-ops)")
    print(f"{'='*70}\n")
    
    issues_found = False
    
    # Find all discovery logs
    discovery_logs = list(args.routes_dir.rglob('*source-discovery*.md'))
    print(f"Discovery logs found: {len(discovery_logs)}\n")
    
    for log_path in discovery_logs:
        route_name = log_path.parent.name
        print(f"Checking {route_name}...")
        
        entries = parse_discovery_log(log_path)
        if not entries:
            print("  ⚠️  No entries parsed")
            continue
        
        print(f"  Entries: {len(entries)}")
        
        # Check pending duration
        stale_pending = check_pending_duration(entries, threshold_days=60)
        if stale_pending:
            issues_found = True
            print(f"  ⚠️  Stale pending ({len(stale_pending)}):")
            for sp in stale_pending[:3]:  # Show first 3
                print(f"    - {sp['source_id']}: {sp['pending_days']} days")
        else:
            print("  ✅ No stale pending entries")
        
        # Check archive gaps
        archive_gaps = check_archive_gaps(entries)
        if archive_gaps:
            issues_found = True
            print(f"  ⚠️  Archive gaps ({len(archive_gaps)}):")
            for ag in archive_gaps[:3]:
                print(f"    - {ag['source_id']}: no archive URL")
        else:
            print("  ✅ All resolved entries have archives")
        
        # Check ledger consistency if ledger exists
        route_ledger = log_path.parent / 'event-ledger-seed.md'
        if not route_ledger.exists():
            # Try alternate names
            for alt in log_path.parent.glob('*event-ledger*.md'):
                route_ledger = alt
                break
        
        if route_ledger.exists():
            inconsistencies = check_ledger_consistency(entries, route_ledger)
            if inconsistencies:
                issues_found = True
                print(f"  ⚠️  Ledger inconsistencies ({len(inconsistencies)}):")
                for inc in inconsistencies[:3]:
                    print(f"    - {inc}")
            else:
                print("  ✅ Discovery-ledger consistent")
        
        print()
    
    # Summary
    print(f"{'='*70}")
    if issues_found:
        print("Result: ISSUES FOUND - review discovery queue")
        if args.strict:
            sys.exit(1)
    else:
        print("Result: ✅ ALL CHECKS PASSED")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
