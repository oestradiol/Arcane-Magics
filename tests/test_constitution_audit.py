"""Negative suite for the constitution auditor.

An auditor is worthless until it has been shown to fail. Both prior auditors in
this repository shipped with real defects found exactly this way -- one
reported PASS over zero commits because a bare date parsed to nothing, the
other looped forever on a cyclic graph, and a hang is indistinguishable from a
pass. Neither would have been caught by exercising the happy path.

Every test here mutates a copy of the declaration, asserts the specific rule
fires, and restores. Run: python3 -m unittest tests/test_constitution_audit.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONST = ROOT / "kernel/CONSTITUTION.json"
SCRIPT = ROOT / "scripts/audit_constitution.py"
TEMP_ROLE_FILE = ROOT / "kernel/development/_TEST_TEMP_ROLE_PROBE.json"


def run_audit() -> tuple[int, str]:
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, timeout=120
    )
    return cp.returncode, cp.stdout + cp.stderr


def load() -> dict:
    return json.loads(CONST.read_text(encoding="utf-8"))


def with_mutation(mutate) -> tuple[int, str]:
    original = CONST.read_text(encoding="utf-8")
    try:
        doc = json.loads(original)
        mutate(doc)
        CONST.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        return run_audit()
    finally:
        CONST.write_text(original, encoding="utf-8")


class DeclaredConstitutionTests(unittest.TestCase):
    def test_declared_constitution_passes(self):
        code, out = run_audit()
        self.assertEqual(code, 0, out)
        self.assertIn("CONSTITUTION AUDIT PASS", out)

    def test_pass_message_denies_that_enforcement_is_correctness(self):
        _, out = run_audit()
        self.assertIn("Enforcement is not correctness", out)

    def test_register_is_live_constitution(self):
        # A constitution nothing may cite governs nothing.
        self.assertEqual(load()["register"], "LIVE_CONSTITUTION")

    def test_carries_no_promotion_or_truth_authority(self):
        doc = load()
        self.assertFalse(doc["promotion_authority"])
        self.assertFalse(doc["truth_authority"])

    def test_unenforced_items_are_visible_not_hidden(self):
        # The three deny-list items with no enforcing distinction must appear
        # in normal output. A gap that only shows up on failure is a gap that
        # gets forgotten.
        _, out = run_audit()
        for item in ("EVALUATOR_CUSTODY", "CLAIM_BINDING_AUTHORITY", "PARENT_CUSTODY"):
            with self.subTest(item=item):
                self.assertIn(item, out)

    def test_governing_but_unenforced_roles_are_visible(self):
        _, out = run_audit()
        for role in ("crystallizer_role", "lateralizer_role", "internalizer_role"):
            with self.subTest(role=role):
                self.assertIn(role, out)


class RuleFiresTests(unittest.TestCase):
    def assert_fires(self, rule: str, mutate) -> None:
        code, out = with_mutation(mutate)
        self.assertEqual(code, 1, f"{rule} did not fail the audit:\n{out}")
        self.assertTrue(
            any(line.strip().startswith(rule) for line in out.splitlines()),
            f"{rule} did not fire:\n{out}",
        )

    def test_k4_fires_when_a_law_goes_missing_from_the_tree(self):
        # The probe law is assembled at runtime and never appears as a literal
        # in this file. CORPUS_DIRS includes tests/, so writing it out plainly
        # would place it in the very corpus being searched and the check would
        # find the law inside the test asserting its absence.
        probe = "_".join(["ZZPROBE", "LAW"]) + " != " + "_".join(["NOT", "IN", "TREE"])
        self.assert_fires(
            "K4", lambda d: d["block_a_permanent_noncollapse_laws"]["laws"].append(probe)
        )

    def test_k4_fires_when_a_declared_absent_law_reappears(self):
        # Ratchet in the other direction: a law declared absent that IS present
        # must be promoted out of known_absent, or the list hides real coverage.
        def mutate(d):
            block = d["block_a_permanent_noncollapse_laws"]
            block["known_absent"].append(
                {
                    "law": "CODE_DELETION != INTERNALIZATION",  # present in the tree
                    "reason": "deliberately wrong, for the test",
                    "reopening_condition": "n/a",
                }
            )

        self.assert_fires("K4", mutate)

    def test_k4_fires_when_a_declared_absent_law_gives_no_reason(self):
        def mutate(d):
            for row in d["block_a_permanent_noncollapse_laws"]["known_absent"]:
                row["reason"] = ""

        self.assert_fires("K4", mutate)

    def test_k1_fires_on_deny_list_item_with_no_enforcement_entry(self):
        self.assert_fires(
            "K1",
            lambda d: d["block_b_deny_list"]["must_remain_outside"].append("NEW_UNGOVERNED_ITEM"),
        )

    def test_k1_fires_on_enforcement_none_without_a_reason(self):
        def mutate(d):
            for row in d["deny_list_enforcement"]:
                if row["item"] == "EVALUATOR_CUSTODY":
                    row["reason"] = "   "

        self.assert_fires("K1", mutate)

    def test_k1_fires_when_named_enforcing_artifact_is_missing(self):
        def mutate(d):
            for row in d["deny_list_enforcement"]:
                if row["item"] == "STOP":
                    row["enforced_by"] = "kernel/development/NO_SUCH_FILE.json"

        self.assert_fires("K1", mutate)

    def test_k3_fires_on_a_new_unreferenced_role(self):
        # The load-bearing rule: a *_role that claims to govern and is bound to
        # nothing must not pass silently.
        original = CONST.read_text(encoding="utf-8")
        TEMP_ROLE_FILE.write_text(
            json.dumps({"probe_role": "claims to govern and binds to nothing"}),
            encoding="utf-8",
        )
        try:
            code, out = run_audit()
            self.assertEqual(code, 1, out)
            self.assertIn("K3", out)
            self.assertIn("probe_role", out)
        finally:
            TEMP_ROLE_FILE.unlink(missing_ok=True)
            CONST.write_text(original, encoding="utf-8")

    def test_k3_fires_on_unenforced_role_without_reopening_condition(self):
        def mutate(d):
            for row in d["governing_roles_unenforced"]:
                if row["role"] == "crystallizer_role":
                    row["reopening_condition"] = ""

        self.assert_fires("K3", mutate)

    def test_k3_fires_when_an_unenforced_role_is_actually_referenced(self):
        # Ratchet: once a role is wired to code it must be promoted out of the
        # unenforced list, or the list would hide a real check.
        def mutate(d):
            d["governing_roles_unenforced"].append(
                {
                    "role": "actor_role",  # referenced by executable files today
                    "claims": "x",
                    "reopening_condition": "y",
                }
            )

        self.assert_fires("K3", mutate)

    def test_k3_fires_when_a_governing_role_names_a_missing_check(self):
        def mutate(d):
            d["governing_roles"]["crystallizer_role"] = "scripts/no_such_check.py"
            d["governing_roles_unenforced"] = [
                r for r in d["governing_roles_unenforced"] if r["role"] != "crystallizer_role"
            ]

        self.assert_fires("K3", mutate)

    def test_k2_fires_when_unrouted_paths_exceed_the_baseline(self):
        self.assert_fires(
            "K2", lambda d: d["block_c_authority_graph"].__setitem__("withhold_baseline", 0)
        )

    def test_k2_fires_when_no_baseline_is_declared(self):
        self.assert_fires(
            "K2", lambda d: d["block_c_authority_graph"].pop("withhold_baseline")
        )

    def test_k2_baseline_is_a_ratchet_not_a_target(self):
        # Shrinking the unrouted surface must never fail; only growth does.
        code, out = with_mutation(
            lambda d: d["block_c_authority_graph"].__setitem__("withhold_baseline", 9999)
        )
        self.assertEqual(code, 0, out)


class FailClosedTests(unittest.TestCase):
    def test_unparseable_constitution_withholds(self):
        original = CONST.read_text(encoding="utf-8")
        try:
            CONST.write_text("{ not json", encoding="utf-8")
            code, out = run_audit()
            self.assertEqual(code, 2)
            self.assertIn("WITHHOLD", out)
        finally:
            CONST.write_text(original, encoding="utf-8")

    def test_wrong_register_withholds(self):
        original = CONST.read_text(encoding="utf-8")
        try:
            doc = json.loads(original)
            doc["register"] = "CANDIDATE_NOT_ADMITTED"
            CONST.write_text(json.dumps(doc, indent=2), encoding="utf-8")
            code, out = run_audit()
            self.assertEqual(code, 2)
            self.assertIn("WITHHOLD", out)
        finally:
            CONST.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
