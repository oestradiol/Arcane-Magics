from __future__ import annotations

"""External stdio cognitive-adapter protocol for WorldMirror Console.

The adapter is operator-configured transport. It receives a bounded JSON request
and may return one JSON reply. It is not tool authority, learner identity, or
independent evaluation.
"""

from dataclasses import dataclass
import json
import os
import subprocess
from typing import Any, Iterable


class AgentBridgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentBridge:
    argv: tuple[str, ...]
    timeout_seconds: float = 60.0
    max_response_bytes: int = 1_048_576

    @classmethod
    def build(
        cls,
        argv: Iterable[str],
        *,
        timeout_seconds: float = 60.0,
        max_response_bytes: int = 1_048_576,
    ) -> "AgentBridge":
        args = tuple(str(x) for x in argv)
        if not args:
            raise AgentBridgeError("agent argv cannot be empty")
        return cls(
            argv=args,
            timeout_seconds=float(timeout_seconds),
            max_response_bytes=int(max_response_bytes),
        )

    def reply(self, request: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(request, ensure_ascii=False, sort_keys=True).encode("utf-8")
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        try:
            cp = subprocess.run(
                self.argv,
                input=raw,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                shell=False,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentBridgeError("agent adapter timed out") from exc

        if cp.returncode != 0:
            detail = cp.stderr[:4096].decode("utf-8", errors="replace")
            raise AgentBridgeError(f"agent adapter failed ({cp.returncode}): {detail}")
        if len(cp.stdout) > self.max_response_bytes:
            raise AgentBridgeError("agent adapter response exceeds limit")

        try:
            value = json.loads(cp.stdout.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AgentBridgeError("agent adapter must return UTF-8 JSON") from exc
        if not isinstance(value, dict):
            raise AgentBridgeError("agent adapter JSON must be an object")
        text = value.get("text")
        if not isinstance(text, str) or not text:
            raise AgentBridgeError("agent adapter reply requires non-empty text")
        if "tool_calls" in value:
            raise AgentBridgeError("v0.1 agent protocol does not accept tool_calls")
        return {
            "text": text,
            "media_type": str(value.get("media_type") or "text/plain"),
            "metadata": value.get("metadata") if isinstance(value.get("metadata"), dict) else {},
        }


def request_from_events(
    *,
    session_id: str,
    trigger_event: dict[str, Any],
    recent_events: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": "Venus.WorldMirrorAgentRequest.v0.1",
        "session_id": session_id,
        "trigger_event": trigger_event,
        "recent_events": recent_events,
        "capabilities": {
            "reply_text": True,
            "tool_execution": False,
            "promotion_authority": False,
            "truth_authority": False,
            "independent_evaluation": False,
        },
    }
