from __future__ import annotations

import unittest

from kernel.development.autonomous_learning import (
    empty_state,
    update_from_cycle_prs,
)


class TraceConfigLearningTests(unittest.TestCase):
    def test_authorized_trace_config_return_updates_only_trace_axis(self):
        state=empty_state()
        carriers=({
            "number":229,
            "title":"venus: autonomous cycle issue-78",
            "state":"CLOSED",
            "_carrier_kind":"ISSUE",
            "comments":[{
                "author":{"login":"oestradiol"},
                "body":"VENUS_TRACE_CONFIG_RETURN: MULTI_ANCHOR: UNHELPFUL",
                "createdAt":"2026-09-26T14:18:00Z",
            }],
        },)
        out=update_from_cycle_prs(
            state,
            carriers,
            authorized_logins=("oestradiol",),
        )
        self.assertEqual(out.trace_config_failure.get("MULTI_ANCHOR"),1)
        self.assertEqual(out.trace_config_success.get("MULTI_ANCHOR",0),0)
        self.assertEqual(out.kind_success["ISSUE"],0)
        self.assertEqual(out.kind_failure["ISSUE"],0)

    def test_self_authored_trace_return_is_ignored(self):
        state=empty_state()
        carriers=({
            "number":229,
            "title":"venus: autonomous cycle issue-78",
            "state":"CLOSED",
            "_carrier_kind":"ISSUE",
            "comments":[{
                "author":{"login":"github-actions[bot]"},
                "body":"VENUS_TRACE_CONFIG_RETURN: MULTI_ANCHOR: USEFUL",
                "createdAt":"2026-09-26T14:18:00Z",
            }],
        },)
        out=update_from_cycle_prs(
            state,
            carriers,
            authorized_logins=("oestradiol",),
        )
        self.assertEqual(out.trace_config_success.get("MULTI_ANCHOR",0),0)


if __name__=="__main__":
    unittest.main()
