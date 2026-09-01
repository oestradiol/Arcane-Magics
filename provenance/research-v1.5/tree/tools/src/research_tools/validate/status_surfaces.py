from __future__ import annotations

import re
from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.parse.nz_ledger import parse_nz_ledger
from research_tools.parse.taiwan_ledger import parse_taiwan_ledger
from research_tools.paths import RepoPaths
from research_tools.reports.nz_summary import compute_route_summary

VERSION_RE = re.compile(r'^version:\s*"([^"]+)"\s*$', re.MULTILINE)


def _safe_read_text(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, f"missing file: {path}"
    if not path.is_file():
        return None, f"not a regular file: {path}"
    return path.read_text(encoding="utf-8"), None


def _contains(check_name: str, path: Path, fragment: str, text: str, message: str) -> ValidationResult:
    status = "pass" if fragment in text else "fail"
    return ValidationResult(
        check_name=check_name,
        status=status,
        message=message if status == "pass" else f"{message} Required fragment missing.",
        path=str(path),
        expected=fragment if status == "fail" else None,
        found="missing" if status == "fail" else None,
    )


def _absent(check_name: str, path: Path, fragment: str, text: str, message: str) -> ValidationResult:
    status = "pass" if fragment.casefold() not in text.casefold() else "fail"
    return ValidationResult(
        check_name=check_name,
        status=status,
        message=message if status == "pass" else f"{message} Forbidden fragment present.",
        path=str(path),
        expected=f"no '{fragment}'",
        found=fragment if status == "fail" else "none",
    )


def _absent_pattern(check_name: str, path: Path, pattern: str, label: str, text: str, message: str) -> ValidationResult:
    match = re.search(pattern, text)
    status = "pass" if match is None else "fail"
    return ValidationResult(
        check_name=check_name,
        status=status,
        message=message if status == "pass" else f"{message} Forbidden pattern present.",
        path=str(path),
        expected=f"no pattern '{label}'",
        found="none" if status == "pass" else match.group(0),
    )


def _extract_version(path: Path) -> tuple[str | None, str | None]:
    text, error = _safe_read_text(path)
    if error is not None:
        return None, error
    match = VERSION_RE.search(text)
    if not match:
        return None, f"version not found in {path}"
    return match.group(1), None


def validate_status_surfaces(paths: RepoPaths) -> list[ValidationResult]:
    nz_events = parse_nz_ledger(paths.nz_route_root / "event-ledger-seed.md")
    taiwan_events = parse_taiwan_ledger(paths.taiwan_route_root / "taiwan-event-ledger-seed.md")
    nz_summary = compute_route_summary("nz", nz_events)
    taiwan_summary = compute_route_summary("taiwan", taiwan_events)
    version_value, version_error = _extract_version(paths.research_root / 'CITATION.cff')
    hosted_version = f"v{version_value}" if version_error is None else None
    locked_payoff_sentence = (
        "SUF shows that the New Zealand response should not be read only as centralized executive command, "
        "because public-information coordination is structurally central to the working coordination architecture."
    )

    root_readme = paths.research_root / "README.md"
    suf_readme = paths.suf_root / "README.md"
    project_status = paths.suf_root / "docs" / "project-status.md"
    pending_inventory = paths.suf_root / "docs" / "pending-inventory.md"
    contribution_note = paths.suf_root / "docs" / "argument" / "CONTRIBUTION_AND_POSITIONING.md"
    v1_bundle = paths.suf_root / "docs" / "argument" / "CONTRIBUTION_AND_POSITIONING.md"
    framework_overview = paths.suf_root / "docs" / "frontdoor" / "FRAMEWORK_OVERVIEW_AND_READING_GUIDE.md"
    how_to_read = paths.suf_root / "docs" / "frontdoor" / "FRAMEWORK_OVERVIEW_AND_READING_GUIDE.md"
    index_doc = paths.suf_root / "docs" / "INDEX.md"
    reviewer_doc = paths.suf_root / "docs" / "audit" / "OBJECTIONS_AND_EVIDENCE_STATUS.md"
    evidence_doc = paths.suf_root / "docs" / "audit" / "OBJECTIONS_AND_EVIDENCE_STATUS.md"
    interface_doc = paths.suf_root / "framework" / "framework-interface.md"
    publication_scope = paths.suf_root / "meta" / "publication-scope.md"
    roadmap = paths.suf_root / "ROADMAP.md"
    research_program = paths.suf_root / "framework" / "research-program.md"
    bounded_gain_note = (
        paths.suf_root
        / "applications"
        / "demonstrated-routes"
        / "states-and-societies"
        / "institutional-coordination-under-perturbation"
        / "bounded-gain-against-simpler-readings.md"
    )

    checks = []
    if version_error is None:
        checks.append(("status-root-readme-main-state", root_readme, f"Current `main` state: aligned with the hosted `{hosted_version}` New Zealand monograph-baseline release.", "Umbrella README keeps the current release-point alignment explicit."))
    else:
        checks.append(("status-citation-version-readable", paths.research_root / "CITATION.cff", None, "Hosted version can be read from CITATION.cff."))

    checks.extend([
        ("status-suf-readme-bounded-release", suf_readme, "bounded public academic package", "SUF README keeps the bounded public package wording explicit."),
        ("status-suf-readme-no-proof-whole-stack", suf_readme, "treat the New Zealand route as proof of the whole stack", "SUF README explicitly blocks treating the New Zealand route as proof of the whole stack."),
        ("status-suf-readme-metrics", suf_readme, f"a `{nz_summary.event_count}`-event New Zealand public ledger with a `{nz_summary.main_interval_count}`-event main interval", "SUF README exposes the current New Zealand baseline metrics."),
        ("status-suf-readme-taiwan", suf_readme, f"a `{taiwan_summary.event_count}`-event bounded Taiwan comparator with one conservative lag pair", "SUF README exposes the current Taiwan comparator baseline."),
        ("status-v1-bundle-metrics", v1_bundle, f"The main empirical anchor is a New Zealand pandemic-coordination route with a `{nz_summary.event_count}`-event public ledger, a `{nz_summary.main_interval_count}`-event main perturbation interval", "v1 academic bundle current New Zealand baseline matches the ledger."),
        ("status-v1-bundle-taiwan", v1_bundle, f"A bounded Taiwan comparator now adds a `{taiwan_summary.event_count}`-event archive-clean tranche under the same source-admission rule.", "v1 academic bundle current Taiwan baseline matches the comparator ledger."),
        ("status-interface-bridge-control", interface_doc, "Framework Interface is the **bridge/control** layer of Structured Unity Framework.", "Framework Interface explicitly uses bridge/control wording."),
        ("status-overview-layer-framing", framework_overview, "one methodological preface, two substantive layers, and a bridge/control layer", "Framework overview reflects the updated layer framing."),
        ("status-how-to-read-sp-link", how_to_read, "framework/sp-downstream-role.md", "Reading path includes the Structural Phenomenology downstream-role note."),
        ("status-how-to-read-bounded-gain-link", how_to_read, "bounded-gain-against-simpler-readings.md", "Reading path includes the bounded-gain note."),
        ("status-index-reviewer-doc", index_doc, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "Index includes the reviewer-objections doc."),
        ("status-index-evidence-doc", index_doc, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "Index includes the evidence-status matrix."),
        ("status-project-status-reviewer-doc", project_status, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "Project status links the reviewer-objections doc."),
        ("status-project-status-evidence-doc", project_status, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "Project status links the evidence-status matrix."),
        ("status-v1-reviewer-doc", v1_bundle, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "v1 bundle links the reviewer-objections doc."),
        ("status-v1-evidence-doc", v1_bundle, "audit/OBJECTIONS_AND_EVIDENCE_STATUS.md", "v1 bundle links the evidence-status matrix."),
        ("status-reviewer-purpose", reviewer_doc, "## Reviewer objections and current answers", "Reviewer-objections doc has its intended reviewer-objection section."),
        ("status-evidence-purpose", evidence_doc, "## Evidence-status matrix role", "Evidence-status matrix has its intended role section."),
        ("status-reviewer-doc-evidence-mapping", reviewer_doc, "stronger evidence-to-claim mapping", "Reviewer-objections doc keeps the remaining evidence-to-claim mapping burden explicit."),
        ("status-publication-scope-no-universal-proof", publication_scope, "that one demonstrated route proves the framework universally", "Publication scope explicitly blocks one-route universal proof language."),
        ("status-publication-scope-no-closure", publication_scope, "that the current package already yields objectively settled cross-domain measurement or strong predictive closure", "Publication scope explicitly blocks settled measurement and predictive closure claims."),
        ("status-contribution-note-locked-payoff", contribution_note, locked_payoff_sentence, "Contribution note keeps the locked public payoff sentence explicit."),
        ("status-project-status-locked-payoff", project_status, locked_payoff_sentence, "Project status matches the locked public payoff sentence."),
        ("status-bounded-gain-locked-payoff", bounded_gain_note, locked_payoff_sentence, "Bounded-gain note matches the locked public payoff sentence."),
        ("status-evidence-payoff-row", evidence_doc, locked_payoff_sentence, "Evidence-status matrix includes the locked payoff claim."),
        ("status-evidence-payoff-modeled-locked", evidence_doc, "modeled / provisional but publicly locked", "Evidence-status matrix marks the locked payoff sentence as modeled / provisional but publicly locked."),
        ("status-evidence-no-predictive-closure", evidence_doc, "| The current package demonstrates high-fit predictive closure. | not established |", "Evidence-status matrix keeps predictive closure as not established."),
        ("status-evidence-no-cross-domain-measurement", evidence_doc, "| The current package has objectively settled cross-domain measurement for `I`, `C`, `L`, and `U`. | not established |", "Evidence-status matrix keeps settled cross-domain measurement as not established."),
        ("status-evidence-no-strong-consciousness", evidence_doc, "| The current package justifies strong consciousness attribution to states or institutions. | not established |", "Evidence-status matrix keeps strong institutional consciousness attribution as not established."),
        ("status-research-program-open-work", research_program, "- deeper comparative execution beyond the current bounded Taiwan comparator", "Research program open-work section reflects the current Taiwan comparator posture."),
        ("status-publication-scope-layer-framing", publication_scope, "a methodological preface, two substantive framework layers, and one bridge/control layer", "Publication scope reflects the updated layer framing."),
    ])

    forbidden_checks = [
        ("status-readme-no-four-coordinated", suf_readme, "four coordinated theory layers", "SUF README no longer presents four coordinated theory layers.", None),
        ("status-overview-no-four-theory-layers", framework_overview, None, "Framework overview no longer presents four peer theory layers.", r"(?i)\bthe\s+four\s+theory\s+layers\b"),
        ("status-v1-no-four-coordinated", v1_bundle, "four coordinated theory layers", "v1 academic bundle no longer presents four coordinated theory layers.", None),
        ("status-publication-scope-no-four-layer", publication_scope, None, "Publication scope no longer presents the four-layer framework wording.", r"(?i)\bthe\s+four-layer\s+framework\b"),
        ("status-project-status-no-four-layer", project_status, None, "Project status no longer presents the four-layer framework wording.", r"(?i)\bthe\s+four-layer\s+framework\s+structure\b"),
        ("status-reviewer-doc-no-indexing-missing", reviewer_doc, "stronger completeness in reviewer-facing indexing", "Reviewer-objections doc no longer describes reviewer-facing indexing as missing or incomplete.", None),
        ("status-readme-no-nz-proves-stack", suf_readme, None, "SUF README does not imply that the New Zealand route proves the whole stack.", r"(?i)\b(?:new\s+zealand\s+route|route)\s+proves\s+the\s+whole\s+stack\b"),
        ("status-project-status-no-high-fit-closure", project_status, None, "Project status does not imply high-fit predictive closure.", r"(?i)\b(?:already\s+)?(?:yields|demonstrates|has|shows)\s+high-fit\s+predictive\s+closure\b"),
        ("status-readme-no-human-like-consciousness", suf_readme, None, "SUF README does not imply human-like consciousness attribution.", r"(?i)\b(?:justifies|supports|establishes|attributes?)\s+human-like\s+consciousness\b"),
        ("status-project-status-no-human-like-consciousness", project_status, None, "Project status does not imply human-like consciousness attribution.", r"(?i)\b(?:justifies|supports|establishes|attributes?)\s+human-like\s+consciousness\b"),
    ]

    results: list[ValidationResult] = []
    for check_name, path, fragment, message in checks:
        if fragment is None:
            results.append(ValidationResult(
                check_name=check_name,
                status="fail",
                message=f"{message} {version_error}.",
                path=str(path),
                expected='parseable version line in CITATION.cff',
                found=version_error,
            ))
            continue
        text, error = _safe_read_text(path)
        if error is not None:
            results.append(ValidationResult(
                check_name=check_name,
                status="fail",
                message=f"{message} Required-fragment check could not run because the file is unavailable.",
                path=str(path),
                expected=fragment,
                found=error,
            ))
            continue
        results.append(_contains(check_name, path, fragment, text, message))
    for check_name, path, fragment, message, pattern in forbidden_checks:
        text, error = _safe_read_text(path)
        if error is not None:
            expected = f"no '{fragment}'" if fragment is not None else f"no pattern '{pattern}'"
            results.append(ValidationResult(
                check_name=check_name,
                status="fail",
                message=f"{message} Forbidden-check could not run because the file is unavailable.",
                path=str(path),
                expected=expected,
                found=error,
            ))
            continue
        if pattern is not None:
            results.append(_absent_pattern(check_name, path, pattern, pattern, text, message))
        else:
            results.append(_absent(check_name, path, fragment, text, message))
    return results
