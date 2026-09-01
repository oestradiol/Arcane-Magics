# Environment Entry Protocol

## For Agents and Automation

### Quick Path (when .venv exists)

```bash
# From Research/tools/ directory
./.venv/bin/python -m research_tools validate all

# From Research/ root
cd tools && ./.venv/bin/python -m research_tools validate all
```

### Full Setup (when .venv missing or stale)

```bash
cd Research/tools
nix develop
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-build-isolation -e .[dev]
```

## Environment Architecture

| Layer | Purpose | Location |
|-------|---------|----------|
| Nix | Base toolchain (Python 3.12, ruff, pytest) | `flake.nix` in tools/ |
| venv | Package environment with editable install | `tools/.venv/` |
| research_tools | Importable Python package | `tools/src/research_tools/` |

## Known Constraints

- No `flake.nix` at Research/ root — must enter tools/ first
- No system `python3` on NixOS hosts
- venv Python at `tools/.venv/bin/python` is the canonical interpreter
- The `research-tools` CLI is only available after editable install

## Agent Entry Rule

When entering from cold start without prior context:
1. Check for `tools/.venv/bin/python`
2. If exists: use direct path invocation
3. If missing: run full Nix+venv setup before any validation

## Status

`environment entry documentation`
