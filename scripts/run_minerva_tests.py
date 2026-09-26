from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests"
SCOPE = ROOT / "kernel/development/MINERVA_TEST_SCOPE.json"

def main() -> int:
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    excluded = {row["path"] for row in scope["excluded"]}
    existing = {p.relative_to(ROOT).as_posix() for p in TEST_DIR.glob("test_*.py")}

    missing = excluded - existing
    if missing:
        raise SystemExit(f"declared exclusions missing from branch: {sorted(missing)}")

    selected = sorted(existing - excluded)
    if not selected:
        raise SystemExit("no Minerva tests selected")

    print(f"Minerva branch-local tests: {len(selected)} selected, {len(excluded)} jurisdiction-excluded")
    for rel in selected:
        print(f"\n=== {rel} ===", flush=True)
        cp = subprocess.run([sys.executable, "-m", "unittest", rel], cwd=ROOT)
        if cp.returncode != 0:
            return cp.returncode
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
