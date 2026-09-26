from __future__ import annotations

import inspect
import unittest
from kernel.runtime import token_knn

PROGRAM={
    "schema":"Venus.StateOwnedTokenKNN.v0.1",
    "program":{
        "metric":"JACCARD","k":1,"exact_tie_decision":"0",
        "examples":[
            {"example_id":"a","tokens":["x","y"],"decision":"1"},
            {"example_id":"b","tokens":["z"],"decision":"0"},
        ],
    },
}

class TokenKNNTests(unittest.TestCase):
    def test_generic_executor_has_no_capability_vocabulary(self):
        src=inspect.getsource(token_knn).lower()
        for forbidden in ("lateral_episode","pull request","github","path_topology","issue 169"):
            self.assertNotIn(forbidden,src)

    def test_state_controls_decision(self):
        self.assertEqual(token_knn.execute(PROGRAM,["x"]),"1")
        self.assertEqual(token_knn.execute(PROGRAM,["z"]),"0")

if __name__=="__main__":
    unittest.main()
