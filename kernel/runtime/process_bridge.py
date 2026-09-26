from __future__ import annotations

"""Bounded process transport for WorldMirror.

This is an argv/cwd/size/timeout boundary, not an OS security sandbox.
Untrusted learner-controlled programs still require an external container/VM/
OS sandbox. The bridge never uses a shell.
"""

from dataclasses import asdict, dataclass
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Iterable


class ProcessBridgeError(ValueError):
    pass


@dataclass(frozen=True)
class ProcessPolicy:
    root: Path
    allowed_executables: frozenset[str]
    timeout_seconds: float = 15.0
    max_stdin_bytes: int = 262_144
    max_output_bytes: int = 1_048_576
    allowed_env: frozenset[str] = frozenset()

    @classmethod
    def build(
        cls,
        root: str | Path,
        *,
        allowed_executables: Iterable[str],
        timeout_seconds: float = 15.0,
        max_stdin_bytes: int = 262_144,
        max_output_bytes: int = 1_048_576,
        allowed_env: Iterable[str] = (),
    ) -> "ProcessPolicy":
        root_path = Path(root).resolve()
        root_path.mkdir(parents=True, exist_ok=True)
        allowed = frozenset(str(x) for x in allowed_executables)
        if any("/" in x or "\\" in x for x in allowed):
            raise ProcessBridgeError("allowed executables must be basenames")
        if not allowed:
            raise ProcessBridgeError("allowed_executables cannot be empty")
        return cls(
            root=root_path,
            allowed_executables=allowed,
            timeout_seconds=float(timeout_seconds),
            max_stdin_bytes=int(max_stdin_bytes),
            max_output_bytes=int(max_output_bytes),
            allowed_env=frozenset(str(x) for x in allowed_env),
        )


@dataclass(frozen=True)
class ProcessReceipt:
    argv: tuple[str, ...]
    cwd: str
    executable_path: str
    stdin_sha256: str
    stdout_sha256: str
    stderr_sha256: str
    stdout_bytes: int
    stderr_bytes: int
    stdout_truncated: bool
    stderr_truncated: bool
    exit_code: int | None
    timed_out: bool
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProcessBridge:
    def __init__(self, policy: ProcessPolicy):
        self.policy = policy

    def _cwd(self, cwd: str | Path | None) -> Path:
        target = self.policy.root if cwd in (None, "", ".") else (self.policy.root / str(cwd))
        resolved = target.resolve()
        try:
            resolved.relative_to(self.policy.root)
        except ValueError as exc:
            raise ProcessBridgeError("cwd escapes process root") from exc
        if not resolved.exists() or not resolved.is_dir():
            raise ProcessBridgeError("cwd must be an existing directory")
        return resolved

    def _executable(self, argv0: str) -> tuple[str, str]:
        if "/" in argv0 or "\\" in argv0:
            raise ProcessBridgeError("argv[0] must be an allowed executable basename")
        if argv0 not in self.policy.allowed_executables:
            raise ProcessBridgeError(f"executable not allowed: {argv0}")
        found = shutil.which(argv0)
        if found is None:
            raise ProcessBridgeError(f"executable unavailable: {argv0}")
        return argv0, str(Path(found).resolve())

    def run(
        self,
        argv: Iterable[str],
        *,
        cwd: str | Path | None = None,
        stdin: bytes = b"",
        env: dict[str, str] | None = None,
    ) -> tuple[ProcessReceipt, bytes, bytes]:
        args = tuple(str(x) for x in argv)
        if not args:
            raise ProcessBridgeError("argv cannot be empty")
        if len(stdin) > self.policy.max_stdin_bytes:
            raise ProcessBridgeError("stdin exceeds policy limit")

        _, executable_path = self._executable(args[0])
        resolved_cwd = self._cwd(cwd)

        child_env = {"PATH": os.environ.get("PATH", "")}
        for key, value in (env or {}).items():
            if key not in self.policy.allowed_env:
                raise ProcessBridgeError(f"environment key not allowed: {key}")
            child_env[key] = str(value)

        started = time.monotonic_ns()
        timed_out = False
        exit_code: int | None
        try:
            cp = subprocess.run(
                args,
                cwd=resolved_cwd,
                input=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=child_env,
                shell=False,
                timeout=self.policy.timeout_seconds,
                check=False,
            )
            stdout_raw, stderr_raw = cp.stdout, cp.stderr
            exit_code = int(cp.returncode)
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout_raw = bytes(exc.stdout or b"")
            stderr_raw = bytes(exc.stderr or b"")
            exit_code = None

        duration_ms = max(0, (time.monotonic_ns() - started) // 1_000_000)
        stdout = stdout_raw[: self.policy.max_output_bytes]
        stderr = stderr_raw[: self.policy.max_output_bytes]
        receipt = ProcessReceipt(
            argv=args,
            cwd=str(resolved_cwd),
            executable_path=executable_path,
            stdin_sha256=hashlib.sha256(stdin).hexdigest(),
            stdout_sha256=hashlib.sha256(stdout_raw).hexdigest(),
            stderr_sha256=hashlib.sha256(stderr_raw).hexdigest(),
            stdout_bytes=len(stdout_raw),
            stderr_bytes=len(stderr_raw),
            stdout_truncated=len(stdout_raw) > len(stdout),
            stderr_truncated=len(stderr_raw) > len(stderr),
            exit_code=exit_code,
            timed_out=timed_out,
            duration_ms=int(duration_ms),
        )
        return receipt, stdout, stderr
