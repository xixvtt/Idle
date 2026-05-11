"""Hook event → session state mapping."""

from __future__ import annotations

from .registry import (
    STATE_DONE,
    STATE_ERROR,
    STATE_IDLE,
    STATE_RUNNING,
    STATE_WAITING,
)


def map_event_to_state(event_type: str) -> str | None:
    """Return the new state for a given hook event_type, or None if unknown."""
    if event_type in ("PreToolUse", "PostToolUse"):
        return STATE_RUNNING
    if event_type == "PermissionRequest":
        return STATE_WAITING
    if event_type == "Stop":
        return STATE_DONE
    if event_type == "StopFailure":
        return STATE_ERROR
    return None


__all__ = [
    "map_event_to_state",
    "STATE_RUNNING",
    "STATE_IDLE",
    "STATE_WAITING",
    "STATE_DONE",
    "STATE_ERROR",
]
