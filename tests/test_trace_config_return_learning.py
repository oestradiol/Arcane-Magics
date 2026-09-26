from __future__ import annotations

import unittest

from kernel.development.autonomous_learning import (
    extract_explicit_returns,
    extract_trace_config_returns,
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
        trace_rows=extract_trace_config_returns(
            (carrier,),authorized_logins=("oestradiol",)
        )
        self.assertEqual(
            tuple((key,useful) for _,key,useful in trace_rows),
            (("CROSS_SOURCE_BRIDGE",False),),
        )
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
            rows=extract_trace_config_returns(
                (carrier,),authorized_logins=("oestradiol",)
            )
            self.assertEqual(rows,())

    def test_duplicate_same_cycle_marker_counts_once(self):
        carrier=self.carrier(
            "oestradiol",
            "VENUS_TRACE_CONFIG_RETURN: MULTI_ANCHOR: UNHELPFUL",
        )
        carrier["comments"].append({
            "author":{"login":"oestradiol"},
            "body":"VENUS_TRACE_CONFIG_RETURN: MULTI_ANCHOR: UNHELPFUL",
            "createdAt":"2026-09-26T14:12:31Z",
        })
        rows=extract_trace_config_returns(
            (carrier,),authorized_logins=("oestradiol",)
        )
        self.assertEqual(len(rows),1)
        state=update_from_cycle_prs(
            empty_state(),(carrier,),authorized_logins=("oestradiol",)
        )
        self.assertEqual(state.trace_config_failure["MULTI_ANCHOR"],1)

    def test_conflicting_same_cycle_marker_yields_no_trace_learning(self):
        carrier=self.carrier(
            "oestradiol",
            "VENUS_TRACE_CONFIG_RETURN: TITLE_ANCHORED: USEFUL",
        )
        carrier["comments"].append({
            "author":{"login":"oestradiol"},
            "body":"VENUS_TRACE_CONFIG_RETURN: TITLE_ANCHORED: UNHELPFUL",
            "createdAt":"2026-09-26T14:12:31Z",
        })
        rows=extract_trace_config_returns(
            (carrier,),authorized_logins=("oestradiol",)
        )
        self.assertEqual(rows,())


if __name__=="__main__":
    unittest.main()
