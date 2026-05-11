"""Transcript parsing tests."""

from __future__ import annotations

import json
import time
from pathlib import Path

from idle_daemon import transcript


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())


def _old_iso() -> str:
    """A timestamp guaranteed to be before today's local midnight."""
    return time.strftime(
        "%Y-%m-%dT00:00:00+00:00", time.gmtime(time.time() - 7 * 86400)
    )


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_tail_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    p.write_text("")
    d = transcript.tail_for_tokens(str(p), 0)
    assert d.tokens == 0
    assert d.new_offset == 0


def test_tail_counts_assistant_usage(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    _write_jsonl(
        p,
        [
            {"role": "user", "message": {"text": "hi"}},
            {
                "role": "assistant",
                "timestamp": _now_iso(),
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_creation_input_tokens": 10,
                    "cache_read_input_tokens": 9999,  # should be ignored
                },
            },
        ],
    )
    d = transcript.tail_for_tokens(str(p), 0)
    assert d.tokens == 160  # 100 + 50 + 10, cache_read excluded
    assert d.new_offset > 0


def test_tail_excludes_yesterday(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    _write_jsonl(
        p,
        [
            {
                "role": "assistant",
                "timestamp": _old_iso(),
                "usage": {"input_tokens": 10000, "output_tokens": 0},
            },
            {
                "role": "assistant",
                "timestamp": _now_iso(),
                "usage": {"input_tokens": 5, "output_tokens": 3},
            },
        ],
    )
    d = transcript.tail_for_tokens(str(p), 0)
    assert d.tokens == 8  # old day's 10000 excluded


def test_tail_handles_message_wrapper(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    _write_jsonl(
        p,
        [
            {
                "timestamp": _now_iso(),
                "message": {
                    "role": "assistant",
                    "usage": {"input_tokens": 5, "output_tokens": 3},
                },
            }
        ],
    )
    d = transcript.tail_for_tokens(str(p), 0)
    assert d.tokens == 8


def test_tail_resumes_from_offset(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    _write_jsonl(
        p,
        [
            {"timestamp": _now_iso(), "usage": {"input_tokens": 100, "output_tokens": 0}}
        ],
    )
    d1 = transcript.tail_for_tokens(str(p), 0)
    assert d1.tokens == 100

    with p.open("a") as f:
        f.write(
            json.dumps(
                {
                    "timestamp": _now_iso(),
                    "usage": {"input_tokens": 7, "output_tokens": 3},
                }
            )
            + "\n"
        )
    d2 = transcript.tail_for_tokens(str(p), d1.new_offset)
    assert d2.tokens == 10


def test_tail_partial_line_held(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    p.write_text('{"usage": {"input_tokens": 5')  # truncated, no newline
    d = transcript.tail_for_tokens(str(p), 0)
    assert d.tokens == 0
    assert d.new_offset == 0  # held until line completes


def test_tail_handles_truncation(tmp_path: Path) -> None:
    p = tmp_path / "session.jsonl"
    _write_jsonl(
        p,
        [
            {"timestamp": _now_iso(), "usage": {"input_tokens": 100, "output_tokens": 0}}
        ],
    )
    d1 = transcript.tail_for_tokens(str(p), 0)
    # File shrinks (rotation) — should reset.
    p.write_text("")
    d2 = transcript.tail_for_tokens(str(p), d1.new_offset)
    assert d2.tokens == 0
    assert d2.new_offset == 0
