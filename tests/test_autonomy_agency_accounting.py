from __future__ import annotations

import unittest

from kernel.development.autonomy_agency import (
    AgencyRole,
    make_agency_receipt,
    receipt_dict,
)


def fixtures():
    cycle = {
        "cycle_id": "cycle-1",
        "target_kind": "ISSUE",
        "target_number": 72,
        "decision": "PROBE",
        "study_method": "DEPENDENCY_TRACE",
    }
    proposal = {"proposal_id": "p1", "cycle_id": "cycle-1"}
    evidence = {"evidence_id": "e1", "proposal_id": "p1", "status": "LOCAL_CHECKS_PASS"}
    change = {"change_id": "c1", "disposition": "RETAIN_NO_MUTATION_LOCAL_EVIDENCE_PASS"}
    patch = {"plan_id": "w1", "disposition": "PROPOSAL_ONLY"}
    return cycle, proposal, evidence, change, patch


class AgencyAccountingTests(unittest.TestCase):
    def test_receipt_explicitly_denies_runtime_llm_credit(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        self.assertFalse(r.runtime_llm_invocation)
        self.assertEqual(
            r.strong_rsi_credit,
            "BOUNDED_AUTONOMOUS_AGENT_WITHOUT_LIVE_FULL_STRONG_RSI",
        )

    def test_target_and_method_are_venus_side_but_safe_command_universe_is_not(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        roles = {x.component: x.role for x in r.components}
        self.assertEqual(roles["target_selection"], AgencyRole.VENUS_STATE_OWNED)
        self.assertEqual(roles["study_method_selection"], AgencyRole.VENUS_LEARNED_STATE)
        self.assertEqual(roles["safe_command_universe"], AgencyRole.HOST_SCAFFOLD)
        self.assertEqual(roles["write_jurisdiction"], AgencyRole.EXTERNAL_GOVERNANCE)

    def test_local_execution_is_not_world_return(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        roles = {x.component: x.role for x in r.components}
        self.assertEqual(roles["local_test_evidence"], AgencyRole.LOCAL_EXECUTION_RECEIPT)
        self.assertEqual(roles["learning_return"], AgencyRole.EXTERNAL_WORLD_RETURN)
        self.assertNotEqual(roles["local_test_evidence"], roles["learning_return"])

    def test_git_carrier_is_not_reasoning_or_promotion(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        roles = {x.component: x.role for x in r.components}
        self.assertEqual(roles["git_branch_pr_materialization"], AgencyRole.CARRIER_ACTION)
        self.assertEqual(roles["merge_release_promotion"], AgencyRole.EXTERNAL_GOVERNANCE)
        self.assertFalse(r.promotion_authority)

    def test_implementation_authorship_is_not_retroactively_credited_to_venus(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        row = next(x for x in r.components if x.component == "implementation_authorship")
        self.assertEqual(row.role, AgencyRole.HOST_SCAFFOLD)
        self.assertFalse(row.causally_active)

    def test_claim_fence_is_explicit(self):
        d = receipt_dict(make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        ))
        self.assertFalse(d["phenomenal_consciousness_claim"])
        self.assertFalse(d["agi_claim"])
        self.assertFalse(d["open_ended_rsi_claim"])
        self.assertFalse(d["promotion_authority"])

    def test_identity_mismatch_fails_closed(self):
        cycle, proposal, evidence, change, patch = fixtures()
        proposal = dict(proposal)
        proposal["cycle_id"] = "other"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            make_agency_receipt(
                cycle=cycle,
                proposal=proposal,
                evidence=evidence,
                change=change,
                patch_plan=patch,
            )


    def test_meta_learning_strategy_is_venus_state_but_strategy_family_is_host_scaffold(self):
        r = make_agency_receipt(
            cycle=fixtures()[0],
            proposal=fixtures()[1],
            evidence=fixtures()[2],
            change=fixtures()[3],
            patch_plan=fixtures()[4],
        )
        roles = {x.component: x.role for x in r.components}
        self.assertEqual(
            roles["learning_strategy_selection"],
            AgencyRole.VENUS_LEARNED_STATE,
        )
        self.assertEqual(
            roles["learning_strategy_family"],
            AgencyRole.HOST_SCAFFOLD,
        )


if __name__ == "__main__":
    unittest.main()
