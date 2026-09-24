#!/usr/bin/env python3
from __future__ import annotations

import hashlib, ipaddress, json, os, socket, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.environ.get("VENUS_MODEL", "openai/gpt-4.1")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ENDPOINT = "https://models.github.ai/inference/chat/completions"


def die(msg: str) -> None:
    raise SystemExit(msg)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def github_model(messages, temperature: float = 0.2):
    if not TOKEN:
        die("GITHUB_TOKEN missing")
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "venus-minerva-worker",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            obj = json.load(response)
        return json.loads(obj["choices"][0]["message"]["content"])
    except Exception as exc:
        die(f"GitHub Models call failed or returned invalid JSON: {exc}")


def safe_repo_path(path: str) -> Path:
    p = (ROOT / path).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError("path escapes repository")
    return p


def read_text(path: str) -> str:
    return safe_repo_path(path).read_text(encoding="utf-8")


def search_repo(term: str, limit: int = 20):
    needle = term.lower()
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            if p.stat().st_size > 2_000_000:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(p.relative_to(ROOT))
        low = text.lower()
        if needle in low or needle in rel.lower():
            i = low.find(needle)
            excerpt = text[max(0, i - 500): i + 1400] if i >= 0 else text[:1200]
            hits.append({"path": rel, "excerpt": excerpt})
            if len(hits) >= limit:
                break
    return hits


def bounded_fetch(url: str, max_bytes: int = 300_000) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("only https URLs are allowed")
    for info in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM):
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError("private/reserved network target blocked")
    req = urllib.request.Request(url, headers={"User-Agent": "venus-minerva-worker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("response exceeds bounded fetch limit")
        ctype = response.headers.get("content-type", "")
        if not any(kind in ctype for kind in ("text/", "json", "xml")):
            raise ValueError(f"non-text content blocked: {ctype}")
        return data.decode("utf-8", errors="replace")


def repo_context():
    files = [
        "prototype/CURRENT_STATE.md",
        "REPOSITORY_AUTHORITY_BOUNDARY.md",
        "PUBLICATION_CONSTITUTION.md",
        "docs/FRONTIER_RESEARCH.md",
        "docs/AUTONOMOUS_RESEARCH.md",
    ]
    return {path: read_text(path) if safe_repo_path(path).exists() else "" for path in files}


def selection_messages(context, issues, recent_return):
    system = (
        "You are the bounded Venus-Minerva research selector. Choose at most one next research episode. "
        "You may select an existing issue, propose one new bounded issue only if an earned residual is absent, or STOP. "
        "You have no external research tools in this phase. Preserve claim modality and fail closed. "
        "Return JSON with keys action, selected_issue_number, lane, slug, title, prefreeze_markdown, new_issue_body. "
        "action must be SELECT_EXISTING, PROPOSE_NEW, or STOP. prefreeze_markdown must contain parent/authority, frozen question, "
        "register, rivals/hypothesis where relevant, admitted evidence/tools, discriminator, PASS/FAIL/WITHHOLD conditions, and claim fence."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps({"context": context, "issues": issues, "recent_return": recent_return})},
    ]


def research_messages(prefreeze, context):
    system = (
        "You are the bounded Venus-Minerva research worker. The preregistration below is frozen and must not be rewritten. "
        "You may request bounded tools iteratively. Return JSON only. If more information is needed use action TOOL with tool and args. "
        "Allowed tools: READ_FILE, SEARCH_REPO, FETCH_HTTPS. When enough evidence exists use action FINAL and return outcome, "
        "result_markdown, evidence_log, next_issue_proposal. Valid outcomes: PASS_BOUNDED, FAIL, WITHHOLD, MATURE_REDUCTION, PARTIAL. "
        "Never promote theorem/SOTA/AGI/physics/consciousness by self-assertion."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps({"prefreeze": prefreeze, "context": context})},
    ]


def run_research(prefreeze: str, context, max_steps: int = 8):
    messages = research_messages(prefreeze, context)
    evidence = []
    for _ in range(max_steps):
        obj = github_model(messages)
        if obj.get("action") == "FINAL":
            obj.setdefault("evidence_log", evidence)
            return obj
        if obj.get("action") != "TOOL":
            die(f"unexpected research action: {obj}")
        name = obj.get("tool")
        args = obj.get("args") or {}
        try:
            if name == "READ_FILE":
                result = read_text(args["path"])[:200_000]
            elif name == "SEARCH_REPO":
                result = search_repo(args["term"], int(args.get("limit", 20)))
            elif name == "FETCH_HTTPS":
                result = bounded_fetch(args["url"])
            else:
                raise ValueError("tool not allowed")
            record = {"tool": name, "args": args, "ok": True, "result_digest": sha256_text(json.dumps(result, sort_keys=True, default=str))}
            tool_return = {"ok": True, "tool": name, "args": args, "result": result}
        except Exception as exc:
            record = {"tool": name, "args": args, "ok": False, "error": str(exc)}
            tool_return = record
        evidence.append(record)
        messages.append({"role": "assistant", "content": json.dumps(obj)})
        messages.append({"role": "user", "content": json.dumps({"tool_return": tool_return})})
    return {
        "action": "FINAL",
        "outcome": "WITHHOLD",
        "result_markdown": "# Result\n\nWITHHOLD: bounded tool/step budget exhausted before the frozen discriminator could be resolved.\n",
        "evidence_log": evidence,
        "next_issue_proposal": "",
    }


def main():
    if len(sys.argv) < 2:
        die("usage: venus_worker.py select|research ...")
    cmd = sys.argv[1]
    if cmd == "select":
        issues_path, return_path, out_path = map(Path, sys.argv[2:5])
        issues = json.loads(issues_path.read_text(encoding="utf-8"))
        recent = json.loads(return_path.read_text(encoding="utf-8")) if return_path.exists() else {}
        obj = github_model(selection_messages(repo_context(), issues, recent))
        if obj.get("action") not in {"SELECT_EXISTING", "PROPOSE_NEW", "STOP"}:
            die(f"invalid selection action: {obj}")
        out_path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    elif cmd == "research":
        prefreeze_path, out_path = map(Path, sys.argv[2:4])
        result = run_research(prefreeze_path.read_text(encoding="utf-8"), repo_context())
        out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        die(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
