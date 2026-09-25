from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.autonomous_recurrence import (
    extract_training_returns,
    load_catalog,
    make_live_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(
    ROOT / "kernel/development/AUTONOMOUS_RECURRENCE_CATALOG.json"
)


PROBLEM = {
    "problem_id": "problem-live-1",
    "disposition": "FORMED_BOUNDED_PROBLEM",
    "source_stream_ids": ["stream-live"],
    "residual_coordinates": ["continuation_state_unresolved"],
    "discriminator": "REPRODUCE_OR_REFRESH_CONTINUATION_STATE",
}


def marker(problem_id="problem-live-1", program_id="AUTONOMOUS_RESEARCH_LOOP_V1"):
    base = {
        "problem_id": "placeholder",
        "residual": "placeholder",
        "discriminator": "placeholder",
        "provenance_ids": ["placeholder"],
    }
    traces = [{
        "trace_id": "valid",
        "prior_state": "IDLE",
        "action": "FORM_PROBLEM",
        "payload": dict(base),
        "expect_success": True,
        "expected_next_state": "PROBLEM_FORMED_V2",
        "provenance_id": "review:return:valid",
    }]
    for key in tuple(base):
        payload = dict(base)
        payload.pop(key)
        traces.append({
            "trace_id": f"missing-{key}",
            "prior_state": "IDLE",
            "action": "FORM_PROBLEM",
            "payload": payload,
            "expect_success": False,
            "expected_next_state": None,
            "provenance_id": f"review:return:missing-{key}",
        })
    obj = {
        "schema": "Venus.LiveRecurrenceTrainingReturn.v0.1",
        "problem_id": problem_id,
        "program_id": program_id,
        "traces": traces,
    }
    return "VENUS_RECURRENCE_TRAINING_V1: " + json.dumps(obj, separators=(",", ":"))


def carrier(body, login="oestradiol", number=900):
    return {
        "_carrier_kind": "PR",
        "number": number,
        "reviews": [{
            "body": body,
            "author": {"login": login},
            "submittedAt": "2026-09-25T00:00:00Z",
        }],
    }


class LiveRecurrenceReturnTests(unittest.TestCase):
    def test_authorized_problem_specific_return_freezes_candidate(self):
        envelope = make_live_candidate(
            problem=PROBLEM,
            carriers=(carrier(marker()),),
            catalog=CATALOG,
            repository_root=ROOT,
            authorized_logins={"oestradiol"},
        )
        self.assertTrue(envelope["generated"])
        self.assertEqual(
            envelope["status"],
            "CANDIDATE_FROZEN_AWAITING_HELDOUT_RETURN",
        )
        self.assertEqual(envelope["problem_id"], PROBLEM["problem_id"])
        self.assertFalse(envelope["promotion_authority"])
        self.assertFalse(envelope["merge_authority"])
        self.assertFalse(envelope["truth_authority"])

    def test_wrong_problem_return_cannot_drive_current_problem(self):
        envelope = make_live_candidate(
            problem=PROBLEM,
            carriers=(carrier(marker(problem_id="other-problem")),),
            catalog=CATALOG,
            repository_root=ROOT,
            authorized_logins={"oestradiol"},
        )
        self.assertFalse(envelope["generated"])
        self.assertEqual(
            envelope["status"],
            "AWAITING_PROBLEM_SPECIFIC_EXTERNAL_RETURN",
        )

    def test_self_review_cannot_author_recurrence_return(self):
        rows = extract_training_returns(
            (carrier(marker(), login="github-actions[bot]"),),
            catalog=CATALOG,
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(rows, ())

    def test_unauthorized_reviewer_cannot_author_recurrence_return(self):
        rows = extract_training_returns(
            (carrier(marker(), login="random-person"),),
            catalog=CATALOG,
            authorized_logins={"oestradiol"},
        )
        self.assertEqual(rows, ())

    def test_multiple_returns_for_same_problem_fail_closed(self):
        envelope = make_live_candidate(
            problem=PROBLEM,
            carriers=(
                carrier(marker(), number=900),
                {
                    "_carrier_kind": "ISSUE",
                    "number": 901,
                    "comments": [{
                        "body": marker(),
                        "author": {"login": "oestradiol"},
                        "createdAt": "2026-09-25T00:01:00Z",
                    }],
                },
            ),
            catalog=CATALOG,
            repository_root=ROOT,
            authorized_logins={"oestradiol"},
        )
        self.assertFalse(envelope["generated"])
        self.assertEqual(
            envelope["status"],
            "WITHHOLD_AMBIGUOUS_EXTERNAL_RETURNS",
        )

    def test_nonallowlisted_program_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not uniquely allowlisted"):
            extract_training_returns(
                (carrier(marker(program_id="ARBITRARY_PROGRAM")),),
                catalog=CATALOG,
                authorized_logins={"oestradiol"},
            )

    def test_return_parser_has_no_execution_primitive(self):
        source = (
            ROOT / "kernel/development/autonomous_recurrence.py"
        ).read_text(encoding="utf-8").lower()
        for forbidden in ("subprocess", "os.system", "shell=true", "eval(", "exec("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
