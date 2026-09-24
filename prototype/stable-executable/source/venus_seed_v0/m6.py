from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class M6EArm(str, Enum):
    ABSENT_H='ABSENT_H'
    AUTHORIZED_R60_HARDCOPY='AUTHORIZED_R60_HARDCOPY'
    AUTHORIZED_R61_S4='AUTHORIZED_R61_S4'
    AUTHORIZED_R61_S5='AUTHORIZED_R61_S5'
    WITHHELD_AFTER_ADMIT='WITHHELD_AFTER_ADMIT'
    DELETED_AFTER_STEP2='DELETED_AFTER_STEP2'
    UNAUTHORIZED_DIRECT_H_INJECTION='UNAUTHORIZED_DIRECT_H_INJECTION'
    MISALIGNED_FUNCTIONAL_COMPARATOR='MISALIGNED_FUNCTIONAL_COMPARATOR'
    DIRECT_MATCHED_PRIOR='DIRECT_MATCHED_PRIOR'

@dataclass(frozen=True)
class M6EFreezeReceipt:
    freeze_manifest_sha256: str
    freeze_receipt_sha256: str=''
    status: str='FROZEN_UNEXECUTED'
    result_seed_drawn: bool=False
    result_seed_receipt_present: bool=False
    result_bearing_execution_started: bool=False
    result_artifacts_present: bool=False

@dataclass(frozen=True)
class M6EDesign:
    hypothesis_count: int=486
    higher_order_payload: tuple[int,...]=(1,1,2,2,2,2)
    task_count: int=32
    train_updates_per_task: int=6
    holdout_episodes_per_task: int=4
    arms: tuple[M6EArm,...]=tuple(M6EArm)
    matched_information_required: bool=True
    matched_update_budget_required: bool=True
    deletion_control_required: bool=True
    direct_prior_comparator_required: bool=True
    consequence_dominates_prior: bool=True


def assert_m6e_freeze_valid(freeze:M6EFreezeReceipt|None)->None:
    if freeze is None:
        raise RuntimeError('M6-E prospective freeze receipt required')
    if freeze.status!='FROZEN_UNEXECUTED':
        raise RuntimeError('M6-E freeze receipt is not frozen-unexecuted')
    if not isinstance(freeze.freeze_manifest_sha256,str) or len(freeze.freeze_manifest_sha256)!=64:
        raise RuntimeError('incomplete M6-E freeze binding')
    if not isinstance(freeze.freeze_receipt_sha256,str) or len(freeze.freeze_receipt_sha256)!=64:
        raise RuntimeError('incomplete M6-E freeze receipt binding')
    if freeze.result_bearing_execution_started or freeze.result_artifacts_present:
        raise RuntimeError('freeze receipt is not pre-execution')


def assert_m6e_execution_authorized(freeze:M6EFreezeReceipt|None, result_seed_receipt:Any|None=None)->None:
    """Fail closed after freeze until a separately drawn, freeze-bound result seed exists.

    This authorizes only execution of the already-frozen M6-E pipeline. It is not an M6
    scientific verdict and cannot be satisfied by the freeze transaction itself.
    """
    assert_m6e_freeze_valid(freeze)
    if result_seed_receipt is None:
        raise RuntimeError('M6-E frozen but unexecuted: post-freeze result seed receipt required')
    if freeze.result_seed_drawn or freeze.result_seed_receipt_present:
        raise RuntimeError('prospective freeze receipt must predate the result seed')
    if isinstance(result_seed_receipt,dict):
        if result_seed_receipt.get('freeze_manifest_sha256')!=freeze.freeze_manifest_sha256:
            raise RuntimeError('M6-E result seed is not bound to this freeze')
        if result_seed_receipt.get('freeze_receipt_sha256_at_draw')!=freeze.freeze_receipt_sha256:
            raise RuntimeError('M6-E result seed is not bound to this freeze receipt')
        if result_seed_receipt.get('rerolls')!=0 or not isinstance(result_seed_receipt.get('seed'),int) or result_seed_receipt.get('freeze_bytes_verified_at_draw') is not True:
            raise RuntimeError('invalid M6-E result seed receipt')
    else:
        raise RuntimeError('invalid M6-E result seed receipt')
