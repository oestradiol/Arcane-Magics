from __future__ import annotations

"""Minimal local WorldMirror Console.

Default bind is loopback only. Process execution is disabled unless an explicit
process root and executable allowlist are supplied by the operator.

The server is an interaction surface, not the learner and not an authorization
root.
"""

import argparse
import base64
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kernel.runtime.interaction_store import InteractionStore
from kernel.runtime.process_bridge import ProcessBridge, ProcessBridgeError, ProcessPolicy


MAX_HTTP_BODY = 1_048_576


class ConsoleContext:
    def __init__(
        self,
        *,
        data_root: Path,
        static_root: Path,
        process_bridge: ProcessBridge | None,
    ):
        self.store = InteractionStore(data_root)
        self.static_root = static_root
        self.process_bridge = process_bridge

    def close(self) -> None:
        self.store.close()


class Handler(SimpleHTTPRequestHandler):
    server_version = "WorldMirrorConsole/0.1"

    @property
    def ctx(self) -> ConsoleContext:
        return self.server.ctx  # type: ignore[attr-defined]

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        rel = parsed.path.lstrip("/") or "index.html"
        candidate = (self.ctx.static_root / rel).resolve()
        try:
            candidate.relative_to(self.ctx.static_root.resolve())
        except ValueError:
            return str(self.ctx.static_root / "__invalid__")
        return str(candidate)

    def _json(self, status: int, payload: object) -> None:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _body(self, *, limit: int = MAX_HTTP_BODY) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0 or length > limit:
            raise ValueError("request body exceeds limit")
        return self.rfile.read(length)

    def _json_body(self) -> dict:
        raw = self._body()
        value = json.loads(raw.decode("utf-8") if raw else "{}")
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        return value

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            sessions = self.ctx.store.sessions(limit=1)
            self._json(
                HTTPStatus.OK,
                {
                    "schema": "Venus.WorldMirrorConsoleStatus.v0.1",
                    "process_bridge_enabled": self.ctx.process_bridge is not None,
                    "agent_backend_bound": False,
                    "fabricated_agent_reply": False,
                    "latest_session": sessions[0] if sessions else None,
                    "claim_fence": "console surface != learner != World truth != authorization",
                },
            )
            return

        if parsed.path == "/api/sessions":
            self._json(HTTPStatus.OK, {"sessions": self.ctx.store.sessions()})
            return

        if parsed.path == "/api/events":
            q = parse_qs(parsed.query)
            sid = (q.get("session_id") or [""])[0]
            if not sid:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "session_id required"})
                return
            events = [x.to_dict() for x in self.ctx.store.events(sid)]
            self._json(HTTPStatus.OK, {"session_id": sid, "events": events})
            return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/sessions":
                body = self._json_body()
                sid = self.ctx.store.create_session(title=str(body.get("title") or ""))
                self._json(HTTPStatus.CREATED, {"session_id": sid})
                return

            if parsed.path == "/api/raw":
                raw = self._body()
                sid = self.headers.get("X-WorldMirror-Session", "")
                actor = self.headers.get("X-WorldMirror-Actor", "human")
                kind = self.headers.get("X-WorldMirror-Kind", "CHAT_MESSAGE")
                parent = self.headers.get("X-WorldMirror-Parent") or None
                media = self.headers.get("Content-Type", "application/octet-stream").split(";", 1)[0]
                if not sid:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "X-WorldMirror-Session required"})
                    return
                event = self.ctx.store.append(
                    session_id=sid,
                    actor=actor,
                    kind=kind,
                    media_type=media,
                    raw=raw,
                    parent_event_id=parent,
                )
                self._json(HTTPStatus.CREATED, {"event": event.to_dict()})
                return

            if parsed.path == "/api/process":
                if self.ctx.process_bridge is None:
                    self._json(
                        HTTPStatus.FORBIDDEN,
                        {
                            "error": "process bridge disabled",
                            "note": "enable only inside an externally sandboxed environment",
                        },
                    )
                    return
                body = self._json_body()
                argv = body.get("argv")
                if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
                    raise ValueError("argv must be a list of strings")
                stdin = base64.b64decode(str(body.get("stdin_base64") or ""), validate=True)
                receipt, stdout, stderr = self.ctx.process_bridge.run(
                    argv,
                    cwd=body.get("cwd"),
                    stdin=stdin,
                    env=body.get("env") if isinstance(body.get("env"), dict) else None,
                )
                self._json(
                    HTTPStatus.OK,
                    {
                        "receipt": receipt.to_dict(),
                        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
                        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
                        "stdout_text": stdout.decode("utf-8", errors="replace"),
                        "stderr_text": stderr.decode("utf-8", errors="replace"),
                    },
                )
                return

            self._json(HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"})
        except (ValueError, KeyError, ProcessBridgeError, json.JSONDecodeError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def log_message(self, fmt: str, *args: object) -> None:
        print("[WorldMirror Console] " + (fmt % args))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the local WorldMirror Console")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--data-root", default=".worldmirror-console")
    p.add_argument("--process-root")
    p.add_argument("--allow-exec", action="append", default=[])
    p.add_argument("--process-timeout", type=float, default=15.0)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.process_root and not args.allow_exec:
        raise SystemExit("--process-root requires at least one --allow-exec")
    if args.allow_exec and not args.process_root:
        raise SystemExit("--allow-exec requires --process-root")

    bridge = None
    if args.process_root:
        policy = ProcessPolicy.build(
            args.process_root,
            allowed_executables=args.allow_exec,
            timeout_seconds=args.process_timeout,
        )
        bridge = ProcessBridge(policy)

    static_root = Path(__file__).resolve().parent / "static"
    ctx = ConsoleContext(
        data_root=Path(args.data_root),
        static_root=static_root,
        process_bridge=bridge,
    )
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.ctx = ctx  # type: ignore[attr-defined]
    print(f"WorldMirror Console: http://{args.host}:{args.port}")
    if bridge is None:
        print("Process bridge: disabled")
    else:
        print("Process bridge: enabled; this is not an OS sandbox")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        ctx.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
