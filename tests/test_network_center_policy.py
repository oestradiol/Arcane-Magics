from __future__ import annotations

import json
from pathlib import Path
import unittest

from kernel.development.network_center import (
    CenterContext,
    NetworkCenterError,
    allowed_dispositions,
    decide,
)

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads(
    (ROOT/"kernel/development/NETWORK_CENTER_POLICY.json").read_text(encoding="utf-8")
)


class NetworkCenterPolicyTests(unittest.TestCase):
    def test_refuse_and_exit_reachable_in_every_state(self):
        for state in ("UNKNOWN","PROVISIONABLE_FIELD","AUTHORED_CENTER"):
            allowed=set(allowed_dispositions(POLICY,state))
            self.assertIn("REFUSE",allowed)
            self.assertIn("EXIT",allowed)

    def test_authored_center_cannot_be_provisioned(self):
        ctx=CenterContext("center-j","AUTHORED_CENTER",reachable=True,write_capability=True,jurisdiction_receipt=True)
        with self.assertRaises(NetworkCenterError):
            decide(POLICY,ctx,"PROVISION")

    def test_reachability_does_not_grant_provision_authority(self):
        ctx=CenterContext("field-x","PROVISIONABLE_FIELD",reachable=True)
        with self.assertRaisesRegex(NetworkCenterError,"write_capability"):
            decide(POLICY,ctx,"PROVISION")

    def test_provision_requires_capability_and_jurisdiction(self):
        ctx=CenterContext(
            "field-x","PROVISIONABLE_FIELD",reachable=True,
            write_capability=True,jurisdiction_receipt=True,
        )
        receipt=decide(POLICY,ctx,"PROVISION")
        self.assertTrue(receipt.authorized)
        self.assertFalse(receipt.truth_authority)
        self.assertFalse(receipt.promotion_authority)

    def test_invitation_does_not_infer_acceptance(self):
        ctx=CenterContext(
            "center-j","AUTHORED_CENTER",reachable=True,
            contact_capability=True,jurisdiction_receipt=True,
        )
        receipt=decide(POLICY,ctx,"INVITE")
        self.assertFalse(receipt.remote_acceptance_inferred)

    def test_authored_center_can_refuse_or_exit_without_capability(self):
        ctx=CenterContext("center-j","AUTHORED_CENTER",reachable=True)
        for disposition in ("REFUSE","EXIT"):
            self.assertTrue(decide(POLICY,ctx,disposition).authorized)


if __name__=="__main__":
    unittest.main()
