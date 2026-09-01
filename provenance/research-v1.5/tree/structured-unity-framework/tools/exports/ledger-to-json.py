#!/usr/bin/env python3
"""
Export SUF event ledger from Markdown to JSON/CSV.

Usage:
    python ledger-to-json.py --input <ledger.md> --output <ledger.json>
    python ledger-to-json.py --input <ledger.md> --output <ledger.csv> --format csv
    python ledger-to-json.py --corpus --output <corpus.json>

v1.5 analysis-ready tooling: structured exports for 76-event corpus validation.
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional


@dataclass
class LedgerEvent:
    """Structured representation of a single ledger event."""
    event_id: str
    timestamp_or_date: str = ""
    issuing_unit: str = ""
    receiving_units: List[str] = field(default_factory=list)
    action_type: str = ""
    dependency_type: List[str] = field(default_factory=list)
    implementation_marker: str = ""
    public_information_marker: str = ""
    source_citation: str = ""
    confidence_note: str = ""
    scale_tag: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_flat_dict(self) -> Dict[str, str]:
        """Flatten for CSV export."""
        return {
            'event_id': self.event_id,
            'timestamp_or_date': self.timestamp_or_date,
            'issuing_unit': self.issuing_unit,
            'receiving_units': '; '.join(self.receiving_units),
            'action_type': self.action_type,
            'dependency_type': '; '.join(self.dependency_type),
            'implementation_marker': self.implementation_marker,
            'public_information_marker': self.public_information_marker,
            'source_citation': self.source_citation,
            'confidence_note': self.confidence_note,
            'scale_tag': '; '.join(self.scale_tag),
        }


@dataclass
class LedgerMetadata:
    """Ledger-level metadata."""
    route_id: str = ""  # nz, tw, au
    route_name: str = ""
    purpose: str = ""
    current_status: str = ""
    total_events: int = 0
    expected_events: int = 0  # For validation
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedLedger:
    """Complete parsed ledger with metadata and events."""
    metadata: LedgerMetadata
    events: List[LedgerEvent] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metadata': self.metadata.to_dict(),
            'events': [e.to_dict() for e in self.events],
            'validation': {
                'errors': self.validation_errors,
                'valid': len(self.validation_errors) == 0
            }
        }


# Expected event counts per route (v1.5 verified corpus)
# NOTE: Australia has 13 verified events (5 additional events removed - sources unverified)
CORPUS_SPEC = {
    'nz': {'expected': 38, 'file': 'event-ledger-seed.md', 'name': 'New Zealand'},
    'tw': {'expected': 20, 'file': 'taiwan-event-ledger-seed.md', 'name': 'Taiwan'},
    'au': {'expected': 13, 'file': 'australia-event-ledger-seed.md', 'name': 'Australia'},
}
TOTAL_CORPUS_EVENTS = 71  # Verified (38 + 20 + 13)


def parse_event_section(section_text: str, event_id: str) -> LedgerEvent:
    """Parse a single event section from the ledger."""
    event = LedgerEvent(event_id=event_id)
    
    # Extract timestamp/date
    date_match = re.search(r'- `timestamp_or_date`: `([^`]+)`', section_text)
    if date_match:
        event.timestamp_or_date = date_match.group(1)
    
    # Extract issuing unit
    issuing_match = re.search(r'- `issuing_unit`: `([^`]+)`', section_text)
    if issuing_match:
        event.issuing_unit = issuing_match.group(1)
    
    # Extract receiving units (semicolon-separated, backtick-wrapped)
    receiving_match = re.search(r'- `receiving_units`: (.+?)(?=\n- `)', section_text, re.DOTALL)
    if receiving_match:
        units_text = receiving_match.group(1)
        event.receiving_units = [u.strip().strip('`') for u in units_text.split(';') if u.strip()]
    
    # Extract action type (multiline until next field)
    action_match = re.search(r'- `action_type`: (.+?)(?=\n- `)', section_text, re.DOTALL)
    if action_match:
        event.action_type = action_match.group(1).strip().replace('\n', ' ')
    
    # Extract dependency types
    dep_match = re.search(r'- `dependency_type`: (.+?)(?=\n- `)', section_text, re.DOTALL)
    if dep_match:
        deps_text = dep_match.group(1)
        event.dependency_type = [d.strip().strip('`') for d in deps_text.split(';') if d.strip()]
    
    # Extract implementation marker
    impl_match = re.search(r'- `implementation_marker`: `([^`]+)`', section_text)
    if impl_match:
        event.implementation_marker = impl_match.group(1)
    
    # Extract public information marker (can be multiple values)
    pub_match = re.search(r'- `public_information_marker`: (.+?)(?=\n- `)', section_text, re.DOTALL)
    if pub_match:
        pub_text = pub_match.group(1)
        # Handle both single values and semicolon-separated lists
        event.public_information_marker = pub_text.strip().replace('`', '').replace('\n', ' ')
    
    # Extract source citation (can have multiple sources)
    src_match = re.search(r'- `source_citation`: (.+?)(?=\n- `)', section_text, re.DOTALL)
    if src_match:
        event.source_citation = src_match.group(1).strip().replace('\n', ' ')
    
    # Extract confidence
    conf_match = re.search(r'- `confidence_note`: `([^`]+)`', section_text)
    if conf_match:
        event.confidence_note = conf_match.group(1)
    
    # Extract scale tags
    scale_match = re.search(r'- `scale_tag`: (.+?)(?=\n\n|$)', section_text, re.DOTALL)
    if scale_match:
        scales_text = scale_match.group(1)
        event.scale_tag = [s.strip().strip('`') for s in scales_text.split(';') if s.strip()]
    
    return event


def detect_route_id(ledger_text: str, filename: str) -> str:
    """Detect route ID from content or filename."""
    # Check filename first
    if 'taiwan' in filename.lower():
        return 'tw'
    if 'australia' in filename.lower():
        return 'au'
    if 'new-zealand' in filename.lower() or filename == 'event-ledger-seed.md':
        return 'nz'
    
    # Check content markers
    if 'tw-' in ledger_text[:5000] or 'Taiwan' in ledger_text[:1000]:
        return 'tw'
    if 'au-' in ledger_text[:5000] or 'Australia' in ledger_text[:1000]:
        return 'au'
    if 'nz-' in ledger_text[:5000] or 'New Zealand' in ledger_text[:1000]:
        return 'nz'
    
    return 'unknown'


def parse_ledger(ledger_text: str, filename: str) -> ParsedLedger:
    """Parse full ledger into structured format with validation."""
    route_id = detect_route_id(ledger_text, filename)
    spec = CORPUS_SPEC.get(route_id, {'expected': 0, 'name': 'Unknown'})
    
    metadata = LedgerMetadata(
        route_id=route_id,
        route_name=spec['name'],
        expected_events=spec['expected']
    )
    
    ledger = ParsedLedger(metadata=metadata)
    
    # Extract metadata
    purpose_match = re.search(r'^## Purpose\n\n(.+?)(?=\n##|$)', ledger_text, re.DOTALL)
    if purpose_match:
        metadata.purpose = purpose_match.group(1).strip().replace('\n', ' ')
    
    status_match = re.search(r'Current status: `([^`]+)`', ledger_text)
    if status_match:
        metadata.current_status = status_match.group(1)
    
    # Extract events using pattern: ### `event-id` followed by fields
    event_sections = re.findall(r'### `([a-z]+-[a-z]-\d+)`\n\n(.+?)(?=(?:### `[a-z]+-[a-z]-\d+`|## |\Z))', ledger_text, re.DOTALL)
    
    for event_id, section_text in event_sections:
        event = parse_event_section(section_text, event_id)
        ledger.events.append(event)
    
    metadata.total_events = len(ledger.events)
    
    # Validation
    if metadata.expected_events > 0 and metadata.total_events != metadata.expected_events:
        ledger.validation_errors.append(
            f"Event count mismatch: expected {metadata.expected_events}, found {metadata.total_events}"
        )
    
    # Check for required fields
    for event in ledger.events:
        if not event.timestamp_or_date:
            ledger.validation_errors.append(f"{event.event_id}: missing timestamp_or_date")
        if not event.issuing_unit:
            ledger.validation_errors.append(f"{event.event_id}: missing issuing_unit")
        if not event.source_citation:
            ledger.validation_errors.append(f"{event.event_id}: missing source_citation")
    
    return ledger


def export_json(ledger: ParsedLedger, output_path: Path) -> None:
    """Export ledger to JSON format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ledger.to_dict(), f, indent=2, ensure_ascii=False)


def export_csv(ledger: ParsedLedger, output_path: Path) -> None:
    """Export ledger to CSV format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not ledger.events:
        print(f"Warning: No events to export for {output_path}", file=sys.stderr)
        return
    
    fieldnames = list(ledger.events[0].to_flat_dict().keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for event in ledger.events:
            writer.writerow(event.to_flat_dict())


def parse_corpus(routes_dir: Path) -> Dict[str, ParsedLedger]:
    """Parse all three route ledgers for corpus validation."""
    corpus = {}
    
    route_paths = {
        'nz': routes_dir / 'event-ledger-seed.md',
        'tw': routes_dir / 'taiwan-event-ledger-seed.md',
        'au': routes_dir / 'australia-event-ledger-seed.md',
    }
    
    for route_id, path in route_paths.items():
        if not path.exists():
            print(f"Warning: {path} not found", file=sys.stderr)
            continue
        
        ledger_text = path.read_text(encoding='utf-8')
        ledger = parse_ledger(ledger_text, path.name)
        corpus[route_id] = ledger
    
    return corpus


def export_corpus_json(corpus: Dict[str, ParsedLedger], output_path: Path) -> None:
    """Export full 76-event corpus with metadata and cross-case summary."""
    total_events = sum(l.metadata.total_events for l in corpus.values())
    all_valid = all(len(l.validation_errors) == 0 for l in corpus.values())
    
    corpus_dict = {
        'metadata': {
            'total_events': total_events,
            'expected_total': TOTAL_CORPUS_EVENTS,
            'validation_passed': total_events == TOTAL_CORPUS_EVENTS and all_valid,
            'routes': {rid: l.metadata.to_dict() for rid, l in corpus.items()}
        },
        'cross_case_summary': {
            'issuing_units': {},
            'dependency_types': {},
            'scale_tags': {},
        },
        'routes': {rid: l.to_dict() for rid, l in corpus.items()}
    }
    
    # Compute cross-case summaries
    for ledger in corpus.values():
        for event in ledger.events:
            # Issuing units
            iu = event.issuing_unit
            if iu:
                corpus_dict['cross_case_summary']['issuing_units'][iu] = \
                    corpus_dict['cross_case_summary']['issuing_units'].get(iu, 0) + 1
            # Dependency types
            for dt in event.dependency_type:
                corpus_dict['cross_case_summary']['dependency_types'][dt] = \
                    corpus_dict['cross_case_summary']['dependency_types'].get(dt, 0) + 1
            # Scale tags
            for st in event.scale_tag:
                corpus_dict['cross_case_summary']['scale_tags'][st] = \
                    corpus_dict['cross_case_summary']['scale_tags'].get(st, 0) + 1
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(corpus_dict, f, indent=2, ensure_ascii=False)


def export_corpus_csv(corpus: Dict[str, ParsedLedger], output_path: Path) -> None:
    """Export full corpus as merged CSV with route column."""
    all_events = []
    for route_id, ledger in corpus.items():
        for event in ledger.events:
            flat = event.to_flat_dict()
            flat['route'] = route_id
            flat['route_name'] = ledger.metadata.route_name
            all_events.append(flat)
    
    if not all_events:
        print("Warning: No events to export", file=sys.stderr)
        return
    
    fieldnames = ['route', 'route_name'] + list(all_events[0].keys())[:-2]  # Exclude added route fields
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for event in all_events:
            writer.writerow({k: event[k] for k in fieldnames})


def main():
    parser = argparse.ArgumentParser(
        description='Export SUF ledger to structured formats (v1.5 analysis-ready tooling)'
    )
    parser.add_argument('--input', '-i', help='Input ledger markdown file')
    parser.add_argument('--output', '-o', required=True, help='Output file')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json',
                        help='Output format')
    parser.add_argument('--corpus', '-c', action='store_true',
                        help='Export full 76-event corpus (requires --routes-dir)')
    parser.add_argument('--routes-dir', '-r', type=Path,
                        default=Path('../applications/demonstrated-routes/states-and-societies/institutional-coordination-under-perturbation'),
                        help='Directory containing route ledger files (relative to tools/)')
    args = parser.parse_args()
    
    if args.corpus:
        # Export full 76-event corpus
        corpus = parse_corpus(args.routes_dir)
        
        if args.format == 'json':
            export_corpus_json(corpus, Path(args.output))
        else:
            export_corpus_csv(corpus, Path(args.output))
        
        total = sum(l.metadata.total_events for l in corpus.values())
        print(f"Exported 76-event corpus ({total} events from {len(corpus)} routes) to {args.output}")
        
        # Report validation status
        all_valid = True
        for route_id, ledger in corpus.items():
            if ledger.validation_errors:
                all_valid = False
                print(f"\nValidation errors for {route_id}:", file=sys.stderr)
                for err in ledger.validation_errors:
                    print(f"  - {err}", file=sys.stderr)
        
        if all_valid:
            print("✓ All validation checks passed")
        else:
            print("\n⚠ Validation failed - see errors above", file=sys.stderr)
            sys.exit(1)
    
    else:
        # Single ledger export
        if not args.input:
            parser.error('--input is required when not using --corpus')
        
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        ledger_text = input_path.read_text(encoding='utf-8')
        ledger = parse_ledger(ledger_text, input_path.name)
        
        if args.format == 'json':
            export_json(ledger, Path(args.output))
        else:
            export_csv(ledger, Path(args.output))
        
        print(f"Exported {ledger.metadata.total_events} events ({ledger.metadata.route_name}) to {args.output}")
        
        if ledger.validation_errors:
            print("\nValidation errors:", file=sys.stderr)
            for err in ledger.validation_errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✓ Validation passed")


if __name__ == '__main__':
    main()
