"""Privacy boundary test.

Ensures that idle_daemon never reads `message.content` from transcripts.
If this test fails, REVIEW THE CODE — do not relax the test, since reading
message content would break Idle's primary privacy guarantee.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG_DIR = Path(__file__).resolve().parent.parent / "idle_daemon"

# String tokens that should never appear in code that reads transcript records.
FORBIDDEN = [
    '"content"',
    "'content'",
    '["content"]',
    "['content']',",
    ".content",
]


def _python_files() -> list[Path]:
    return sorted(p for p in PKG_DIR.rglob("*.py"))


def test_transcript_does_not_reference_content() -> None:
    transcript_py = PKG_DIR / "transcript.py"
    src = transcript_py.read_text()
    # Strip comments so the privacy notice itself doesn't trigger the check.
    lines = []
    for line in src.splitlines():
        stripped = line.split("#", 1)[0]
        lines.append(stripped)
    code_only = "\n".join(lines)
    # Allow the word "content" inside docstrings or notice prose: strip those.
    tree = ast.parse(src)
    # Walk AST: any attribute access named "content" or subscript with "content".
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "content":
            pytest.fail(f"transcript.py reads .content at line {node.lineno}")
        if isinstance(node, ast.Subscript):
            slice_node = node.slice
            if isinstance(slice_node, ast.Constant) and slice_node.value == "content":
                pytest.fail(
                    f"transcript.py subscripts ['content'] at line {node.lineno}"
                )


def test_no_module_reads_message_content_attribute() -> None:
    """Broader check across the package."""
    for py in _python_files():
        if py.name == "test_no_content_read.py":
            continue
        try:
            tree = ast.parse(py.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "content":
                pytest.fail(f"{py.name}:{node.lineno} reads .content")
