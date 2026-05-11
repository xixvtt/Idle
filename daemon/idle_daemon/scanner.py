"""Filesystem scanner — computes today's total tokens across ALL transcripts
in ~/.claude/projects/. Catches sessions that haven't fired hooks since
daemon start.

PRIVACY: same boundary as transcript.py — only reads `usage` and `timestamp`
fields, never `message.content`.
"""

from __future__ import annotations

import glob
import json
import logging
import os
import time
from datetime import datetime, timezone

log = logging.getLogger(__name__)


def _today_start_epoch() -> float:
    now = time.localtime()
    midnight = time.struct_time(
        (now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, now.tm_isdst)
    )
    return time.mktime(midnight)


def _parse_ts(value) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        s = value.replace("Z", "+00:00")
        return datetime.fromisoformat(s).astimezone(timezone.utc).timestamp()
    except ValueError:
        return None


def _extract_usage_tokens(usage: dict) -> int:
    return (
        int(usage.get("input_tokens", 0) or 0)
        + int(usage.get("output_tokens", 0) or 0)
        + int(usage.get("cache_creation_input_tokens", 0) or 0)
    )


def _scan_file_for_today(path: str, today_start: float) -> int:
    total = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict):
                    continue
                msg = rec.get("message")
                usage = None
                if isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
                    usage = msg["usage"]
                elif isinstance(rec.get("usage"), dict):
                    usage = rec["usage"]
                if not usage:
                    continue
                ts_raw = (
                    rec.get("timestamp")
                    or rec.get("ts")
                    or rec.get("created_at")
                )
                ts = _parse_ts(ts_raw)
                if ts is None or ts < today_start:
                    continue
                total += _extract_usage_tokens(usage)
    except OSError as e:
        log.warning("scan failed for %s: %s", path, e)
    return total


def scan_today_total(projects_dir: str | None = None) -> int:
    """Sum today's tokens across every transcript JSONL under projects_dir.

    Only considers files modified within the last 36 hours to keep the scan
    fast — stale older files cannot contain today's content."""
    if projects_dir is None:
        projects_dir = os.path.expanduser("~/.claude/projects")
    today_start = _today_start_epoch()
    cutoff = time.time() - 36 * 3600
    total = 0
    pattern = os.path.join(projects_dir, "**", "*.jsonl")
    for path in glob.iglob(pattern, recursive=True):
        try:
            if os.path.getmtime(path) < cutoff:
                continue
        except OSError:
            continue
        total += _scan_file_for_today(path, today_start)
    return total
