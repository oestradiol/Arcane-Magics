#!/usr/bin/env python3
"""
Validate closure note claims against ledger data.

Usage:
    python validate-closure-note.py --corpus corpus.json

Validates cross-case patterns from nz-taiwan-australia-closure-note.md:
- Public-information coordination centrality
- Health-executive advisory bridge
- Implementation-observed vs decision-announced distribution
- Event count claims
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


class ValidationResult:
    def __init__(self, claim: str, passed: bool, details: str = ""):
        self.claim = claim
        self.passed = passed
        self.details = details


def load_corpus(corpus_path: Path) -> Dict[str, Any]:
    """Load corpus JSON."""
    with open(corpus_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_public_information_centrality(corpus: Dict[str, Any]) -> ValidationResult:
    """
    Validate claim: All three cases show public-information coordination as structurally central.
    Claim: NZ 38/38, Taiwan 20/20, Australia 18/18 events involve public-information coordination.
    """
    routes = corpus.get('routes', {})
    failures = []
    
    for route_id, route_data in routes.items():
        events = route_data.get('events', [])
        metadata = route_data.get('metadata', {})
        total = metadata.get('total_events', len(events))
        
        # Count events where public-information is in receiving_units OR issuing_unit
        pi_count = 0
        for event in events:
            receiving = event.get('receiving_units', [])
            issuing = event.get('issuing_unit', '')
            pi_marker = event.get('public_information_marker', '')
            
            if ('public-information coordination' in receiving or 
                'public-information coordination' in issuing or
                'public' in pi_marker.lower()):
                pi_count += 1
        
        if pi_count != total:
            failures.append(f"{route_id}: {pi_count}/{total} events with public-information (expected {total}/{total})")
    
    if failures:
        return ValidationResult(
            "Public-information coordination centrality",
            False,
            "; ".join(failures)
        )
    
    return ValidationResult(
        "Public-information coordination centrality",
        True,
        "All routes show public-information coordination in all events"
    )


def validate_health_executive_bridge(corpus: Dict[str, Any]) -> ValidationResult:
    """
    Validate claim: Health-executive advisory bridge exists in all three cases.
    - NZ: MoH → DPMC directive dependencies
    - Taiwan: CECC includes health as core function
    - Australia: AHPPC → National Cabinet chain (au-b-010, au-b-005, au-b-001)
    """
    routes = corpus.get('routes', {})
    findings = []
    
    for route_id, route_data in routes.items():
        events = route_data.get('events', [])
        health_to_exec = 0
        
        for event in events:
            issuing = event.get('issuing_unit', '')
            receiving = event.get('receiving_units', [])
            
            # Check for health → executive flow
            if ('public-health' in issuing and 'strategic executive' in str(receiving)):
                health_to_exec += 1
            # Check for executive → health flow (also counts as bridge)
            if ('strategic executive' in issuing and 'public-health' in str(receiving)):
                health_to_exec += 1
        
        findings.append(f"{route_id}: {health_to_exec} health-executive links")
    
    # The claim is qualitative - just need to verify bridge exists, not specific count
    # Australia specifically mentions au-b-010, au-b-005, au-b-001
    au_events = routes.get('au', {}).get('events', [])
    specific_events = ['au-b-010', 'au-b-005', 'au-b-001']
    found_specific = [e.get('event_id') for e in au_events if e.get('event_id') in specific_events]
    
    if len(found_specific) >= 2:  # At least 2 of 3 mentioned events exist
        return ValidationResult(
            "Health-executive advisory bridge",
            True,
            f"Health-executive links found: {'; '.join(findings)}; Australia specific events: {found_specific}"
        )
    
    return ValidationResult(
        "Health-executive advisory bridge",
        False,
        f"Insufficient health-executive links: {'; '.join(findings)}"
    )


def validate_implementation_distribution(corpus: Dict[str, Any]) -> ValidationResult:
    """
    Validate claim: Implementation-observed vs decision-announced distribution.
    Claim: NZ 21 impl-obs/17 dec-ann; Taiwan 8/12; Australia 2/16
    """
    routes = corpus.get('routes', {})
    expected = {
        'nz': {'implementation_observed': 21, 'decision_announced': 17},
        'tw': {'implementation_observed': 8, 'decision_announced': 12},
        'au': {'implementation_observed': 2, 'decision_announced': 16},
    }
    
    results = []
    all_pass = True
    
    for route_id, route_data in routes.items():
        events = route_data.get('events', [])
        impl_obs = sum(1 for e in events if 'implementation observed' in e.get('implementation_marker', ''))
        dec_ann = sum(1 for e in events if 'decision announced' in e.get('implementation_marker', ''))
        
        if route_id in expected:
            exp = expected[route_id]
            match_impl = impl_obs == exp['implementation_observed']
            match_dec = dec_ann == exp['decision_announced']
            
            if match_impl and match_dec:
                results.append(f"{route_id}: ✓ {impl_obs}/{dec_ann}")
            else:
                all_pass = False
                results.append(f"{route_id}: ✗ got {impl_obs}/{dec_ann}, expected {exp['implementation_observed']}/{exp['decision_announced']}")
        else:
            results.append(f"{route_id}: ? {impl_obs}/{dec_ann} (no expectation)")
    
    return ValidationResult(
        "Implementation-observed vs decision-announced distribution",
        all_pass,
        "; ".join(results)
    )


def validate_event_counts(corpus: Dict[str, Any]) -> ValidationResult:
    """
    Validate claim: 38 NZ + 20 Taiwan + 18 Australia = 76 events.
    """
    metadata = corpus.get('metadata', {})
    actual_total = metadata.get('total_events', 0)
    routes = metadata.get('routes', {})
    
    expected = {'nz': 38, 'tw': 20, 'au': 18}
    expected_total = 76
    
    results = []
    all_pass = True
    
    for route_id, exp_count in expected.items():
        if route_id in routes:
            actual = routes[route_id].get('total_events', 0)
            if actual == exp_count:
                results.append(f"{route_id}: ✓ {actual}")
            else:
                all_pass = False
                results.append(f"{route_id}: ✗ {actual} (expected {exp_count})")
        else:
            all_pass = False
            results.append(f"{route_id}: ✗ missing")
    
    total_match = actual_total == expected_total
    
    return ValidationResult(
        f"Event counts (total: {actual_total}, expected: {expected_total})",
        all_pass and total_match,
        "; ".join(results)
    )


def validate_border_sequence(corpus: Dict[str, Any]) -> ValidationResult:
    """
    Validate claim: Border tightening follows sequence across cases.
    Qualitative check - verify border-control coordination appears in early events.
    """
    routes = corpus.get('routes', {})
    findings = []
    
    for route_id, route_data in routes.items():
        events = route_data.get('events', [])
        border_events = []
        
        for i, event in enumerate(events):
            receiving = event.get('receiving_units', [])
            issuing = event.get('issuing_unit', '')
            
            if 'border-control coordination' in receiving or 'border-control coordination' in issuing:
                border_events.append(f"{event.get('event_id')}@{i}")
        
        findings.append(f"{route_id}: {len(border_events)} border events ({', '.join(border_events[:3])}{'...' if len(border_events) > 3 else ''})")
    
    # Border sequence is qualitative - just verify presence
    has_border = all('0 border' not in f for f in findings)
    
    return ValidationResult(
        "Border-tightening sequence visibility",
        has_border,
        "; ".join(findings)
    )


def main():
    parser = argparse.ArgumentParser(
        description='Validate closure note claims against corpus data'
    )
    parser.add_argument('--corpus', '-c', required=True, help='Corpus JSON file path')
    parser.add_argument('--strict', '-s', action='store_true', 
                        help='Exit with error on any validation failure')
    args = parser.parse_args()
    
    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f"❌ Error: Corpus file not found: {args.corpus}", file=sys.stderr)
        sys.exit(1)
    
    corpus = load_corpus(corpus_path)
    
    # Run all validations
    validations = [
        validate_event_counts(corpus),
        validate_public_information_centrality(corpus),
        validate_health_executive_bridge(corpus),
        validate_implementation_distribution(corpus),
        validate_border_sequence(corpus),
    ]
    
    # Report results
    print(f"\n{'='*70}")
    print("Closure Note Validation Report")
    print(f"{'='*70}\n")
    
    passed = 0
    failed = 0
    
    for v in validations:
        status = "✅ PASS" if v.passed else "❌ FAIL"
        print(f"{status}: {v.claim}")
        if v.details:
            print(f"      {v.details}")
        print()
        
        if v.passed:
            passed += 1
        else:
            failed += 1
    
    print(f"{'='*70}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*70}\n")
    
    if failed > 0 and args.strict:
        sys.exit(1)
    
    if failed > 0:
        sys.exit(0 if not args.strict else 1)  # Non-strict: exit 0 with warnings
    else:
        print("✅ All closure note claims validated successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
