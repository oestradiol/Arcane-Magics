from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json, re
from pathlib import Path
from typing import Any, Iterable, Mapping
from kernel.runtime.induced_policy import execute_tree
from kernel.runtime.vmk2 import digest
from kernel.development.autonomous_learning import METHODS, TargetBarrier

FORBIDDEN_OPERATIONS=frozenset({"MERGE_PR","RELEASE","PROMOTE_AUTHORITY","CLOSE_ISSUE","DELETE_HISTORY","CHANGE_BRANCH_PROTECTION","ACCESS_SECRETS","SELF_VALIDATE","MINT_RETURN","CHANGE_SAFETY_FLOOR","CHANGE_JURISDICTION"})
ALLOWED_OPERATIONS=("READ_REPOSITORY","READ_ISSUES","READ_PRS","RUN_TESTS","STUDY_TARGET","PROPOSE_PATCH","OPEN_DRAFT_PR","COMMENT_WITH_RECEIPT")
FEATURE_NAMES=tuple(f"x{i}" for i in range(8))

@dataclass(frozen=True)
class WorkItem:
    kind:str; number:int; title:str; state:str="OPEN"; draft:bool=False
    merge_state:str|None=None; updated_at:str|None=None; body:str=""
    has_comments:bool=False; has_labels:bool=False; ci_failed:bool=False; ci_pending:bool=False

@dataclass(frozen=True)
class AutonomousCycleReceipt:
    schema:str; cycle_id:str; target_kind:str|None; target_number:int|None; target_title:str|None
    decision:str; rationale:tuple[str,...]; feature_snapshot:Mapping[str,bool]
    study_method:str|None; study:Mapping[str,Any]|None; allowed_operations:tuple[str,...]
    forbidden_operations:tuple[str,...]; source_digest:str
    promotion_authority:bool=False; merge_authority:bool=False; release_authority:bool=False

def roadmap_issue_order(text:str)->tuple[int,...]:
    out=[]
    for m in re.finditer(r"#(\d+)",text):
        n=int(m.group(1))
        if n not in out: out.append(n)
    return tuple(out)

def _time(v):
    return None if not v else datetime.fromisoformat(v.replace("Z","+00:00"))

def item_features(item:WorkItem,*,now:datetime|None=None)->dict[str,bool]:
    now=now or datetime.now(timezone.utc); t=_time(item.updated_at)
    return {"x0":item.kind.upper()=="PR","x1":bool(item.draft),"x2":item.ci_failed,"x3":item.ci_pending,
            "x4":item.merge_state in {"DIRTY","BLOCKED","CONFLICTING"},"x5":item.has_comments,
            "x6":item.has_labels,"x7":bool(t and (now-t).total_seconds()<=604800)}

def _blocked(item,barriers):
    rows=tuple(b for b in barriers if b.kind==item.kind and b.number==item.number)
    if not rows:return False
    if any(b.cycle_state=="OPEN" for b in rows):return True
    it=_time(item.updated_at)
    if it is None:return True
    resolved=[_time(b.outcome_at) for b in rows if b.outcome_at]
    resolved=[x for x in resolved if x]
    return not resolved or it<=max(resolved)

def choose_target(items:Iterable[WorkItem],*,roadmap_text:str,target_barriers:Iterable[TargetBarrier]=(),
                  active_cycle:bool=False,recent_targets:Iterable[tuple[str,int]]=(),
                  kind_utility:Mapping[str,float]|None=None,feature_weights:Mapping[str,float]|None=None,
                  learner_state_id:str="")->WorkItem|None:
    _=roadmap_text
    if active_cycle:return None
    recent=set(recent_targets); barriers=tuple(target_barriers); ku=kind_utility or {}; fw=feature_weights or {}
    rows=tuple(i for i in items if i.state.upper()=="OPEN" and not i.ci_pending and
               (i.kind,i.number) not in recent and not _blocked(i,barriers) and
               not(i.kind=="PR" and i.title.lower().startswith("venus: autonomous cycle")))
    if not rows:return None
    def rank(i):
        conflict=0 if i.kind=="PR" and i.merge_state in {"DIRTY","BLOCKED","CONFLICTING"} else 1
        learned=float(ku.get(i.kind,0))+sum(float(fw.get(k,0)) for k,v in item_features(i).items() if v)
        tie=digest({"learner_state_id":learner_state_id,"target":[i.kind,i.number,i.title]})
        return (conflict,-learned,tie)
    return sorted(rows,key=rank)[0]

def _sentences(text): return tuple(x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+",text) if x.strip())

def choose_study_method(item:WorkItem,method_utility:Mapping[str,float]|None=None)->str:
    u=method_utility or {}
    return sorted(METHODS,key=lambda m:(-float(u.get(m,0)),digest({"target":[item.kind,item.number,item.title],"method":m})))[0]

def study_target(item:WorkItem,*,method:str)->dict[str,Any]:
    body=item.body or ""
    refs=tuple(dict.fromkeys(int(x) for x in re.findall(r"(?<!\w)#(\d+)",body) if int(x)!=item.number))
    paths=tuple(dict.fromkeys(x.rstrip(".,;:!?)]}") for x in re.findall(r"(?:kernel|tests|docs|evaluation|benchmarks|provenance|scripts)/[A-Za-z0-9_./-]+",body)))
    terms=("remaining","requires","required","blocked","blocking","pending","await","waiting","external return","hidden","withhold","stop","not yet","missing","open")
    blockers=tuple(s for s in _sentences(body) if any(t in s.lower() for t in terms))[:12]
    marks=tuple(sorted(set(x.lower() for x in re.findall(r"(?i)\b(ignore|override|bypass|disable|merge|promote|release|delete|exfiltrate|secret|token|password|system prompt)\b",body))))
    disposition="REPAIR_RETURNED_FAILURE" if item.ci_failed else ("REOPEN_STRUCTURAL_CONFLICT" if item.merge_state in {"DIRTY","BLOCKED","CONFLICTING"} else "PROBE")
    return {"body_digest":digest(body),"referenced_issue_or_pr_numbers":refs,"referenced_repository_paths":paths,
            "returned_blocker_sentences":blockers,"untrusted_instruction_markers":marks,"body_is_executable_instruction":False,
            "external_state":{"merge_state":item.merge_state,"ci_failed":item.ci_failed,"ci_pending":item.ci_pending,"has_comments":item.has_comments,"has_labels":item.has_labels},
            "disposition":disposition,"method":method,
            "questions":("What exact residual remains unresolved in the returned repository state?","What rival explanations or candidate dispositions remain live?","What fresh returned evidence would discriminate them?","Can a local repository change lawfully produce that discriminator, or must Venus WITHHOLD/STOP for external return?","What is the smallest implicated dependency that could be changed without altering a prefrozen claim object?"),
            "study_authority":"LEARNER_SIDE_RECONSTRUCTION_FROM_EXTERNAL_GITHUB_SNAPSHOT","promotion_authority":False}

def make_cycle(*,issues,prs,roadmap_text,internal_policy,target_barriers=(),active_cycle=False,recent_targets=(),
               kind_utility=None,feature_weights=None,learner_state_id="",method_utility=None,active_cycle_pending=False):
    items=tuple(issues)+tuple(prs)
    target=None if active_cycle_pending else choose_target(items,roadmap_text=roadmap_text,target_barriers=target_barriers,
        active_cycle=active_cycle,recent_targets=recent_targets,kind_utility=kind_utility,feature_weights=feature_weights,
        learner_state_id=learner_state_id)
    source={"items":[asdict(i) for i in items],"roadmap_digest_context_only":digest(roadmap_text),
            "target_barriers":[asdict(b) for b in target_barriers],"kind_utility":dict(kind_utility or {}),
            "feature_weights":dict(feature_weights or {}),"learner_state_id":learner_state_id,
            "method_utility":dict(method_utility or {}),"active_cycle_pending":active_cycle_pending}
    snapshot={}; method=None; study=None
    if active_cycle_pending:
        decision="STOP"; rationale=("an autonomous draft remains open awaiting external review/return","bounded autonomy may not route around a pending returned consequence")
    elif target is None:
        decision="STOP"; rationale=("no admissible OPEN work item remains after pending-return, reopening, and recurrence gates",)
    else:
        snapshot=item_features(target); method=choose_study_method(target,method_utility); study=study_target(target,method=method)
        pf={"f0":True,"f1":target.merge_state not in {"BLOCKED","CONFLICTING"},"f2":True,"f3":True,"f4":False,"f5":True,"f6":False,"f7":False}
        decision=execute_tree(internal_policy,pf)
        if decision=="ACT":decision="PROBE"
        rationale=("one bounded target selected from current external GitHub snapshot","internalized learner-side policy is upstream of work disposition","explicit external work-return reviews may alter later target ranking","roadmap is context/provenance only and has zero target-selection weight","selected target body is transformed into a bounded source-grounded study object","prior target study remains withheld until newer external target return reopens it","draft proposal only; admission remains external")
    body={"schema":"Venus.AutonomousCycleReceipt.v0.4","target_kind":target.kind if target else None,"target_number":target.number if target else None,
          "target_title":target.title if target else None,"decision":decision,"rationale":rationale,"feature_snapshot":dict(snapshot),
          "study_method":method,"study":study,"allowed_operations":ALLOWED_OPERATIONS,"forbidden_operations":tuple(sorted(FORBIDDEN_OPERATIONS)),
          "source_digest":digest(source),"promotion_authority":False,"merge_authority":False,"release_authority":False}
    return AutonomousCycleReceipt(cycle_id=digest(body),**body)

def load_work_items(path:str|Path,kind:str)->tuple[WorkItem,...]:
    rows=json.loads(Path(path).read_text(encoding="utf-8")); out=[]
    for row in rows:
        checks=row.get("statusCheckRollup") or []
        conc={str(x.get("conclusion") or "").upper() for x in checks if isinstance(x,Mapping)}
        stat={str(x.get("status") or "").upper() for x in checks if isinstance(x,Mapping)}
        out.append(WorkItem(kind=kind,number=int(row["number"]),title=str(row["title"]),state=str(row.get("state","OPEN")),
            draft=bool(row.get("isDraft",row.get("draft",False))),merge_state=row.get("mergeStateStatus",row.get("merge_state")),
            updated_at=row.get("updatedAt",row.get("updated_at")),body=str(row.get("body") or ""),has_comments=bool(row.get("comments")),
            has_labels=bool(row.get("labels")),ci_failed=any(x in {"FAILURE","CANCELLED","TIMED_OUT","ACTION_REQUIRED"} for x in conc),
            ci_pending=any(x in {"QUEUED","IN_PROGRESS","PENDING"} for x in stat)))
    return tuple(out)
