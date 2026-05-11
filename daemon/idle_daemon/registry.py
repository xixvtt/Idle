"""SessionRegistry: in-memory state for all known Claude Code sessions.

A session is registered the first time a hook event references its session_id.
Sessions are removed when their underlying process is gone or after a long
period of silence.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Iterator


STATE_RUNNING = "RUNNING"
STATE_IDLE = "IDLE"
STATE_WAITING = "WAITING"
STATE_DONE = "DONE"
STATE_ERROR = "ERROR"


@dataclass
class SessionState:
    session_id: str
    cwd: str
    transcript_path: str
    state: str = STATE_IDLE
    tokens: int = 0
    last_delta: int = 0
    byte_offset: int = 0
    created_at: float = field(default_factory=time.time)
    last_event_at: float = field(default_factory=time.time)
    started_at: float | None = None  # for DONE duration calc

    @property
    def display_name(self) -> str:
        cwd = self.cwd.rstrip("/")
        if not cwd:
            return ""
        parent, base = os.path.split(cwd)
        gp_name = os.path.basename(parent)
        if gp_name and gp_name not in ("/", "Users"):
            return f"{gp_name}/{base}"
        return base or cwd

    def to_dict(self, include_tokens: bool = True) -> dict:
        d = {
            "session_id": self.session_id,
            "cwd": self.display_name,
            "state": self.state,
        }
        if include_tokens:
            d["tokens"] = self.tokens
        return d


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._today_tokens: int = 0
        self._today_date: str = self._today()

    @staticmethod
    def _today() -> str:
        return time.strftime("%Y-%m-%d")

    @staticmethod
    def tz_name() -> str:
        # E.g. ("PST", "PDT") -> pick the active one.
        idx = time.localtime().tm_isdst
        return time.tzname[idx] if idx >= 0 else time.tzname[0]

    def _maybe_roll_day(self) -> None:
        today = self._today()
        if today != self._today_date:
            self._today_date = today
            self._today_tokens = 0

    @property
    def today_tokens(self) -> int:
        self._maybe_roll_day()
        return self._today_tokens

    @property
    def today_date(self) -> str:
        return self._today_date

    def restore_today(self, date: str, tokens: int) -> None:
        if date == self._today():
            self._today_date = date
            self._today_tokens = tokens

    def set_today_tokens(self, tokens: int) -> None:
        """Set the day's ground-truth total (e.g. from filesystem scan)."""
        self._maybe_roll_day()
        self._today_tokens = tokens

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def all(self) -> list[SessionState]:
        return list(self._sessions.values())

    def __iter__(self) -> Iterator[SessionState]:
        return iter(self._sessions.values())

    def register(
        self,
        session_id: str,
        cwd: str,
        transcript_path: str,
    ) -> tuple[SessionState, bool]:
        """Return (session, is_new)."""
        existing = self._sessions.get(session_id)
        if existing:
            return existing, False
        s = SessionState(
            session_id=session_id,
            cwd=cwd,
            transcript_path=transcript_path,
        )
        self._sessions[session_id] = s
        return s, True

    def remove(self, session_id: str) -> SessionState | None:
        return self._sessions.pop(session_id, None)

    def add_tokens(self, session_id: str, delta: int) -> None:
        """Update per-session running total. today_tokens is owned by the
        filesystem scanner (see scanner.scan_today_total) — do NOT modify it
        from hooks, or it will double-count with the bootstrap scan."""
        s = self._sessions.get(session_id)
        if not s:
            return
        s.tokens += delta
        s.last_delta = delta
        self._maybe_roll_day()

    def touch(self, session_id: str) -> None:
        s = self._sessions.get(session_id)
        if s:
            s.last_event_at = time.time()
