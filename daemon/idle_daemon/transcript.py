"""Transcript JSONL tailer.

PRIVACY BOUNDARY:
This module reads Claude Code transcript files. It must ONLY access the
`usage` field of assistant messages. It must NEVER read `message.content` or
any other field that could contain user prompts, model outputs, or code.

The unit test `tests/test_no_content_read.py` enforces this rule by inspecting
the source for forbidden accessors. Do not relax that test.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TokenDelta:
    tokens: int
    new_offset: int


def _extract_usage_tokens(usage: dict) -> int:
    """Token formula: input + output + cache_creation. Excludes cache_read."""
    return (
        int(usage.get("input_tokens", 0) or 0)
        + int(usage.get("output_tokens", 0) or 0)
        + int(usage.get("cache_creation_input_tokens", 0) or 0)
    )


def _today_start_epoch() -> float:
    """Local-time midnight today, as a unix timestamp."""
    now = time.localtime()
    midnight = time.struct_time(
        (now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, now.tm_isdst)
    )
    return time.mktime(midnight)


def _parse_timestamp(value) -> float | None:
    """Best-effort: accept ISO-8601 string or numeric epoch. Returns unix
    seconds, or None if unparseable. Never reads message content."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Heuristic: if value looks like milliseconds, normalize.
        return float(value) / 1000.0 if value > 1e12 else float(value)
    if isinstance(value, str):
        try:
            # Python's fromisoformat handles "Z" suffix as of 3.11.
            s = value.replace("Z", "+00:00")
            return datetime.fromisoformat(s).astimezone(timezone.utc).timestamp()
        except ValueError:
            return None
    return None


def _parse_line_for_usage(line: str, today_start: float) -> int:
    """Return token count from one JSONL line, or 0 if not an assistant message
    with a usage field whose timestamp is today. Never reads message content."""
    line = line.strip()
    if not line:
        return 0
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        return 0

    # Anthropic transcripts can wrap the message under "message" or expose
    # role at the top level. Either way, we only ever look at usage and timestamp.
    if not isinstance(record, dict):
        return 0

    usage = None
    if isinstance(record.get("usage"), dict):
        usage = record["usage"]
    elif isinstance(record.get("message"), dict) and isinstance(
        record["message"].get("usage"), dict
    ):
        usage = record["message"]["usage"]

    if not usage:
        return 0

    # Find a timestamp: top-level "timestamp", "ts", or nested under message.
    ts_raw = (
        record.get("timestamp")
        or record.get("ts")
        or record.get("created_at")
        or (
            record["message"].get("timestamp")
            if isinstance(record.get("message"), dict)
            else None
        )
    )
    ts = _parse_timestamp(ts_raw)
    if ts is not None and ts < today_start:
        # Message is from a previous day — exclude.
        return 0

    return _extract_usage_tokens(usage)


def tail_for_tokens(path: str, byte_offset: int) -> TokenDelta:
    """Read from byte_offset to EOF; return summed token delta and new offset."""
    try:
        size = _file_size(path)
    except FileNotFoundError:
        return TokenDelta(tokens=0, new_offset=byte_offset)

    # File rotated/truncated — reset.
    if size < byte_offset:
        byte_offset = 0

    if size == byte_offset:
        return TokenDelta(tokens=0, new_offset=byte_offset)

    total = 0
    with open(path, "rb") as f:
        f.seek(byte_offset)
        chunk = f.read()
        new_offset = f.tell()

    # Only complete lines are parsed. Last partial line (no trailing \n) is
    # discarded; we'll re-read it next time when more bytes arrive.
    text = chunk.decode("utf-8", errors="replace")
    if not text.endswith("\n"):
        last_nl = text.rfind("\n")
        if last_nl == -1:
            # No newline at all: rewind, wait for more.
            return TokenDelta(tokens=0, new_offset=byte_offset)
        consumed = last_nl + 1
        new_offset = byte_offset + len(text[:consumed].encode("utf-8"))
        text = text[:consumed]

    today_start = _today_start_epoch()
    for line in text.splitlines():
        total += _parse_line_for_usage(line, today_start)

    return TokenDelta(tokens=total, new_offset=new_offset)


def _file_size(path: str) -> int:
    import os

    return os.path.getsize(path)
