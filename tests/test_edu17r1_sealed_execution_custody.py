from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from benchmarks.edu17r1_mention_incidence.run_sealed_conditions import (
    SealedExecutionError,
    execute,
    verify_freeze,
)


ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "benchmarks/edu17r1_mention_incidence/dev.jsonl"
FREEZE = ROOT / "benchmarks/edu17r1_mention_incidence/CONDITION_IMPLEMENTATIONS.json"


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EDU17R1SealedExecutionCustodyTests(unittest.TestCase):
    def test_prefrozen_artifact_hashes_match_repository(self):
        out = verify_freeze()
        self.assertEqual(set(out["conditions"]), {"A", "B", "C", "D"})

    def test_execution_uses_blind_rows_only_and_emits_all_conditions(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            blind = base / "blind.jsonl"
            rows = []
            for line in DEV.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                rows.append({"id": row["id"], "text": row["text"], "subtype": row.get("subtype")})
            blind.write_text(
                "".join(json.dumps(x, sort_keys=True) + "\n" for x in rows),
                encoding="utf-8",
            )
            manifest = base / "blind-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "Venus.EDU17R1BlindInputManifest.v0.1",
                        "benchmark": "edu17r1_mention_incidence",
                        "source_hidden_sha256": "0" * 64,
                        "condition_freeze_sha256": sha256_bytes(FREEZE),
                        "blind_input_sha256": sha256_bytes(blind),
                        "n": len(rows),
                        "excluded_fields": ["answer", "expected", "gold", "label", "rationale"],
                        "labels_exposed": False,
                        "promotion_authority": False,
                    },
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )
            out = execute(blind, manifest, base / "run")
            self.assertFalse(out["gold_labels_read"])
            self.assertFalse(out["scoring_performed"])
            self.assertFalse(out["promotion_authority"])
            self.assertEqual(set(out["conditions"]), {"A", "B", "C", "D"})
            for cid in ("A", "B", "C", "D"):
                self.assertEqual(out["conditions"][cid]["n"], len(rows))

    def test_sensitive_field_in_blind_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            blind = base / "blind.jsonl"
            blind.write_text(
                json.dumps({"id": "x", "text": "x", "label": "incidence"}) + "\n",
                encoding="utf-8",
            )
            manifest = base / "blind-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "Venus.EDU17R1BlindInputManifest.v0.1",
                        "source_hidden_sha256": "0" * 64,
                        "condition_freeze_sha256": sha256_bytes(FREEZE),
                        "blind_input_sha256": sha256_bytes(blind),
                        "n": 1,
                        "labels_exposed": False,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SealedExecutionError, "sensitive field"):
                execute(blind, manifest, base / "run")

    def test_blind_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            blind = base / "blind.jsonl"
            blind.write_text(json.dumps({"id": "x", "text": "x"}) + "\n", encoding="utf-8")
            manifest = base / "blind-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "Venus.EDU17R1BlindInputManifest.v0.1",
                        "source_hidden_sha256": "0" * 64,
                        "condition_freeze_sha256": sha256_bytes(FREEZE),
                        "blind_input_sha256": "f" * 64,
                        "n": 1,
                        "labels_exposed": False,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SealedExecutionError, "blind input hash mismatch"):
                execute(blind, manifest, base / "run")


if __name__ == "__main__":
    unittest.main()
