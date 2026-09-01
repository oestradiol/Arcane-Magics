from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    doctor = subprocess.run([sys.executable, str(BASE / 'package_doctor.py')], capture_output=True, text=True)
    print(doctor.stdout)
    if doctor.returncode != 0:
        print('LAUNCH GATE: FAIL')
        print('Do not treat the repository as current-operated until package_doctor.py passes.')
        sys.exit(1)

    cfg = json.loads((BASE / 'governance' / 'AUTHORITATIVE_SOURCES_v0_2.json').read_text(encoding='utf-8'))
    package_entrypoints = [BASE / rel for rel in cfg['package_entrypoints'].values()]
    required = [BASE / rel for rel in cfg['root_entrypoints']] + package_entrypoints
    missing = [str(p.relative_to(BASE)) for p in required if not p.exists()]
    if missing:
        print('LAUNCH GATE: FAIL')
        print('Missing current entrypoint artifacts:', ', '.join(missing))
        sys.exit(1)

    print('LAUNCH GATE: PASS')
    print('Current repository entrypoints and package entrypoints are present, integrity manifests pass, and current-surface / file-registry / claim / minimality audits passed through package_doctor.py.')
    print('This launch gate demonstrates bounded repository coherence and current operational readiness. It does not by itself validate scientific claims or broader empirical truth.')
    sys.exit(0)


if __name__ == '__main__':
    main()
