#!/usr/bin/env python3
"""
Generate cross-case comparison matrix from ledger JSON files.

Usage:
    python generate-comparison-matrix.py --ledgers <nz.json> <taiwan.json> <australia.json> --output <matrix.md>
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any


def load_ledgers(ledger_paths: List[str]) -> Dict[str, Any]:
    """Load multiple ledger JSON files."""
    ledgers = {}
    
    for path_str in ledger_paths:
        path = Path(path_str)
        case_name = path.stem.replace('-ledger', '')
        
        with open(path, 'r', encoding='utf-8') as f:
            ledgers[case_name] = json.load(f)
    
    return ledgers


def generate_metrics(ledgers: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate comparative metrics across cases."""
    metrics = {}
    
    for case_name, ledger in ledgers.items():
        events = ledger.get('events', [])
        
        # Count metrics
        total = len(events)
        
        # Implementation markers
        impl_initiated = sum(1 for e in events if e.get('implementation_marker') == 'implementation initiated')
        impl_observed = sum(1 for e in events if e.get('implementation_marker') == 'implementation observed')
        impl_clarified = sum(1 for e in events if e.get('implementation_marker') == 'implementation clarified')
        decision_announced = sum(1 for e in events if e.get('implementation_marker') == 'decision announced')
        
        # Public information markers
        major_briefing = sum(1 for e in events if e.get('public_information_marker') == 'major public briefing')
        guidance_update = sum(1 for e in events if e.get('public_information_marker') == 'official guidance update')
        
        # Issuing units
        issuing_units = {}
        for e in events:
            unit = e.get('issuing_unit', 'unknown')
            issuing_units[unit] = issuing_units.get(unit, 0) + 1
        
        # Scale tags
        sigma1 = sum(1 for e in events if 'sigma1' in e.get('scale_tag', []))
        sigma2 = sum(1 for e in events if 'sigma2' in e.get('scale_tag', []))
        sigma3 = sum(1 for e in events if 'sigma3' in e.get('scale_tag', []))
        
        # Confidence
        high_conf = sum(1 for e in events if e.get('confidence_note') == 'high')
        
        metrics[case_name] = {
            'total_events': total,
            'implementation_initiated': impl_initiated,
            'implementation_observed': impl_observed,
            'implementation_clarified': impl_clarified,
            'decision_announced': decision_announced,
            'major_public_briefing': major_briefing,
            'official_guidance_update': guidance_update,
            'issuing_units': issuing_units,
            'sigma1_events': sigma1,
            'sigma2_events': sigma2,
            'sigma3_events': sigma3,
            'high_confidence': high_conf,
        }
    
    return metrics


def generate_markdown_table(metrics: Dict[str, Dict[str, Any]]) -> str:
    """Generate markdown comparison table."""
    cases = list(metrics.keys())
    
    lines = [
        "# Three-Case Comparison Matrix",
        "",
        "Generated from canonical ledger exports.",
        "",
        "## Overview",
        "",
        "| Metric | " + " | ".join(cases) + " |",
        "|" + "---|" * (len(cases) + 1),
    ]
    
    # Total events
    row = "| Total events | " + " | ".join(str(metrics[c]['total_events']) for c in cases) + " |"
    lines.append(row)
    
    # Implementation breakdown
    lines.append("| **Implementation** |" + " |" * len(cases))
    
    for metric in ['decision_announced', 'implementation_initiated', 'implementation_observed', 'implementation_clarified']:
        label = metric.replace('_', ' ').title()
        row = f"| {label} | " + " | ".join(str(metrics[c][metric]) for c in cases) + " |"
        lines.append(row)
    
    # Public information
    lines.append("| **Public Information** |" + " |" * len(cases))
    
    for metric in ['major_public_briefing', 'official_guidance_update']:
        label = metric.replace('_', ' ').title()
        row = f"| {label} | " + " | ".join(str(metrics[c][metric]) for c in cases) + " |"
        lines.append(row)
    
    # Scale coverage
    lines.append("| **Scale Coverage** |" + " |" * len(cases))
    
    for metric in ['sigma1_events', 'sigma2_events', 'sigma3_events']:
        label = metric.replace('_', ' ').replace('events', 'Events')
        row = f"| {label} | " + " | ".join(str(metrics[c][metric]) for c in cases) + " |"
        lines.append(row)
    
    # Confidence
    lines.append("| **Confidence** |" + " |" * len(cases))
    row = "| High confidence | " + " | ".join(str(metrics[c]['high_confidence']) for c in cases) + " |"
    lines.append(row)
    
    # Issuing units breakdown
    lines.extend([
        "",
        "## Issuing Units by Case",
        "",
    ])
    
    for case in cases:
        lines.extend([
            f"### {case.title()}",
            "",
            "| Unit | Count |",
            "|---|---|",
        ])
        for unit, count in sorted(metrics[case]['issuing_units'].items(), key=lambda x: -x[1]):
            lines.append(f"| {unit} | {count} |")
        lines.append("")
    
    lines.extend([
        "",
        "---",
        "",
        "*Generated by tools/generators/generate-comparison-matrix.py*",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate cross-case comparison matrix')
    parser.add_argument('--ledgers', '-l', nargs='+', required=True, help='Ledger JSON files')
    parser.add_argument('--output', '-o', required=True, help='Output markdown file')
    args = parser.parse_args()
    
    # Load ledgers
    ledgers = load_ledgers(args.ledgers)
    print(f"Loaded {len(ledgers)} cases: {', '.join(ledgers.keys())}")
    
    # Generate metrics
    metrics = generate_metrics(ledgers)
    
    # Generate markdown
    markdown = generate_markdown_table(metrics)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Generated comparison matrix: {args.output}")
    
    # Print summary
    total_events = sum(m['total_events'] for m in metrics.values())
    print(f"\nTotal events across all cases: {total_events}")


if __name__ == '__main__':
    main()
