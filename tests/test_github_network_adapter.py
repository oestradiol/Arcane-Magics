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

    def test_adapter_source_has_no_shell_or_returned_url_execution(self):
        src=(ROOT/"scripts/execute_github_network_query.py").read_text(encoding="utf-8").lower()
        for forbidden in ("subprocess","os.system","shell=true","eval(","exec("):
            self.assertNotIn(forbidden,src)
        self.assertIn('api_origin = "https://api.github.com"',src)
        self.assertIn('"returned_text_executed":false',src.replace(" ",""))
        self.assertIn('"returned_urls_followed":false',src.replace(" ",""))


if __name__=="__main__":
    unittest.main()
