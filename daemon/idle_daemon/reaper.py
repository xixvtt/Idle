"""Periodic health check — drops sessions whose owning process is gone or
that have been silent for too long."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Awaitable, Callable

import psutil

from .registry import SessionRegistry, STATE_IDLE, STATE_RUNNING

log = logging.getLogger(__name__)


IDLE_AFTER_S = 600       # 10 min silent while running → IDLE
DEAD_AFTER_S = 1800      # 30 min total silent → DEAD
TICK_S = 10


def _active_claude_cwds() -> set[str]:
    """Return cwds of currently running claude-code-like processes.

    We match by process name or command line containing 'claude'. Adjust if
    Claude Code rebrands its binary.
    """
    cwds: set[str] = set()
    for proc in psutil.process_iter(attrs=["name", "cmdline", "cwd"]):
        try:
            info = proc.info
            name = (info.get("name") or "").lower()
            cmdline = info.get("cmdline") or []
            cwd = info.get("cwd")
            joined = " ".join(cmdline).lower() if cmdline else ""
            if "claude" in name or "claude" in joined:
                if cwd:
                    cwds.add(cwd)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return cwds


async def run_reaper(
    registry: SessionRegistry,
    on_state_change: Callable[[str, str], Awaitable[None]],
    on_remove: Callable[[str], Awaitable[None]],
    tick_s: float = TICK_S,
) -> None:
    """Long-running task; call from the daemon main loop."""
    while True:
        try:
            await _tick(registry, on_state_change, on_remove)
        except Exception as e:
            log.exception("reaper tick failed: %s", e)
        await asyncio.sleep(tick_s)


async def _tick(
    registry: SessionRegistry,
    on_state_change: Callable[[str, str], Awaitable[None]],
    on_remove: Callable[[str], Awaitable[None]],
) -> None:
    """Death detection is silence-based.

    We intentionally do NOT try to map a session's workspace cwd to a process
    cwd: Claude Code's process cwd is wherever the user launched it, not the
    workspace path that appears in hook payloads. Those rarely match.
    Silence timeouts are the reliable signal.
    """
    now = time.time()
    any_claude_alive = len(_active_claude_cwds()) > 0

    for s in list(registry.all()):
        silent_for = now - s.last_event_at

        if silent_for > DEAD_AFTER_S:
            registry.remove(s.session_id)
            await on_remove(s.session_id)
            continue

        # If no claude process exists at all and session has been silent for a
        # short while, it's safe to drop. Avoids ghost sessions after `claude`
        # quits cleanly.
        if not any_claude_alive and silent_for > 60:
            registry.remove(s.session_id)
            await on_remove(s.session_id)
            continue

        if silent_for > IDLE_AFTER_S and s.state == STATE_RUNNING:
            s.state = STATE_IDLE
            await on_state_change(s.session_id, STATE_IDLE)
