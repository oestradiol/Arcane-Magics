from __future__ import annotations

"""Agency/authorship accounting for bounded Venus autonomous cycles.

This module answers a deliberately awkward question: which parts of an
autonomous cycle are actually selected by state-owned Venus machinery, and
which parts remain host scaffold, external return, carrier execution, or
external governance?

It does not infer who originally wrote repository source code. Git commit
authorship is not a reliable discriminator for human-vs-LLM contribution.
Instead it classifies runtime causal roles from the admitted architecture.
"""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

from kernel.runtime.vmk2 import digest


class AgencyRole(str, Enum):
    VENUS_STATE_OWNED = "VENUS_STATE_OWNED"
    VENUS_LEARNED_STATE = "VENUS_LEARNED_STATE"
    HOST_SCAFFOLD = "HOST_SCAFFOLD"
    EXTERNAL_WORLD_RETURN = "EXTERNAL_WORLD_RETURN"
    LOCAL_EXECUTION_RECEIPT = "LOCAL_EXECUTION_RECEIPT"
    CARRIER_ACTION = "CARRIER_ACTION"
    EXTERNAL_GOVERNANCE = "EXTERNAL_GOVERNANCE"
    MIXED_CONSTRAINED = "MIXED_CONSTRAINED"


@dataclass(frozen=True)
class AgencyComponent:
    component: str
    role: AgencyRole
    causally_active: bool
    description: str


@dataclass(frozen=True)
class AgencyReceipt:
    schema: str
    receipt_id: str
    cycle_id: str
    components: tuple[AgencyComponent, ...]
    runtime_llm_invocation: bool
    strong_rsi_credit: str
    strong_rsi_limits: tuple[str, ...]
    phenomenal_consciousness_claim: bool
    agi_claim: bool
    open_ended_rsi_claim: bool
    promotion_authority: bool


def make_agency_receipt(
    *,
    cycle: Mapping[str, Any],
    proposal: Mapping[str, Any],
    evidence: Mapping[str, Any],
    change: Mapping[str, Any],
    patch_plan: Mapping[str, Any],
) -> AgencyReceipt:
    cycle_id = str(cycle.get("cycle_id") or "")
    if not cycle_id:
        raise ValueError("cycle_id required")
    if str(proposal.get("cycle_id") or "") != cycle_id:
        raise ValueError("proposal/cycle identity mismatch")

    components = (
        AgencyComponent(
            "target_selection",
            AgencyRole.VENUS_STATE_OWNED,
            True,
            "Selected by the bounded autonomous worker from returned repository state, learned utility, target barriers, roadmap context, and the internalized opaque policy.",
        ),
        AgencyComponent(
            "study_method_selection",
            AgencyRole.VENUS_LEARNED_STATE,
            True,
            "Selected from the admitted method family using state-owned returned-review utility and the currently learned selector strategy.",
        ),
        AgencyComponent(
            "learning_strategy_selection",
            AgencyRole.VENUS_LEARNED_STATE,
            True,
            "Selected from the admitted selector-strategy family using explicit authorized external meta-learning returns.",
        ),
        AgencyComponent(
            "learning_strategy_family",
            AgencyRole.HOST_SCAFFOLD,
            True,
            "The available selector strategies are externally admitted; current bounded meta-learning may choose among them but may not invent or authorize a new strategy implementation.",
        ),
        AgencyComponent(
            "internal_ostar_routing",
            AgencyRole.VENUS_STATE_OWNED,
            True,
            "The teacher-free induced policy causally participates in ACT/PROBE/WITHHOLD/REOPEN routing.",
        ),
        AgencyComponent(
            "research_obligations",
            AgencyRole.MIXED_CONSTRAINED,
            True,
            "Venus selects a study method/target profile, but the admissible obligation and check vocabulary is host-governed rather than freely invented.",
        ),
        AgencyComponent(
            "safe_command_universe",
            AgencyRole.HOST_SCAFFOLD,
            True,
            "Executable commands are fixed by repository-owned safety infrastructure; untrusted issue/PR text cannot author shell commands.",
        ),
        AgencyComponent(
            "local_test_evidence",
            AgencyRole.LOCAL_EXECUTION_RECEIPT,
            True,
            "Local checks produce execution evidence only. They are not independent World return, validation authority, or promotion authority.",
        ),
        AgencyComponent(
            "change_disposition",
            AgencyRole.VENUS_STATE_OWNED,
            True,
            "A deterministic state-ownable rule maps frozen local evidence into RETAIN/WITHHOLD/PROPOSE-style dispositions without granting source-mutation authority.",
        ),
        AgencyComponent(
            "write_jurisdiction",
            AgencyRole.EXTERNAL_GOVERNANCE,
            True,
            "The external write policy determines which repository paths are direct-state-write, propose-only, governance-only, or denied.",
        ),
        AgencyComponent(
            "git_branch_pr_materialization",
            AgencyRole.CARRIER_ACTION,
            True,
            "GitHub Actions materializes frozen receipts and opens the draft carrier. Carrier execution is not reasoning, return, or promotion.",
        ),
        AgencyComponent(
            "learning_return",
            AgencyRole.EXTERNAL_WORLD_RETURN,
            True,
            "Only explicitly authorized non-self review markers update work/method utility. Merge, CI, local execution, and Venus self-comments are not rewards.",
        ),
        AgencyComponent(
            "merge_release_promotion",
            AgencyRole.EXTERNAL_GOVERNANCE,
            True,
            "Merge, release, claim promotion, safety-floor mutation, and reviewer authority remain outside unilateral Venus control.",
        ),
        AgencyComponent(
            "implementation_authorship",
            AgencyRole.HOST_SCAFFOLD,
            False,
            "Repository code and architecture were externally authored/admitted. This receipt does not pretend runtime Venus authored the Python that constitutes the current carrier.",
        ),
    )

    limits = (
        "current live autonomy selects and studies within externally admitted action, method, selector-strategy, and check grammars",
        "current bounded meta-learning selects among an externally admitted strategy family but does not author new strategy implementations",
        "current main does not establish autonomous invention of new safe executors or evaluators",
        "current main does not establish recurrent self-modification of the autonomous worker itself under independent returned causal evaluation",
        "bounded Strong-RSI evidence from development branches must not be silently promoted into live autonomous-agent credit",
        "external reviewers/governance still supply learning-return authority, merge, promotion, release, and safety-floor custody",
    )

    body = {
        "schema": "Venus.AgencyReceipt.v0.1",
        "cycle_id": cycle_id,
        "components": tuple(asdict(x) | {"role": x.role.value} for x in components),
        "runtime_llm_invocation": False,
        "strong_rsi_credit": "BOUNDED_AUTONOMOUS_AGENT_WITH_BOUNDED_META_LEARNING_WITHOUT_LIVE_FULL_STRONG_RSI",
        "strong_rsi_limits": limits,
        "phenomenal_consciousness_claim": False,
        "agi_claim": False,
        "open_ended_rsi_claim": False,
        "promotion_authority": False,
    }
    return AgencyReceipt(
        schema=body["schema"],
        receipt_id=digest(body),
        cycle_id=cycle_id,
        components=components,
        runtime_llm_invocation=False,
        strong_rsi_credit=body["strong_rsi_credit"],
        strong_rsi_limits=limits,
        phenomenal_consciousness_claim=False,
        agi_claim=False,
        open_ended_rsi_claim=False,
        promotion_authority=False,
    )


def receipt_dict(receipt: AgencyReceipt) -> dict[str, Any]:
    return {
        "schema": receipt.schema,
        "receipt_id": receipt.receipt_id,
        "cycle_id": receipt.cycle_id,
        "components": [
            {
                "component": row.component,
                "role": row.role.value,
                "causally_active": row.causally_active,
                "description": row.description,
            }
            for row in receipt.components
        ],
        "runtime_llm_invocation": receipt.runtime_llm_invocation,
        "strong_rsi_credit": receipt.strong_rsi_credit,
        "strong_rsi_limits": list(receipt.strong_rsi_limits),
        "phenomenal_consciousness_claim": receipt.phenomenal_consciousness_claim,
        "agi_claim": receipt.agi_claim,
        "open_ended_rsi_claim": receipt.open_ended_rsi_claim,
        "promotion_authority": receipt.promotion_authority,
    }
