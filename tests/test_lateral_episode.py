from __future__ import annotations

import unittest
from kernel.development.lateral_episode import (
    LateralEpisodeError,
    propose_lateral_reconstruction,
    score_hidden_labels,
)


def row(n,label=None,path="kernel/x.py",commits=1,body=""):
    x={
        "pr_number":n,
        "body":body,
        "filenames":[path],
        "commits":commits,
        "additions":commits*3,
        "deletions":commits,
        "changed_files":1,
    }
    if label is not None:
        x["train_label"]=label
    return x


class LateralEpisodeTests(unittest.TestCase):
    def test_holdout_labels_fail_closed_before_prediction(self):
        data={
            "train":[row(1,False),row(2,True),row(3,True),row(4,False)],
            "holdout":[{**row(5),"holdout_label":True}],
        }
        with self.assertRaisesRegex(LateralEpisodeError,"holdout labels"):
            propose_lateral_reconstruction(data)

    def test_faces_remain_distinct_and_internalization_is_not_claimed(self):
        data={
            "train":[
                row(1,False,path="docs/a.md",body="#90"),
                row(2,False,path="docs/b.md",body="#91"),
                row(3,True,path="kernel/a.py",body="#92"),
                row(4,True,path="kernel/b.py",body="#93"),
                row(6,False,path="docs/c.md",body="#94"),
                row(7,True,path="kernel/c.py",body="#95"),
            ],
            "holdout":[row(5,path="kernel/z.py",body="#96")],
        }
        p=propose_lateral_reconstruction(data)
        self.assertIn(p.selected_face,{"path_topology","change_scale"})
        self.assertFalse(p.holdout_label_accessed)
        self.assertFalse(p.internalization_claim)
        self.assertIn("relation",p.preserved_face_sources)

    def test_hidden_scoring_cannot_change_frozen_prediction_ids(self):
        data={
            "train":[
                row(1,False,path="docs/a.md"),
                row(2,False,path="docs/b.md"),
                row(3,True,path="kernel/a.py"),
                row(4,True,path="kernel/b.py"),
                row(6,False,path="docs/c.md"),
                row(7,True,path="kernel/c.py"),
            ],
            "holdout":[row(5,path="kernel/z.py")],
        }
        p=propose_lateral_reconstruction(data)
        with self.assertRaisesRegex(LateralEpisodeError,"label IDs"):
            score_hidden_labels(p,{999:True})

if __name__=="__main__":
    unittest.main()
