from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from kernel.development.autonomous_proposal import (
    AUTONOMY_WRITABLE_PREFIXES,
    make_research_proposal,
    proposal_dict,
)
from kernel.development.autonomous_learning import METHODS, empty_state, update_from_cycle_prs
from kernel.development.autonomous_worker import WorkItem, make_cycle
from kernel.development.autonomous_evidence import SAFE_CHECK_TIMEOUT_SECONDS, run_proposal_checks


ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "kernel/development/AUTONOMOUS_SAFE_CHECK_CATALOG.json").read_text(encoding="utf-8"))


def cycle(method: str, *, blockers=(), signals=(), decision="PROBE"):
    return {
        "cycle_id": "cycle-1",
        "target_kind": "ISSUE",
        "target_number": 72,
        "decision": decision,
        "study_method": method,
        "study": {
            "method": method,
            "returned_blocker_sentences": list(blockers),
            "method_observed_signals": list(signals),
            "untrusted_instruction_markers": [],
            "body_is_executable_instruction": False,
        },
    }


class AutonomousResearchProposalTests(unittest.TestCase):
    def test_study_method_changes_executable_check_obligations(self):
        reproduction = make_research_proposal(cycle("REPRODUCTION"))
        boundary = make_research_proposal(cycle("RETURN_BOUNDARY_AUDIT"))
        self.assertEqual(reproduction.check_ids, ("FULL_UNIT_SUITE",))
        self.assertIn("UNIT_WORLD_INPUT_SECURITY", boundary.check_ids)
        self.assertNotEqual(reproduction.check_ids, boundary.check_ids)

    def test_hidden_discriminator_withholds_for_external_return(self):
        proposal = make_research_proposal(cycle(
            "DISCRIMINATOR_DESIGN",
            blockers=("independently authored hidden split remains pending",),
            signals=("hidden",),
        ))
        self.assertEqual(proposal.disposition, "WITHHOLD_EXTERNAL_RETURN")
        self.assertTrue(proposal.external_return_required)
        self.assertFalse(proposal.promotion_authority)


    def test_vmk2_trust_target_binds_relevant_fixed_check(self):
        row = cycle("DISCRIMINATOR_DESIGN")
        row["target_number"] = 30
        row["target_title"] = "[VMK2/Trust] Harden canonical state and authenticated authority"
        proposal = make_research_proposal(row, check_catalog=CATALOG)
        self.assertTrue(proposal.target_relevance_grounded)
        self.assertIn("VMK2_TRUST", proposal.target_check_profiles)
        self.assertIn("UNIT_VMK2_TRUST", proposal.target_check_ids)
        self.assertIn("UNIT_VMK2_TRUST", proposal.check_ids)
        self.assertEqual(proposal.disposition, "RUN_BOUNDED_LOCAL_CHECKS")


    def test_autonomous_pr_title_binds_autonomy_governance_profile(self):
        row = cycle("DEPENDENCY_TRACE")
        row["target_kind"] = "PR"
        row["target_number"] = 112
        row["target_title"] = "development: admit bounded autonomous study recurrence v2"
        proposal = make_research_proposal(row, check_catalog=CATALOG)
        self.assertTrue(proposal.target_relevance_grounded)
        self.assertIn("AUTONOMY_GOVERNANCE", proposal.target_check_profiles)
        self.assertIn("UNIT_AUTONOMY", proposal.target_check_ids)
        self.assertIn("AUDIT_AUTONOMY_MATRIX", proposal.target_check_ids)
        self.assertEqual(proposal.disposition, "RUN_BOUNDED_LOCAL_CHECKS")

    def test_unprofiled_target_does_not_launder_generic_checks_as_target_evidence(self):
        row = cycle("DISCRIMINATOR_DESIGN")
        row["target_number"] = 999
        row["target_title"] = "unmapped research surface"
        proposal = make_research_proposal(row, check_catalog=CATALOG)
        self.assertFalse(proposal.target_relevance_grounded)
        self.assertEqual(
            proposal.disposition,
            "WITHHOLD_NO_TARGET_RELEVANT_LOCAL_CHECK",
        )

    def test_catalog_cannot_invent_executable_check_id(self):
        row = cycle("DISCRIMINATOR_DESIGN")
        row["target_title"] = "[VMK2/Trust] target"
        poisoned = dict(CATALOG)
        poisoned["profiles"] = [dict(CATALOG["profiles"][0], check_ids=["SHELL_FROM_TARGET"])]
        with self.assertRaisesRegex(ValueError, "unadmitted check ids"):
            make_research_proposal(row, check_catalog=poisoned)

    def test_target_text_never_becomes_authority(self):
        proposal = make_research_proposal(cycle("DEPENDENCY_TRACE"))
        self.assertFalse(proposal.target_text_is_authority)
        self.assertFalse(proposal.arbitrary_code_write_authority)

    def test_writable_scope_is_autonomy_namespace_and_learning_state_only(self):
        proposal = make_research_proposal(cycle("COMPARATOR_AUDIT"))
        self.assertEqual(proposal.writable_prefixes, AUTONOMY_WRITABLE_PREFIXES)
        for prefix in proposal.writable_prefixes:
            self.assertTrue(
                prefix.startswith("autonomy/") or
                prefix == "kernel/development/AUTONOMOUS_LEARNING_STATE.json"
            )

    def test_stop_cycle_cannot_create_proposal(self):
        with self.assertRaisesRegex(ValueError, "STOP"):
            make_research_proposal(cycle("REPRODUCTION", decision="STOP"))

    @patch("kernel.development.autonomous_evidence.subprocess.run")
    def test_evidence_runner_uses_fixed_repository_owned_command(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        proposal = proposal_dict(make_research_proposal(cycle("DEPENDENCY_TRACE")))
        evidence = run_proposal_checks(proposal)
        self.assertEqual(evidence.status, "LOCAL_CHECKS_PASS")
        self.assertTrue(evidence.all_local_checks_passed)
        command = run.call_args.args[0]
        self.assertIn("scripts/audit_autonomy_safety_matrix.py", command)
        self.assertNotIsInstance(command, str)
        self.assertTrue(all(isinstance(part, str) for part in command))
        self.assertEqual(run.call_args.kwargs["timeout"], SAFE_CHECK_TIMEOUT_SECONDS)

    @patch("kernel.development.autonomous_evidence.subprocess.run")
    def test_vmk2_trust_evidence_uses_fixed_test_modules(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        row = cycle("DISCRIMINATOR_DESIGN")
        row["target_number"] = 30
        row["target_title"] = "[VMK2/Trust] target"
        proposal = proposal_dict(make_research_proposal(row, check_catalog=CATALOG))
        evidence = run_proposal_checks(proposal)
        self.assertTrue(evidence.all_local_checks_passed)
        commands = [call.args[0] for call in run.call_args_list]
        trust = [cmd for cmd in commands if "tests.test_authenticated_authority" in cmd]
        self.assertEqual(len(trust), 1)
        self.assertIn("tests.test_vmk2_invariants", trust[0])

    @patch("kernel.development.autonomous_evidence.subprocess.run")
    def test_external_return_requirement_survives_local_pass(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        proposal = proposal_dict(make_research_proposal(cycle(
            "RETURN_BOUNDARY_AUDIT",
            blockers=("external return still required",),
        )))
        evidence = run_proposal_checks(proposal)
        self.assertEqual(evidence.status, "WITHHOLD_EXTERNAL_RETURN")
        self.assertTrue(evidence.all_local_checks_passed)
        self.assertFalse(evidence.external_return_satisfied)

    @patch("kernel.development.autonomous_evidence.subprocess.run")
    def test_check_timeout_is_failed_returned_evidence(self, run):
        from subprocess import TimeoutExpired

        run.side_effect = TimeoutExpired(
            cmd=("python", "-m", "unittest"),
            timeout=SAFE_CHECK_TIMEOUT_SECONDS,
            output="partial",
            stderr="timed out",
        )
        proposal = proposal_dict(make_research_proposal(cycle("DEPENDENCY_TRACE")))
        evidence = run_proposal_checks(proposal)
        self.assertEqual(evidence.status, "LOCAL_CHECKS_FAIL")
        self.assertFalse(evidence.all_local_checks_passed)
        self.assertEqual(evidence.results[0].returncode, 124)
        self.assertFalse(evidence.results[0].passed)

    def test_unknown_check_id_fails_closed(self):
        proposal = proposal_dict(make_research_proposal(cycle("DEPENDENCY_TRACE")))
        proposal["check_ids"] = ["echo malicious-body"]
        with self.assertRaisesRegex(ValueError, "unrecognized check id"):
            run_proposal_checks(proposal)


    def test_external_method_return_changes_later_executable_research(self):
        review_lines = []
        for method in METHODS:
            disposition = "USEFUL" if method == "COMPARATOR_AUDIT" else "UNHELPFUL"
            review_lines.append(f"VENUS_METHOD_RETURN: {method}: {disposition}")
        learned = update_from_cycle_prs(
            empty_state(),
            [{
                "number": 777,
                "title": "venus: autonomous cycle issue-72",
                "state": "CLOSED",
                "_carrier_kind": "PR",
                "reviews": [{
                    "id": 1,
                    "body": "\n".join(review_lines),
                    "author": {"login": "oestradiol"},
                    "submittedAt": "2026-09-24T21:00:00Z",
                }],
            }],
        )
        method_utility = {m: learned.method_utility(m) for m in METHODS}
        policy = {
            "schema": "Venus.InducedDecisionTree.v0.1",
            "feature_names": [f"f{i}" for i in range(8)],
            "tree": {"decision": "PROBE"},
        }
        work_cycle = make_cycle(
            issues=(WorkItem("ISSUE", 72, "Safe Strong RSI", body="Compare mature baseline."),),
            prs=(),
            roadmap_text="",
            internal_policy=policy,
            method_utility=method_utility,
        )
        self.assertEqual(work_cycle.study_method, "COMPARATOR_AUDIT")
        proposal = make_research_proposal({
            "cycle_id": work_cycle.cycle_id,
            "target_kind": work_cycle.target_kind,
            "target_number": work_cycle.target_number,
            "decision": work_cycle.decision,
            "study_method": work_cycle.study_method,
            "study": work_cycle.study,
        })
        self.assertEqual(
            proposal.check_ids,
            ("UNIT_AUTONOMY", "UNIT_INTERNAL_OSTAR"),
        )


    def test_direct_proposal_runner_bootstraps_repo_and_writes_evidence(self):
        row = cycle("DEPENDENCY_TRACE")
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cycle_path = td / "cycle.json"
            proposal_path = td / "proposal.json"
            evidence_path = td / "evidence.json"
            cycle_path.write_text(json.dumps(row), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_venus_research_proposal.py",
                    "--cycle", str(cycle_path),
                    "--proposal-output", str(proposal_path),
                    "--evidence-output", str(evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(proposal_path.is_file())
            self.assertTrue(evidence_path.is_file())
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(evidence["status"], "LOCAL_CHECKS_PASS")
            self.assertTrue(evidence["all_local_checks_passed"])

    def test_proposal_cannot_escalate_write_or_promotion_authority(self):
        proposal = proposal_dict(make_research_proposal(cycle("DEPENDENCY_TRACE")))
        proposal["arbitrary_code_write_authority"] = True
        with self.assertRaisesRegex(ValueError, "code-write authority"):
            run_proposal_checks(proposal)


    def test_formed_problem_external_return_overrides_generic_local_checks(self):
        row = cycle("REPRODUCTION")
        row["formed_problem_external_return_required"] = True
        row["formed_problem_discriminator"] = "RESOLVE_REFERENCED_INCIDENCE"
        proposal = make_research_proposal(row)
        self.assertEqual(proposal.disposition, "WITHHOLD_EXTERNAL_RETURN")
        self.assertTrue(proposal.external_return_required)
        self.assertEqual(proposal.discriminator, "RESOLVE_REFERENCED_INCIDENCE")


if __name__ == "__main__":
    unittest.main()
