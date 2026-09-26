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

### Automatic external agent adapter

A trusted local adapter can be bound explicitly:

```bash
python3 -m apps.worldmirror_console.server \
  --agent-command-json '["python3","/path/to/adapter.py"]'
```

The adapter receives one UTF-8 JSON object on stdin containing the triggering
event and recent interaction context. It must return one JSON object such as:

```json
{"text":"response text"}
```

The v0.1 protocol rejects `tool_calls`. The adapter gets no process-bridge
authority merely by being the conversational backend. Its reply is appended as a
normal raw `machine` event with the triggering event as parent.

Protocol: `kernel/development/WORLDMIRROR_AGENT_PROTOCOL.json`.

```text
agent adapter
!= learner identity
!= tool authority
!= independent evaluator
!= World truth
```

The external event ingress also remains available when no automatic adapter is bound.

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


## Action proposal boundary

Conversational authorship is kept separate from computer authority.

Machine-readable protocol:

`kernel/development/WORLDMIRROR_ACTION_PROPOSAL_PROTOCOL.json`

Generic inert carrier:

`kernel/runtime/action_proposal.py`

```text
learner / external agent
→ ActionProposal
→ external authorization or WITHHOLD
→ ProcessBridge
→ ProcessReceipt
→ later consequence
```

The proposal carrier cannot invoke `ProcessBridge` itself.

```text
PROPOSE != AUTHORIZE
AUTHORIZE != EXECUTE
EXECUTE != RETURN_SUCCESS
PROCESS_SUCCESS != CLAIM_VALIDATION
```

Issuer authentication and jurisdiction remain outside the proposal module. In a
future autonomous local deployment, authorization should be held by the outer
container/VM/capability boundary rather than by the learner process itself.
