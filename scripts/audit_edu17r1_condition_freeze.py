#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BENCH=ROOT/"benchmarks/edu17r1_mention_incidence"
FREEZE=BENCH/"CONDITION_IMPLEMENTATIONS.json"

def git_blob_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def execute(script:Path, blind:Path, output:Path):
    subprocess.run([sys.executable,str(script),str(blind),"--output",str(output)],check=True,cwd=ROOT)
    return [json.loads(x) for x in output.read_text(encoding="utf-8").splitlines() if x.strip()]

def audit():
    freeze=json.loads(FREEZE.read_text(encoding="utf-8"))
    gates={}
    for cid,row in freeze["conditions"].items():
        gates[f"{cid}_blob_bound"]=git_blob_sha(ROOT/row["artifact"])==row["git_blob_sha"]
    gates["protocol_bound"]=git_blob_sha(ROOT/freeze["protocol"]["path"])==freeze["protocol"]["git_blob_sha"]
    gates["analysis_plan_bound"]=git_blob_sha(ROOT/freeze["analysis_plan"]["path"])==freeze["analysis_plan"]["git_blob_sha"]
    gates["candidate_bound"]=git_blob_sha(ROOT/freeze["frozen_candidate"]["path"])==freeze["frozen_candidate"]["git_blob_sha"]
    gates["receipt_bound"]=git_blob_sha(ROOT/freeze["ownership_receipt"]["path"])==freeze["ownership_receipt"]["git_blob_sha"]

    dev=[json.loads(x) for x in (BENCH/"dev.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        blind=td/"blind.jsonl"
        blind.write_text("".join(json.dumps({"id":x["id"],"text":x["text"]},sort_keys=True)+"\n" for x in dev),encoding="utf-8")
        outputs={}
        for cid in "ABCD":
            outputs[cid]=execute(BENCH/f"condition_{cid.lower()}.py",blind,td/f"{cid}.jsonl")
    gates["A_equals_C_public"]=outputs["A"]==outputs["C"]
    gates["B_equals_D_public"]=outputs["B"]==outputs["D"]
    gates["all_ids_preserved"]=all([x["id"] for x in outputs[cid]]==[x["id"] for x in dev] for cid in "ABCD")
    gates["hidden_not_authored"]=freeze["hidden_split_authored"] is False and freeze["hidden_labels_exposed"] is False
    gates["no_post_exposure_repair"]=freeze["post_exposure_repair_allowed"] is False
    gates["promotion_authority_false"]=freeze["promotion_authority"] is False
    return {
      "schema":"Venus.EDU17R1ConditionFreezeAudit.v0.1",
      "status":"PASS_CONDITION_IMPLEMENTATIONS_PREFROZEN" if all(gates.values()) else "FAIL_CONDITION_IMPLEMENTATION_FREEZE",
      "gates":gates,
      "promotion_authority":False,
      "hidden_labels_exposed":False
    }

if __name__=="__main__":
    out=audit()
    print(json.dumps(out,indent=2,sort_keys=True))
    raise SystemExit(0 if out["status"].startswith("PASS_") else 1)
