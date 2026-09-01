from __future__ import annotations

from pathlib import Path

from research_tools.models.reports import ValidationResult
from research_tools.validate.links import validate_markdown_links

REQUIRED_KNOWLEDGE_FILES = (
    "README.md",
    "knowledge-package-spec.md",
    "suf-relationship.md",
    "studying-and-teaching-with-suf.md",
    "_indexes/knowledge-index.md",
    "_indexes/node-index.md",
    "study-routes/README.md",
)


def _contains_check(path: Path, needle: str, check_name: str, message: str) -> ValidationResult:
    text = path.read_text(encoding="utf-8")
    status = "pass" if needle in text else "fail"
    return ValidationResult(
        check_name=check_name,
        status=status,
        message=message if status == "pass" else f"{message} Missing expected reference.",
        path=str(path),
        expected=needle,
        found=needle if status == "pass" else "missing",
    )


def validate_knowledge_package(knowledge_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    results.extend(validate_markdown_links(knowledge_root))

    for relative_path in REQUIRED_KNOWLEDGE_FILES:
        full_path = knowledge_root / relative_path
        status = "pass" if full_path.exists() else "fail"
        results.append(
            ValidationResult(
                check_name="knowledge-required-file",
                status=status,
                message="Required Knowledge surface exists." if status == "pass" else "Required Knowledge surface is missing.",
                path=str(full_path),
                expected=relative_path,
                found=relative_path if status == "pass" else "missing",
            )
        )

    readme_path = knowledge_root / "README.md"
    spec_path = knowledge_root / "knowledge-package-spec.md"
    relationship_path = knowledge_root / "suf-relationship.md"
    contributing_path = knowledge_root / "CONTRIBUTING.md"

    if readme_path.exists():
        for needle, check_name, message in (
            ("_indexes/knowledge-index.md", "knowledge-readme-entry-link", "Knowledge README references the main index."),
            ("../structured-unity-framework/README.md", "knowledge-readme-suf-link", "Knowledge README references the sibling SUF package."),
            ("primary scaffold", "knowledge-readme-primary-scaffold", "Knowledge README includes primary scaffold wording."),
            ("supporting scaffold", "knowledge-readme-supporting-scaffold", "Knowledge README includes supporting scaffold wording."),
            ("domain-native lead", "knowledge-readme-domain-native-lead", "Knowledge README includes domain-native lead wording."),
            ("primary_scaffold", "knowledge-readme-primary-scaffold-code", "Knowledge README includes primary_scaffold."),
            ("supporting_scaffold", "knowledge-readme-supporting-scaffold-code", "Knowledge README includes supporting_scaffold."),
            ("domain_native_lead", "knowledge-readme-domain-native-lead-code", "Knowledge README includes domain_native_lead."),
        ):
            results.append(_contains_check(readme_path, needle, check_name, message))

    if spec_path.exists():
        for needle, check_name, message in (
            ("knowledge-package-spec.md", "knowledge-spec-self-reference", "Knowledge package spec uses the normalized live filename."),
            ("`suf_role`", "knowledge-spec-suf-role", "Knowledge package spec documents suf_role."),
            ("primary_scaffold", "knowledge-spec-primary-scaffold", "Knowledge package spec includes primary_scaffold."),
            ("supporting_scaffold", "knowledge-spec-supporting-scaffold", "Knowledge package spec includes supporting_scaffold."),
            ("domain_native_lead", "knowledge-spec-domain-native-lead", "Knowledge package spec includes domain_native_lead."),
            ("Handoff rule", "knowledge-spec-handoff-rule", "Knowledge package spec includes a handoff rule."),
        ):
            results.append(_contains_check(spec_path, needle, check_name, message))

    if relationship_path.exists():
        for needle, check_name, message in (
            ("primary scaffold", "knowledge-relationship-primary-scaffold", "SUF relationship note includes primary scaffold wording."),
            ("supporting scaffold", "knowledge-relationship-supporting-scaffold", "SUF relationship note includes supporting scaffold wording."),
            ("domain-native lead", "knowledge-relationship-domain-native-lead", "SUF relationship note includes domain-native lead wording."),
            ("Handoff rule", "knowledge-relationship-handoff-rule", "SUF relationship note includes a handoff rule."),
        ):
            results.append(_contains_check(relationship_path, needle, check_name, message))

    if contributing_path.exists():
        results.append(
            _contains_check(
                contributing_path,
                "knowledge-package-spec.md",
                "knowledge-contributing-spec-link",
                "Knowledge contributing guide references the normalized spec filename.",
            )
        )

    legacy_hits: list[str] = []
    for markdown_file in knowledge_root.rglob("*.md"):
        text = markdown_file.read_text(encoding="utf-8")
        if "Knowledge Package Spec.md" in text:
            legacy_hits.append(str(markdown_file))
    results.append(
        ValidationResult(
            check_name="knowledge-legacy-filename",
            status="pass" if not legacy_hits else "fail",
            message="No stale spaced legacy filename remains in Knowledge package prose." if not legacy_hits else "Stale spaced legacy filename remains in Knowledge package prose.",
            expected="no 'Knowledge Package Spec.md' references",
            found=", ".join(legacy_hits) if legacy_hits else "none",
        )
    )

    knowledge_map_root = knowledge_root / "map"
    role_tokens = ("primary_scaffold", "supporting_scaffold", "domain_native_lead")
    hub_markers = (
        'status: "deepened hub node"',
        "status: 'deepened hub node'",
        "knowledge/status/deepened-hub",
        "suf/hub",
    )
    handoff_markers = (
        "should not",
        "better local",
        "domain-native",
        "recede",
        "yield",
        "not be mistaken",
        "not a replacement",
        "not the whole",
        "not the only",
    )
    forbidden_overclaim_fragments = (
        "suf explains everything",
        "suf is the only legitimate framework",
        "suf is the mandatory voice",
        "suf exhausts the package",
        "suf should remain in the foreground everywhere",
    )

    role_failures: list[str] = []
    handoff_failures: list[str] = []
    overclaim_hits: list[str] = []

    if knowledge_map_root.exists():
        for markdown_file in knowledge_map_root.rglob("*.md"):
            text = markdown_file.read_text(encoding="utf-8")
            text_lower = text.lower()
            is_deepened_hub = any(marker in text for marker in hub_markers)
            mentions_suf = "SUF" in text

            if is_deepened_hub and mentions_suf and not any(token in text for token in role_tokens):
                role_failures.append(str(markdown_file))

            if is_deepened_hub and mentions_suf and not any(marker in text_lower for marker in handoff_markers):
                handoff_failures.append(str(markdown_file))

            matching_overclaims = [fragment for fragment in forbidden_overclaim_fragments if fragment in text_lower]
            if matching_overclaims:
                overclaim_hits.append(f"{markdown_file}: {', '.join(matching_overclaims)}")

    results.append(
        ValidationResult(
            check_name="knowledge-map-suf-role-discipline",
            status="pass" if not role_failures else "fail",
            message=(
                "Deepened hub notes that foreground SUF also state an explicit SUF role."
                if not role_failures
                else "Some deepened hub notes foreground SUF without stating an explicit SUF role."
            ),
            expected="Deepened SUF-foregrounding hub notes include primary_scaffold, supporting_scaffold, or domain_native_lead",
            found=", ".join(role_failures) if role_failures else "none",
        )
    )

    results.append(
        ValidationResult(
            check_name="knowledge-map-suf-handoff-discipline",
            status="pass" if not handoff_failures else "fail",
            message=(
                "Deepened hub notes that foreground SUF also include caution or handoff language."
                if not handoff_failures
                else "Some deepened hub notes foreground SUF without caution or handoff language."
            ),
            expected="Deepened SUF-foregrounding hub notes include at least one caution or handoff marker",
            found=", ".join(handoff_failures) if handoff_failures else "none",
        )
    )

    results.append(
        ValidationResult(
            check_name="knowledge-map-no-suf-overclaim",
            status="pass" if not overclaim_hits else "fail",
            message=(
                "Knowledge map prose does not contain tracked SUF-takeover or totalizing overclaim phrases."
                if not overclaim_hits
                else "Knowledge map prose contains tracked SUF-takeover or totalizing overclaim phrases."
            ),
            expected="no tracked SUF-takeover or totalizing overclaim phrases",
            found="; ".join(overclaim_hits) if overclaim_hits else "none",
        )
    )

    return results
