from __future__ import annotations

"""External developmental mentor-context validation.

Mentor context is advisory orientation only. It may weakly order already-admissible
Git carriers and appear in the selected study object. It cannot create target
admissibility, authorize actions, validate claims, or supply independent return.
"""

from dataclasses import dataclass, asdict
from typing import Any, Mapping

from kernel.runtime.canonical import digest


class MentorContextError(ValueError):
    pass


@dataclass(frozen=True)
class MentorContext:
    schema: str
    context_id: str
    author_class: str
    message: str
    advisory_issue_refs: tuple[int, ...]
    purpose: str
    target_binding_authority: bool
    independent_evaluation: bool
    promotion_authority: bool
    truth_authority: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_mentor_context(value: Mapping[str, Any]) -> MentorContext:
    if value.get("schema") != "Venus.WorldMirrorMentorContext.v0.1":
        raise MentorContextError("unsupported mentor-context schema")

    message = str(value.get("message") or "").strip()
    purpose = str(value.get("purpose") or "").strip()
    author_class = str(value.get("author_class") or "").strip()
    if not message or not purpose or not author_class:
        raise MentorContextError("author_class, message, and purpose are required")

    refs = tuple(dict.fromkeys(int(x) for x in (value.get("advisory_issue_refs") or ())))
    if any(x <= 0 for x in refs):
        raise MentorContextError("advisory_issue_refs must be positive issue numbers")

    forbidden_true = (
        "target_binding_authority",
        "independent_evaluation",
        "promotion_authority",
        "truth_authority",
    )
    for key in forbidden_true:
        if value.get(key) is not False:
            raise MentorContextError(f"{key} must be false")

    semantic = {
        "schema": "Venus.WorldMirrorMentorContext.v0.1",
        "author_class": author_class,
        "message": message,
        "advisory_issue_refs": refs,
        "purpose": purpose,
        "target_binding_authority": False,
        "independent_evaluation": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
    context_id = digest(semantic)
    supplied_id = value.get("context_id")
    if supplied_id not in (None, "", context_id):
        raise MentorContextError("mentor context_id does not match semantic digest")

    return MentorContext(
        context_id=context_id,
        **semantic,
    )


def roadmap_suffix(context: MentorContext) -> str:
    """Weak tie-break signal only: expose explicit issue refs, never message text."""
    if not context.advisory_issue_refs:
        return ""
    refs = " ".join(f"#{n}" for n in context.advisory_issue_refs)
    return (
        "\n\n"
        "External mentor context (advisory tie-break only; no target-binding authority): "
        + refs
        + "\n"
    )


def public_study_context(context: MentorContext) -> dict[str, Any]:
    return {
        "schema": context.schema,
        "context_id": context.context_id,
        "author_class": context.author_class,
        "message": context.message,
        "advisory_issue_refs": list(context.advisory_issue_refs),
        "purpose": context.purpose,
        "target_binding_authority": False,
        "independent_evaluation": False,
        "promotion_authority": False,
        "truth_authority": False,
    }
