#!/usr/bin/env python3
"""
Unified validation runner for SUF v1.5 tooling.

Runs all validators and reports aggregated results.

Usage:
    python validate-all.py
    python validate-all.py --strict  # Exit with error on any failure
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Tool paths (relative to tools/ directory)
EXPORTS_DIR = Path('exports')
VALIDATORS_DIR = Path('validators')


def run_command(cmd: list, description: str) -> tuple:
    """Run a command and return (success, output)."""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return (result.returncode == 0, result.stdout + result.stderr)
    except Exception as e:
        print(f"❌ Error running {description}: {e}", file=sys.stderr)
        return (False, str(e))


def main():
    parser = argparse.ArgumentParser(
        description='Run all SUF validation checks'
    )
    parser.add_argument('--strict', '-s', action='store_true',
                        help='Exit with error code if any validation fails')
    parser.add_argument('--skip-ledger-export', action='store_true',
                        help='Skip corpus export (use existing corpus.json)')
    args = parser.parse_args()
    
    tools_dir = Path(__file__).parent
    python_exe = '/home/player/Data/Documents/Obsidian/SUF/Research/tools/.venv/bin/python'
    
    results = []
    
    # Step 1: Export corpus if needed
    if not args.skip_ledger_export:
        success, output = run_command(
            [python_exe, str(EXPORTS_DIR / 'ledger-to-json.py'),
             '--corpus', '--output', str(EXPORTS_DIR / 'corpus.json')],
            "Export 76-event corpus to JSON"
        )
        results.append(('Corpus Export', success))
        if not success and args.strict:
            sys.exit(1)
    
    # Step 2: Export CSV
    success, output = run_command(
        [python_exe, str(EXPORTS_DIR / 'ledger-to-json.py'),
         '--corpus', '--format', 'csv', '--output', str(EXPORTS_DIR / 'corpus.csv')],
        "Export corpus to CSV"
    )
    results.append(('CSV Export', success))
    
    # Step 3: Validate ledger counts
    success, output = run_command(
        [python_exe, str(VALIDATORS_DIR / 'validate-ledger-counts.py'),
         '--ledger-json', str(EXPORTS_DIR / 'corpus.json'),
         '--expected', '71',  # Actual detailed events (38+20+13)
         '--case', 'Three-Case Corpus'],
        "Validate ledger event counts"
    )
    results.append(('Ledger Counts', success))
    
    # Step 4: Validate closure note claims
    success, output = run_command(
        [python_exe, str(VALIDATORS_DIR / 'validate-closure-note.py'),
         '--corpus', str(EXPORTS_DIR / 'corpus.json')],
        "Validate closure note cross-case claims"
    )
    results.append(('Closure Note Claims', success))
    
    # Summary report
    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    passed = sum(1 for _, success in results if success)
    failed = sum(1 for _, success in results if not success)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} checks")
    print(f"{'='*70}")
    
    if failed > 0:
        print("\n⚠️  Some validations failed. Review output above for details.")
        print("   Use --strict to exit with error code on failures.")
        if args.strict:
            sys.exit(1)
    else:
        print("\n✅ All validations passed!")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
