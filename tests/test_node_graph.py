"""Negative suite for the node-graph auditor.

An auditor is worthless until it has been shown to fail. These tests mutate a
copy of the declared graph and assert that each rule fires. The cycle case in
particular is regression cover: the first implementation of is_ancestor had no
cycle guard and hung forever on a malformed graph, which is indistinguishable
from passing it.

Run: python3 -m unittest tests/test_node_graph.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "NODE_GRAPH.json"
SCRIPT = ROOT / "scripts/audit_node_graph.py"


def run_against(graph: dict) -> tuple[int, str]:
    """Run the auditor against a mutated graph, restoring the real one after."""
    original = GRAPH.read_text(encoding="utf-8")
    try:
        GRAPH.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        cp = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return cp.returncode, cp.stdout
    finally:
        GRAPH.write_text(original, encoding="utf-8")


def load() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def node(graph: dict, node_id: str) -> dict:
    return next(n for n in graph["nodes"] if n["id"] == node_id)


class DeclaredGraphTests(unittest.TestCase):
    def test_declared_graph_passes(self):
        code, out = run_against(load())
        self.assertEqual(code, 0, out)
        self.assertIn("NODE GRAPH AUDIT PASS", out)

    def test_pass_message_denies_that_conformance_is_correctness(self):
        _, out = run_against(load())
        self.assertIn("NODE_GRAPH_VALID != STRUCTURE_IS_RIGHT", out)

    def test_graph_is_candidate_without_authority(self):
        graph = load()
        self.assertEqual(graph["status"], "CANDIDATE_NOT_ADMITTED")
        self.assertFalse(graph["promotion_authority"])
        self.assertFalse(graph["truth_authority"])


class RuleFiresTests(unittest.TestCase):
    def assert_fires(self, rule: str, mutate) -> None:
        graph = load()
        mutate(graph)
        code, out = run_against(graph)
        self.assertEqual(code, 1, f"{rule} did not fail the audit:\n{out}")
        self.assertTrue(
            any(line.strip().startswith(rule) for line in out.splitlines()),
            f"{rule} did not fire:\n{out}",
        )

    def test_n1_coverage_fires_when_a_node_is_dropped(self):
        self.assert_fires(
            "N1", lambda g: g["nodes"].remove(node(g, "docs"))
        )

    def test_n2_boundary_fires_on_empty_boundary(self):
        self.assert_fires("N2", lambda g: node(g, "site").__setitem__("boundary", []))

    def test_n3_reopening_fires_on_residual_without_condition(self):
        self.assert_fires(
            "N3",
            lambda g: node(g, "site")["residuals"][0].__setitem__(
                "reopening_condition", ""
            ),
        )

    def test_n3_reopening_fires_on_unjustified_absence_of_residuals(self):
        self.assert_fires(
            "N3", lambda g: node(g, "licenses").pop("residuals_absence_justification")
        )

    def test_n4_acyclic_fires_on_two_roots(self):
        self.assert_fires("N4", lambda g: node(g, "docs").__setitem__("parent", None))

    def test_n4_acyclic_fires_on_cycle_without_hanging(self):
        # Regression: an unguarded parent walk looped forever here.
        self.assert_fires("N4", lambda g: node(g, "root").__setitem__("parent", "docs"))

    def test_n6_non_sovereign_fires_on_sibling_scope_overlap(self):
        self.assert_fires("N6", lambda g: node(g, "site")["scope"].append("docs/"))

    def test_n7_return_closed_fires_when_root_drops_the_union(self):
        # Root keeps a residual, so N3 stays quiet and N7 is isolated.
        def mutate(g):
            node(g, "root")["residuals"] = [
                {
                    "id": "ROOT_RX",
                    "statement": "an unrelated local concern",
                    "reopening_condition": "something local",
                }
            ]

        self.assert_fires("N7", mutate)


class FailClosedTests(unittest.TestCase):
    def test_unparseable_graph_withholds_rather_than_passing(self):
        original = GRAPH.read_text(encoding="utf-8")
        try:
            GRAPH.write_text("{ not json", encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(cp.returncode, 2)
            self.assertIn("WITHHOLD", cp.stdout)
        finally:
            GRAPH.write_text(original, encoding="utf-8")

    def test_empty_node_list_withholds(self):
        graph = load()
        graph["nodes"] = []
        code, out = run_against(graph)
        self.assertEqual(code, 2)
        self.assertIn("WITHHOLD", out)


if __name__ == "__main__":
    unittest.main()
