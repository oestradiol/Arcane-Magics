from __future__ import annotations

"""Bounded external GitHub-network adapter for learner-authored Web study.

The learner supplies only a frozen NetworkQuery object. This adapter:
- sends query terms only as URL-encoded parameters to fixed GitHub Search API endpoints;
- never executes returned text;
- never follows returned URLs;
- returns inert ENCOUNTER_RETURN source records;
- prefers distinct repository centers and records their indexed identity.

It is transport/execution substrate, not learner semantics, evaluator, truth authority,
promotion authority, or jurisdiction.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ORIGIN = "https://api.github.com"
ADAPTER_ID = "GITHUB_PUBLIC_NETWORK_ADAPTER_V1"
CURRENT_REPOSITORY = "oestradiol/Arcane-Magics"

_STOP = frozenset({
    "the","and","for","with","from","into","that","this","then","than","under",
    "over","without","within","resolve","generalize","revise","fresh","returned",
    "return","current","problem","residual","policy","missing","available",
})


class GitHubNetworkAdapterError(ValueError):
    pass


def _tokens(text: str) -> tuple[str, ...]:
    out=[]
    for token in re.findall(r"[A-Za-z0-9_.-]+", text.lower()):
        if len(token) < 3 or token in _STOP:
            continue
        if token not in out:
            out.append(token)
    return tuple(out)


def query_variants(
    query_text: str,
    *,
    study_anchors: Iterable[str] = (),
) -> tuple[str, ...]:
    """Deterministic bounded relaxation that preserves selected-study custody.

    Without selected-study anchors, retain the legacy generic relaxation.
    With anchors, never relax below the bounded anchor core: broad one-token
    searches are not an admissible substitute for the learner's selected topic.
    """
    tokens=_tokens(query_text)
    if not tokens:
        raise GitHubNetworkAdapterError("learner query has no searchable tokens")
    anchors=_tokens(" ".join(str(x) for x in study_anchors))
    variants=[]
    if anchors:
        core=anchors[:min(3,len(anchors))]
        widths=(min(8,len(tokens)), min(6,len(tokens)), min(4,len(tokens)))
        for width in widths:
            if width <= 0:
                continue
            chosen=list(core)
            for token in tokens:
                if token not in chosen:
                    chosen.append(token)
                if len(chosen) >= max(width,len(core)):
                    break
            candidate=" ".join(chosen)
            if candidate and candidate not in variants:
                variants.append(candidate)
        candidate=" ".join(core)
        if candidate and candidate not in variants:
            variants.append(candidate)
        return tuple(variants)

    for width in (min(6,len(tokens)), min(4,len(tokens)), min(2,len(tokens)), 1):
        if width <= 0:
            continue
        candidate=" ".join(tokens[:width])
        if candidate and candidate not in variants:
            variants.append(candidate)
    return tuple(variants)


def _request_json(path: str, params: dict[str, str], token: str) -> dict[str, Any]:
    if not path.startswith("/search/"):
        raise GitHubNetworkAdapterError("adapter path must remain fixed GitHub search surface")
    url=API_ORIGIN + path + "?" + urlencode(params)
    headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"Arcane-Magics-Minerva-Network-Adapter",
        "X-GitHub-Api-Version":"2022-11-28",
    }
    if token:
        headers["Authorization"]=f"Bearer {token}"
    req=Request(url,headers=headers,method="GET")
    with urlopen(req,timeout=20) as response:
        if response.status != 200:
            raise GitHubNetworkAdapterError(f"GitHub search returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _issue_center(item: dict[str, Any]) -> str:
    repo_url=str(item.get("repository_url") or "")
    marker="/repos/"
    return repo_url.split(marker,1)[1] if marker in repo_url else ""


def _repo_center(item: dict[str, Any]) -> str:
    return str(item.get("full_name") or "")


def _clean(text: object, limit: int = 1200) -> str:
    value=re.sub(r"\s+"," ",str(text or "")).strip()
    return value[:limit]


def collect_sources(
    *,
    issue_payloads: Iterable[dict[str, Any]],
    repo_payloads: Iterable[dict[str, Any]],
    max_sources: int = 6,
    current_repository: str = CURRENT_REPOSITORY,
    relevance_terms: Iterable[str] = (),
    min_relevance_matches: int = 0,
) -> tuple[dict[str, Any], ...]:
    """Pure reducer used by tests; keep at most one returned source per center."""
    candidates=[]
    for payload in issue_payloads:
        for item in payload.get("items",()):
            center=_issue_center(item)
            if not center:
                continue
            user=item.get("user") or {}
            author_login=str(user.get("login") or "")
            candidates.append({
                "source_id":f"github-issue:{center}#{item.get('number')}",
                "center_id":f"github-repo:{center}",
                "author_id":f"github-user:{author_login}" if author_login else "",
                "author_login":author_login,
                "author_type":str(user.get("type") or ""),
                "author_association":str(item.get("author_association") or ""),
                "artifact_authored":bool(author_login),
                "learner_minted_artifact":False,
                "source_url":str(item.get("html_url") or ""),
                "source_date":str(item.get("updated_at") or item.get("created_at") or ""),
                "title":_clean(item.get("title")),
                "observed_relation":_clean(item.get("body") or item.get("title")),
                "source_class":"GITHUB_PUBLIC_ISSUE",
                "current_repository":center == current_repository,
            })
    for payload in repo_payloads:
        for item in payload.get("items",()):
            center=_repo_center(item)
            if not center:
                continue
            owner=item.get("owner") or {}
            owner_login=str(owner.get("login") or "")
            candidates.append({
                "source_id":f"github-repository:{center}",
                "center_id":f"github-repo:{center}",
                "author_id":f"github-user:{owner_login}" if owner_login else "",
                "author_login":owner_login,
                "author_type":str(owner.get("type") or ""),
                "author_association":"REPOSITORY_OWNER",
                "artifact_authored":bool(owner_login),
                "learner_minted_artifact":False,
                "source_url":str(item.get("html_url") or ""),
                "source_date":str(item.get("updated_at") or item.get("created_at") or ""),
                "title":_clean(item.get("full_name") or item.get("name")),
                "observed_relation":_clean(item.get("description") or item.get("full_name")),
                "source_class":"GITHUB_PUBLIC_REPOSITORY",
                "current_repository":center == current_repository,
            })

    relevance=tuple(_tokens(" ".join(str(x) for x in relevance_terms)))
    admitted=[]
    for row in candidates:
        haystack=set(_tokens(f'{row["title"]} {row["observed_relation"]}'))
        matched=tuple(term for term in relevance if term in haystack)
        row={**row,"relevance_matches":matched}
        if relevance and len(matched) < min_relevance_matches:
            continue
        admitted.append(row)

    # Prefer external centers while preserving GitHub/API encounter order.
    ordered=(
        [row for row in admitted if not row["current_repository"]]
        + [row for row in admitted if row["current_repository"]]
    )
    seen=set()
    selected=[]
    for row in ordered:
        center=row["center_id"]
        if center in seen or not row["source_url"]:
            continue
        seen.add(center)
        selected.append(row)
        if len(selected) >= max_sources:
            break
    return tuple(selected)


def execute(query: dict[str, Any], *, max_sources: int = 6) -> dict[str, Any]:
    if query.get("schema") != "Venus.NetworkQuery.v0.1":
        raise GitHubNetworkAdapterError("unsupported network query schema")
    if query.get("authorship") not in {
        "LEARNER_DERIVED_FROM_FORMED_PROBLEM",
        "LEARNER_DERIVED_FROM_SELECTED_STUDY",
        "LEARNER_DERIVED_FROM_NETWORK_RECONSTRUCTION",
    }:
        raise GitHubNetworkAdapterError("query must be learner-derived")
    if query.get("execution_owner") != "EXTERNAL_ADAPTER":
        raise GitHubNetworkAdapterError("query execution owner must remain external")
    if query.get("promotion_authority") is not False or query.get("truth_authority") is not False:
        raise GitHubNetworkAdapterError("query may not carry truth/promotion authority")

    token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    study_anchors=tuple(str(x) for x in query.get("study_terms",()) if str(x).strip())
    required_relevance_matches=(
        3 if len(study_anchors) >= 6
        else 2 if len(study_anchors) >= 3
        else 1 if study_anchors
        else 0
    )
    variants=query_variants(
        str(query.get("query_text") or ""),
        study_anchors=study_anchors,
    )
    issue_payloads=[]
    repo_payloads=[]
    attempted=[]
    sources=()

    for variant in variants:
        attempted.append(variant)
        issue_payloads.append(_request_json(
            "/search/issues",
            {"q":variant,"sort":"updated","order":"desc","per_page":"20"},
            token,
        ))
        repo_payloads.append(_request_json(
            "/search/repositories",
            {"q":variant,"sort":"updated","order":"desc","per_page":"20"},
            token,
        ))
        sources=collect_sources(
            issue_payloads=issue_payloads,
            repo_payloads=repo_payloads,
            max_sources=max_sources,
            relevance_terms=study_anchors,
            min_relevance_matches=required_relevance_matches,
        )
        external_centers={x["center_id"] for x in sources if not x["current_repository"]}
        if len(external_centers) >= 2:
            break

    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    centers=tuple(sorted({x["center_id"] for x in sources}))
    external_centers=tuple(sorted({x["center_id"] for x in sources if not x["current_repository"]}))
    return {
        "schema":"Venus.GitHubNetworkEncounter.v0.1",
        "status":"ENCOUNTER_RETURN_AVAILABLE" if sources else "WITHHOLD_NO_INDEXED_SOURCES",
        "query_id":str(query["query_id"]),
        "adapter_id":ADAPTER_ID,
        "adapter_origin":API_ORIGIN,
        "retrieved_at":now,
        "return_class":"ENCOUNTER_RETURN",
        "independent_evaluative_return":False,
        "truth_authority":False,
        "promotion_authority":False,
        "query_text_executed_as_shell":False,
        "returned_text_executed":False,
        "returned_urls_followed":False,
        "search_variants":list(attempted),
        "selected_study_relevance_terms":list(study_anchors),
        "required_relevance_matches":required_relevance_matches,
        "relevance_filter_applied":bool(study_anchors),
        "indexed_center_ids":list(centers),
        "external_center_ids":list(external_centers),
        "multiple_external_centers":len(external_centers) >= 2,
        "sources":[
            {k:v for k,v in row.items() if k != "current_repository"}
            for row in sources
        ],
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--query",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--max-sources",type=int,default=6)
    args=p.parse_args()
    if args.max_sources < 1 or args.max_sources > 12:
        raise SystemExit("--max-sources must be between 1 and 12")
    query=json.loads(Path(args.query).read_text(encoding="utf-8"))
    result=execute(query,max_sources=args.max_sources)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
