from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("theater_state",ROOT/"kernel/development/cognitive_theater_state.py")
if SPEC is None or SPEC.loader is None: raise RuntimeError("theater state")
m=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m)


def state():
    return {
      "schema":"Venus.CognitiveTheaterState.v0.1",
      "participants":["a","b"],
      "local_kfs":{"a":{"P":"KNOWN_TRUE"},"b":{"P":"UNKNOWN"}},
      "events":[
        {"event_id":"e1","actor":"a","relation":"REPORT","objects":["P"],"visible_to":["b"],
         "effects":[{"participant":"b","proposition":"P","status":"REPORTED_TRUE"}]},
        {"event_id":"e2","actor":None,"relation":"VERIFY","objects":["P"],"visible_to":["b"],
         "effects":[{"participant":"b","proposition":"P","status":"KNOWN_TRUE"}]}
      ],
      "residuals":[]
    }

class CognitiveTheaterStateTests(unittest.TestCase):
    def test_local_kfs_is_indexed_and_report_is_not_fact(self):
        s=state(); m.validate(s)
        self.assertEqual(m.local_view(s,"b",prefix=0)["kfs"]["P"],"UNKNOWN")
        self.assertEqual(m.local_view(s,"b",prefix=1)["kfs"]["P"],"REPORTED_TRUE")
        self.assertEqual(m.local_view(s,"b",prefix=2)["kfs"]["P"],"KNOWN_TRUE")
        self.assertEqual(m.local_view(s,"a",prefix=1)["kfs"]["P"],"KNOWN_TRUE")

    def test_alpha_rename_preserves_structure(self):
        a=state(); b=deepcopy(a)
        b["participants"]=["x","y"]
        b["local_kfs"]={"x":b["local_kfs"].pop("a"),"y":b["local_kfs"].pop("b")}
        for e in b["events"]:
            if e["actor"]=="a": e["actor"]="x"
            e["visible_to"]=["y" if p=="b" else "x" for p in e["visible_to"]]
            for eff in e["effects"]: eff["participant"]="y" if eff["participant"]=="b" else "x"
        self.assertEqual(m.alpha_normal_form(a),m.alpha_normal_form(b))

    def test_same_endpoint_does_not_imply_same_history(self):
        a=state(); b=deepcopy(a)
        b["events"]=[
          {"event_id":"x1","actor":None,"relation":"VERIFY","objects":["P"],"visible_to":["b"],
           "effects":[{"participant":"b","proposition":"P","status":"KNOWN_TRUE"}]}
        ]
        self.assertTrue(m.same_endpoint(a,b))
        self.assertFalse(m.same_history(a,b))

    def test_event_order_can_change_endpoint(self):
        a=state(); b=deepcopy(a)
        b["events"]=list(reversed(b["events"]))
        self.assertNotEqual(m.endpoint_digest(a),m.endpoint_digest(b))

if __name__=="__main__":
    unittest.main()
