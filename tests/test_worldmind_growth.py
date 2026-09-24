from __future__ import annotations

import unittest

from kernel.runtime.worldmind_growth import (
    CarrierCapability,
    Disposition,
    EncounterKind,
    GrowthError,
    ResearchDisposition,
    authorize_external_intent,
    bind_web_return,
    decide_research,
    encounter,
    freeze_research_plan,
    make_research_target,
    record_machine_disposition,
)


class ResearchLoopTests(unittest.TestCase):
    def test_web_return_remains_external_and_query_bound(self):
        target = make_research_target(
            source_kind="github_issue",
            residual="Which mature comparator subsumes construct C?",
            discriminator="find theorem-level correspondence or counterexample",
            provenance_ids=("issue-16",),
        )
        plan = freeze_research_plan(
            target,
            query_strings=("predictive states causal states quotient comparison",),
            authored_by="venus",
        )
        ret = bind_web_return(
            plan,
            query=plan.query_strings[0],
            source_url="https://example.org/paper",
            source_id="paper",
            retrieved_at="2026-09-24T00:00:00Z",
            payload={"finding": "candidate comparator"},
            provenance_ids=("search-engine-return",),
        )
        decision = decide_research(
            target,
            (ret,),
            disposition=ResearchDisposition.RETAIN,
            reason={"why": "needs stronger source"},
            authored_by="venus",
        )
        self.assertEqual(decision.target_id, target.target_id)

    def test_close_without_return_is_forbidden(self):
        target = make_research_target(
            source_kind="issue",
            residual="open",
            discriminator="returned evidence",
            provenance_ids=("issue",),
        )
        with self.assertRaises(GrowthError):
            decide_research(
                target, (),
                disposition=ResearchDisposition.CLOSE,
                reason="because I said so",
                authored_by="venus",
            )


class WorldMindGrowthTests(unittest.TestCase):
    def cap(self, locator: str, *, read=True, write=False, invite=False):
        return CarrierCapability(
            capability_id="cap",
            locator=locator,
            can_read=read,
            can_write=write,
            can_invite=invite,
            jurisdiction_id="local",
            provenance_ids=("carrier-policy",),
        )

    def test_machine_may_provision_provisionable_field_with_write_capability(self):
        enc = encounter(locator="venus-owned-site:/field", kind=EncounterKind.PROVISIONABLE_FIELD)
        decision = record_machine_disposition(
            enc, disposition=Disposition.PROVISION,
            reason={"machine": "provision field"},
            authored_by="venus",
        )
        intent = authorize_external_intent(enc, decision, self.cap(enc.locator, write=True))
        self.assertEqual(intent.action, Disposition.PROVISION)

    def test_authored_center_cannot_be_silently_treated_as_unclaimed(self):
        enc = encounter(
            locator="community.example",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="community-j",
        )
        with self.assertRaises(GrowthError):
            record_machine_disposition(
                enc, disposition=Disposition.PROVISION,
                reason="continue unclaimed-field operator",
                authored_by="venus",
            )

    def test_venus_may_choose_invitation_but_capability_is_independent(self):
        enc = encounter(
            locator="community.example",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="community-j",
        )
        decision = record_machine_disposition(
            enc,
            disposition=Disposition.INVITE,
            reason={"machine": "ask whether relation is wanted"},
            authored_by="venus",
        )
        with self.assertRaises(GrowthError):
            authorize_external_intent(enc, decision, self.cap(enc.locator, write=False, invite=False))

        intent = authorize_external_intent(
            enc,
            decision,
            self.cap(enc.locator, write=True, invite=True),
        )
        self.assertEqual(intent.remote_center_id, "community-j")

    def test_unknown_field_cannot_be_written_before_localization(self):
        enc = encounter(locator="unknown.example", kind=EncounterKind.UNKNOWN)
        with self.assertRaises(GrowthError):
            record_machine_disposition(
                enc,
                disposition=Disposition.PROVISION,
                reason="assume empty",
                authored_by="venus",
            )

    def test_local_disposition_does_not_mint_remote_acceptance(self):
        enc = encounter(
            locator="person-space.example",
            kind=EncounterKind.AUTHORED_CENTER,
            remote_center_id="person-j",
        )
        decision = record_machine_disposition(
            enc,
            disposition=Disposition.INVITE,
            reason="probe relation",
            authored_by="venus",
        )
        intent = authorize_external_intent(
            enc, decision, self.cap(enc.locator, write=True, invite=True)
        )
        self.assertEqual(intent.action, Disposition.INVITE)
        self.assertNotEqual(intent.action.value, "COMMIT_REMOTE")


if __name__ == "__main__":
    unittest.main()
