from __future__ import annotations

import json
import unittest
from pathlib import Path

from kernel.development.capability_path_search import (
    Capability,
    capabilities_from_mapping,
    search_paths,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "kernel/development/EDU17R1_BINDER_CAPABILITY_GRAPH.json"


class CapabilityPathSearchTests(unittest.TestCase):
    def test_current_public_graph_has_unique_admissible_composition(self):
        obj = json.loads(GRAPH.read_text(encoding="utf-8"))
        result = search_paths(
            capabilities_from_mapping(obj),
            source_type=obj["source_type"],
            target_type=obj["target_type"],
            required_invariants=obj["required_invariants"],
        )
        self.assertEqual(result.status, "UNIQUE")
        self.assertEqual(
            result.paths,
            ((
                "IG3_GENERIC_RAW_CARRIER_SCANNER",
                "IG2_INDUCED_INCIDENCE_BASIS",
                "U4_SOURCE_GROUNDED_RELATION_BINDING",
                "WORLDMIRROR_EVIDENCE_BOUND_RELATION",
            ),),
        )

    def test_shortcut_that_drops_return_and_authority_invariants_is_rejected(self):
        result = search_paths(
            (
                Capability(
                    "unsafe-shortcut", "A", "B",
                    frozenset({"SOURCE_COORDINATES", "PROVENANCE"}), 0
                ),
                Capability(
                    "safe-1", "A", "X",
                    frozenset({"SOURCE_COORDINATES", "PROVENANCE", "INDEPENDENT_RETURN", "NO_SELF_MINTED_AUTHORITY"}), 1
                ),
                Capability(
                    "safe-2", "X", "B",
                    frozenset({"SOURCE_COORDINATES", "PROVENANCE", "INDEPENDENT_RETURN", "NO_SELF_MINTED_AUTHORITY"}), 1
                ),
            ),
            source_type="A",
            target_type="B",
            required_invariants=("SOURCE_COORDINATES","PROVENANCE","INDEPENDENT_RETURN","NO_SELF_MINTED_AUTHORITY"),
        )
        self.assertEqual(result.paths, (("safe-1", "safe-2"),))

    def test_equal_minimal_paths_withhold(self):
        req=frozenset({"R"})
        result = search_paths(
            (
                Capability("p1","A","B",req,1),
                Capability("p2","A","B",req,1),
            ),
            source_type="A", target_type="B", required_invariants=req,
        )
        self.assertEqual(result.status, "WITHHOLD_AMBIGUOUS_MINIMAL_COMPOSITION")


if __name__ == "__main__":
    unittest.main()
