#!/usr/bin/env python3
"""Structural auditor for the recursive node architecture.

Checks the declared node graph against the tracked tree. It validates
structure, never content: a pass says the declaration is well formed and the
circulation closes, not that the structure is the right one.

  N1 COVERAGE       every tracked path lies in exactly one node scope
  N2 BOUNDARY       every node declares a non-empty boundary
  N3 REOPENING      every node and residual names a reopening condition
  N4 ACYCLIC        parent links form a tree rooted at the single root node
  N5 REACHABLE      every unclosed residual is reachable from root
  N6 NON_SOVEREIGN  no node's scope lies inside a sibling's scope
  N7 RETURN_CLOSED  root residuals cover the union of descendant residuals

See docs/RECURSIVE_NODE_ARCHITECTURE.md.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "NODE_GRAPH.json"


def tracked_paths() -> list[str]:
    cp = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip())
    return [line for line in cp.stdout.splitlines() if line.strip()]


def covers(scope: str, path: str) -> bool:
    if scope.endswith("/"):
        return path.startswith(scope)
    return path == scope


def main() -> int:
    if not GRAPH_PATH.exists():
        print("WITHHOLD: NODE_GRAPH.json is absent")
        return 2
    try:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WITHHOLD: NODE_GRAPH.json does not parse: {exc}")
        return 2

    nodes = graph.get("nodes", [])
    if not nodes:
        print("WITHHOLD: graph declares no nodes")
        return 2

    by_id = {n["id"]: n for n in nodes}
    errors: list[str] = []

    if len(by_id) != len(nodes):
        errors.append("N4 ACYCLIC: duplicate node ids")

    # N4 — single root, parents resolve, no cycles
    roots = [n["id"] for n in nodes if n.get("parent") is None]
    if len(roots) != 1:
        errors.append(f"N4 ACYCLIC: expected exactly one root node, found {roots}")
    for node in nodes:
        parent = node.get("parent")
        if parent is not None and parent not in by_id:
            errors.append(f"N4 ACYCLIC: {node['id']} names unknown parent {parent}")
    for node in nodes:
        seen, cursor = set(), node["id"]
        while cursor is not None:
            if cursor in seen:
                errors.append(f"N4 ACYCLIC: cycle through {node['id']}")
                break
            seen.add(cursor)
            cursor = by_id.get(cursor, {}).get("parent")

    # N2 — non-empty boundary (difference without exile)
    for node in nodes:
        if not node.get("boundary"):
            errors.append(f"N2 BOUNDARY: {node['id']} declares no boundary")

    # N3 — reopening conditions (meaning without closure)
    for node in nodes:
        residuals = node.get("residuals", [])
        if not residuals and not node.get("residuals_absence_justification"):
            errors.append(
                f"N3 REOPENING: {node['id']} declares no residuals and no "
                f"justification for their absence"
            )
        for res in residuals:
            if not res.get("reopening_condition", "").strip():
                errors.append(
                    f"N3 REOPENING: {node['id']}/{res.get('id')} has no "
                    f"reopening condition"
                )
            if not res.get("statement", "").strip():
                errors.append(f"N3 REOPENING: {node['id']}/{res.get('id')} has no statement")

    # N6 — no node scope nested inside a non-ancestor's scope
    def is_ancestor(maybe: str, node_id: str) -> bool:
        # Guarded against cycles: a malformed graph must make this auditor
        # report, not hang. An auditor that loops forever on bad input is
        # indistinguishable from one that passes it.
        cursor = by_id.get(node_id, {}).get("parent")
        seen: set[str] = {node_id}
        while cursor is not None and cursor not in seen:
            if cursor == maybe:
                return True
            seen.add(cursor)
            cursor = by_id.get(cursor, {}).get("parent")
        return False

    for a in nodes:
        for b in nodes:
            if a["id"] == b["id"]:
                continue
            for sa in a.get("scope", []):
                for sb in b.get("scope", []):
                    if sa == sb:
                        errors.append(
                            f"N6 NON_SOVEREIGN: {a['id']} and {b['id']} both claim {sa}"
                        )
                    elif sb.endswith("/") and sa.startswith(sb):
                        if not is_ancestor(b["id"], a["id"]):
                            errors.append(
                                f"N6 NON_SOVEREIGN: {a['id']} scope {sa} lies inside "
                                f"non-ancestor {b['id']} scope {sb}"
                            )

    # N1 — coverage: every tracked path in exactly one node
    try:
        paths = tracked_paths()
    except RuntimeError as exc:
        print(f"WITHHOLD: cannot list tracked files: {exc}")
        return 2

    uncovered: list[str] = []
    for path in paths:
        owners = [n["id"] for n in nodes if any(covers(s, path) for s in n.get("scope", []))]
        if not owners:
            uncovered.append(path)
        elif len(owners) > 1:
            errors.append(f"N1 COVERAGE: {path} claimed by {owners}")
    if uncovered:
        shown = ", ".join(uncovered[:8])
        more = f" (+{len(uncovered) - 8} more)" if len(uncovered) > 8 else ""
        errors.append(f"N1 COVERAGE: {len(uncovered)} tracked paths in no node: {shown}{more}")

    # N5 / N7 — residual reachability and return closure
    root_id = roots[0] if len(roots) == 1 else None
    descendant_residuals: set[str] = set()
    for node in nodes:
        if node["id"] == root_id:
            continue
        for res in node.get("residuals", []):
            rid = res.get("id")
            if rid:
                descendant_residuals.add(rid)
                if not is_ancestor(root_id, node["id"]) and node["id"] != root_id:
                    errors.append(
                        f"N5 REACHABLE: residual {rid} sits on {node['id']}, "
                        f"which is not reachable from root"
                    )

    # N7 — the return must actually close.
    #
    # An earlier version accepted any root residual containing the word "union",
    # which an adversarial reviewer defeated with the literal string "union";
    # descendant_residuals was computed and never compared to anything. The root
    # must now enumerate the descendant residual ids it carries, and that
    # enumeration must equal the real set. Leaves feed the first root, or the
    # sixth-order loop is decoration.
    root_node = by_id.get(root_id, {})
    claimed = set(root_node.get("aggregates_residuals", []))
    missing = sorted(descendant_residuals - claimed)
    phantom = sorted(claimed - descendant_residuals)
    if missing:
        errors.append(
            f"N7 RETURN_CLOSED: root does not account for descendant residual(s) "
            f"{missing}; the sixth-order return does not close"
        )
    if phantom:
        errors.append(
            f"N7 RETURN_CLOSED: root claims residual(s) {phantom} that no "
            f"descendant declares"
        )

    if errors:
        print(f"NODE GRAPH AUDIT FINDINGS ({len(errors)})")
        for item in errors:
            print(f"  {item}")
        return 1

    leaves = [n["id"] for n in nodes if not any(m.get("parent") == n["id"] for m in nodes)]
    print(
        f"NODE GRAPH AUDIT PASS ({len(nodes)} nodes; {len(leaves)} leaves; "
        f"{len(paths)} tracked paths covered; "
        f"{len(descendant_residuals)} descendant residuals reachable)"
    )
    print("Structural conformance is not correctness: NODE_GRAPH_VALID != STRUCTURE_IS_RIGHT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
