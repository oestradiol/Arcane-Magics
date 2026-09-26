from __future__ import annotations

import unittest

from kernel.development.autonomous_learning import (
    extract_explicit_returns,
    update_from_cycle_prs,
    empty_state,
)


class TraceConfigReturnedLearningTests(unittest.TestCase):
    def carrier(self, login: str, body: str):
        return {
            "_carrier_kind": "ISSUE",
            "number": 999,
            "title": "venus: autonomous cycle issue-17",
            "comments": [{
                "author": {"login": login},
                "body": body,
                "createdAt": "2026-09-26T14:12:30Z",
            }],
        }

    def test_authorized_trace_config_return_updates_separate_axis(self):
        carrier=self.carrier(
            "oestradiol",
            "VENUS_WORK_RETURN: USEFUL\n"
            "VENUS_TRACE_CONFIG_RETURN: CROSS_SOURCE_BRIDGE: UNHELPFUL",
        )
        rows=extract_explicit_returns((carrier,),authorized_logins=("oestradiol",))
        self.assertTrue(any(axis=="KIND" and useful for _,axis,_,useful in rows))
        self.assertTrue(any(
            axis=="TRACE_CONFIG" and key=="CROSS_SOURCE_BRIDGE" and not useful
            for _,axis,key,useful in rows
        ))
        state=update_from_cycle_prs(
            empty_state(),(carrier,),authorized_logins=("oestradiol",)
        )
        self.assertEqual(state.trace_config_failure["CROSS_SOURCE_BRIDGE"],1)
        self.assertEqual(state.trace_config_success.get("CROSS_SOURCE_BRIDGE",0),0)
        self.assertFalse(state.trace_config_utility("CROSS_SOURCE_BRIDGE") > 0)

    def test_unauthorized_or_self_comment_cannot_train_trace_config(self):
        for login in ("intruder","github-actions[bot]"):
            carrier=self.carrier(
                login,
                "VENUS_TRACE_CONFIG_RETURN: CROSS_SOURCE_BRIDGE: USEFUL",
            )
            rows=extract_explicit_returns((carrier,),authorized_logins=("oestradiol",))
            self.assertFalse(any(axis=="TRACE_CONFIG" for _,axis,_,_ in rows))


if __name__=="__main__":
    unittest.main()
