# WorldMirror Console

**Status:** minimal local interaction surface for the Minerva / WorldMirror engineering body.

The console is deliberately small:

```text
chat / raw event ingress
+ chronological interaction history
+ state/event inspection
+ optional bounded process transport
```

It is **not** the learner itself, not a promotion surface, and not an OS security sandbox.

## Run

From the repository root:

```bash
python3 -m apps.worldmirror_console.server
```

Open:

```text
http://127.0.0.1:8765
```

Data is stored by default in:

```text
.worldmirror-console/
├── timeline.sqlite3
├── raw/
│   └── <sha-prefix>/<sha256>.bin
└── semantic/
    ├── index.sqlite3
    └── objects/
```

The raw carrier and the decoded/semantic view are separate.

```text
raw bytes
!= decoded text
!= interpretation
!= learned relation
```

## Process bridge

Process execution is **off by default**.

For a trusted executable inside an already externally sandboxed working tree:

```bash
python3 -m apps.worldmirror_console.server \
  --process-root /path/to/sandbox \
  --allow-exec python3 \
  --allow-exec git
```

The bridge enforces:

- no shell invocation;
- executable basename allowlist;
- working-directory confinement to the declared root;
- stdin size limit;
- timeout;
- captured stdout/stderr with digests and truncation metadata.

It does **not** restrict syscalls made by an allowed executable. A Python process can still access whatever the host OS grants it. Therefore:

```text
ProcessBridge
!= container
!= VM isolation
!= OS sandbox
```

For autonomous untrusted execution, put the whole console/process worker inside a real container/VM/OS sandbox and treat that external boundary as the hard substrate capability boundary.

## Agent/backend boundary

The console does not fabricate a machine reply when no cognitive backend is attached.

The HTTP event ingress can accept a machine-authored event from an external adapter:

```text
POST /api/raw
X-WorldMirror-Session: <session>
X-WorldMirror-Actor: machine
X-WorldMirror-Kind: CHAT_MESSAGE
Content-Type: text/plain
```

That adapter can later be a local model, a WorldMirror worker, or another bounded process. Keeping it external prevents the UI from silently becoming the cognition layer.

## Interaction development

See:

- `kernel/development/INTERACTION_DEVELOPMENT_CONTRACT.json`
- `kernel/development/WORLDMIRROR_CONSOLE_POLICY.json`

The intended developmental route is:

```text
interaction
→ retained raw carrier + chronology
→ reconstruct local Theater/KFS
→ identify residual
→ prefreeze proposed abstraction
→ later consequence
→ crystallize or reopen
→ source-remove scaffold
→ internalize only if earned
```

A chat log alone is not learning.
