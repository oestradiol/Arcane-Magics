from __future__ import annotations

from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "execute_github_network_query",
    ROOT / "scripts/execute_github_network_query.py",
)
MOD=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class GitHubNetworkAdapterTests(unittest.TestCase):
    def test_query_relaxation_is_generic_and_bounded(self):
        rows=MOD.query_variants(
            "GENERALIZE_OR_REVISE_LATERAL_POLICY_ON_FRESH_TRANSFER alpha beta"
        )
        self.assertGreaterEqual(len(rows),1)
        self.assertLessEqual(len(rows),4)
        self.assertTrue(all(len(x.split()) <= 6 for x in rows))

    def test_selected_study_relaxation_preserves_learner_lexicon_but_can_escape_local_conjunction(self):
        query="development lateral reconstruction internalize epistemic basis expansion"
        anchors=("development","lateral","reconstruction","internalize","epistemic","basis")
        rows=MOD.query_variants(query,study_anchors=anchors)
        self.assertTrue(rows)
        self.assertLessEqual(len(rows),10)
        self.assertTrue(rows[0].startswith("development lateral reconstruction"))
        self.assertTrue(all(len(row.split()) >= 2 for row in rows))
        admitted=set(MOD._tokens(query + " " + " ".join(anchors)))
        self.assertTrue(all(set(row.split()) <= admitted for row in rows))
        self.assertTrue(
            any(not row.startswith("development lateral reconstruction") for row in rows)
        )
        self.assertTrue(any(len(row.split()) == 2 for row in rows))

    def test_selected_study_relaxation_never_invents_host_synonyms(self):
        rows=MOD.query_variants(
            "curriculum cognitive theater canonical english japanese pt-br math",
            study_anchors=("curriculum","cognitive","theater","canonical","english","japanese","pt-br","math"),
        )
        admitted={"curriculum","cognitive","theater","canonical","english","japanese","pt-br","math"}
        self.assertTrue(rows)
        self.assertTrue(all(set(row.split()) <= admitted for row in rows))
        self.assertNotIn("language"," ".join(rows))
        self.assertNotIn("multilingual"," ".join(rows))

    def test_source_collection_keeps_distinct_centers(self):
        issues=[{"items":[
            {
                "repository_url":"https://api.github.com/repos/a/one",
                "number":1,
                "html_url":"https://github.com/a/one/issues/1",
                "updated_at":"2026-09-25T00:00:00Z",
                "title":"x",
                "body":"one",
            },
            {
                "repository_url":"https://api.github.com/repos/a/one",
                "number":2,
                "html_url":"https://github.com/a/one/issues/2",
                "updated_at":"2026-09-25T00:01:00Z",
                "title":"y",
                "body":"same center",
            },
            {
                "repository_url":"https://api.github.com/repos/b/two",
                "number":3,
                "html_url":"https://github.com/b/two/issues/3",
                "updated_at":"2026-09-25T00:02:00Z",
                "title":"z",
                "body":"second center",
            },
        ]}]
        rows=MOD.collect_sources(issue_payloads=issues,repo_payloads=(),max_sources=6)
        self.assertEqual({x["center_id"] for x in rows},{"github-repo:a/one","github-repo:b/two"})
        self.assertEqual(len(rows),2)

    def test_selected_study_relevance_filters_unrelated_sources(self):
        issues=[{"items":[
            {
                "repository_url":"https://api.github.com/repos/noise/arxiv",
                "number":1,
                "html_url":"https://github.com/noise/arxiv/issues/1",
                "title":"Daily arXiv notification",
                "body":"new submissions and abstracts",
            },
            {
                "repository_url":"https://api.github.com/repos/rel/lateral",
                "number":2,
                "html_url":"https://github.com/rel/lateral/issues/2",
                "title":"Lateral epistemic reconstruction",
                "body":"independent faces support basis expansion and reconstruction",
            },
        ]}]
        rows=MOD.collect_sources(
            issue_payloads=issues,
            repo_payloads=(),
            max_sources=6,
            relevance_terms=("lateral","epistemic","reconstruction","basis","independent","faces"),
            min_relevance_matches=3,
        )
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["center_id"],"github-repo:rel/lateral")
        self.assertGreaterEqual(len(rows[0]["relevance_matches"]),3)

    def test_api_order_is_preserved_within_external_centers(self):
        issues=[{"items":[
            {
                "repository_url":"https://api.github.com/repos/z/first",
                "number":1,
                "html_url":"https://github.com/z/first/issues/1",
                "title":"epistemic lateral reconstruction",
                "body":"independent faces",
            },
            {
                "repository_url":"https://api.github.com/repos/a/second",
                "number":2,
                "html_url":"https://github.com/a/second/issues/2",
                "title":"epistemic lateral reconstruction",
                "body":"independent faces",
            },
        ]}]
        rows=MOD.collect_sources(
            issue_payloads=issues,
            repo_payloads=(),
            max_sources=2,
            relevance_terms=("epistemic","lateral","reconstruction"),
            min_relevance_matches=3,
        )
        self.assertEqual(
            [row["center_id"] for row in rows],
            ["github-repo:z/first","github-repo:a/second"],
        )

    def test_current_repo_is_not_preferred_over_external_centers(self):
        issues=[{"items":[
            {
                "repository_url":"https://api.github.com/repos/oestradiol/Arcane-Magics",
                "number":78,
                "html_url":"https://github.com/oestradiol/Arcane-Magics/issues/78",
                "title":"local",
                "body":"local",
            },
            {
                "repository_url":"https://api.github.com/repos/x/y",
                "number":9,
                "html_url":"https://github.com/x/y/issues/9",
                "title":"external",
                "body":"external",
            },
        ]}]
        rows=MOD.collect_sources(issue_payloads=issues,repo_payloads=(),max_sources=1)
        self.assertEqual(rows[0]["center_id"],"github-repo:x/y")

    def test_selected_study_authorship_is_admitted_without_execution_authority(self):
        src=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8")
        self.assertIn("LEARNER_DERIVED_FROM_SELECTED_STUDY", src)
        self.assertIn('"execution_owner"'," " + src)
        self.assertNotIn("subprocess", src.lower())

    def test_adapter_source_has_no_shell_or_returned_url_execution(self):
        src=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8").lower()
        for forbidden in ("subprocess","os.system","shell=true","eval(","exec("):
            self.assertNotIn(forbidden,src)
        self.assertIn('api_origin = "https://api.github.com"',src)
        self.assertIn('"returned_text_executed":false',src.replace(" ",""))
        self.assertIn('"returned_urls_followed":false',src.replace(" ",""))


if __name__=="__main__":
    unittest.main()
