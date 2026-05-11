"""Daemon state persistence to ~/.idle/state.json."""

from __future__ import annotations

import json
import os
from pathlib import Path


def _state_dir() -> Path:
    p = Path.home() / ".idle"
    p.mkdir(exist_ok=True)
    return p


def state_path() -> Path:
    return _state_dir() / "state.json"


def load() -> dict:
    p = state_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save(state: dict) -> None:
    p = state_path()
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, p)
