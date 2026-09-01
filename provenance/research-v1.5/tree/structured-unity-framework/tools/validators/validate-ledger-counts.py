#!/usr/bin/env python3
"""
Validate that ledger event counts match public claims.

Usage:
    python validate-ledger-counts.py --ledger-json <ledger.json> --expected <count>
"""

import argparse
import json
import sys
from pathlib import Path


def validate_counts(ledger_path: str, expected_count: int) -> bool:
    """Validate event count in ledger JSON."""
    ledger_file = Path(ledger_path)
    
    if not ledger_file.exists():
        print(f"❌ FAIL: Ledger file not found: {ledger_path}")
        return False
    
    with open(ledger_file, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
    
    actual_count = len(ledger.get('events', []))
    metadata_count = ledger.get('metadata', {}).get('total_events', 0)
    
    print(f"Validating: {ledger_path}")
    print(f"  Expected: {expected_count}")
    print(f"  Actual (events array): {actual_count}")
    print(f"  Metadata claim: {metadata_count}")
    
    if actual_count != expected_count:
        print(f"❌ FAIL: Event count mismatch")
        return False
    
    if metadata_count != expected_count:
        print(f"❌ FAIL: Metadata claim mismatch")
        return False
    
    print(f"✅ PASS: Counts match")
    return True


def main():
    parser = argparse.ArgumentParser(description='Validate ledger event counts')
    parser.add_argument('--ledger-json', '-l', required=True, help='Ledger JSON file')
    parser.add_argument('--expected', '-e', type=int, required=True, help='Expected event count')
    parser.add_argument('--case', '-c', required=True, help='Case name (NZ, Taiwan, Australia)')
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Ledger Count Validation: {args.case}")
    print(f"{'='*60}")
    
    passed = validate_counts(args.ledger_json, args.expected)
    
    if passed:
        print(f"\n✅ {args.case}: VALID")
        sys.exit(0)
    else:
        print(f"\n❌ {args.case}: INVALID")
        sys.exit(1)


if __name__ == '__main__':
    main()
