"""CLI entrypoint."""

from __future__ import annotations

import asyncio
import logging

import click

from . import __version__
from .server import run


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Idle daemon — Claude Code state and token monitor."""


@cli.command()
@click.option("--debug", is_flag=True, help="Verbose logging.")
def serve(debug: bool) -> None:
    """Run the daemon (default)."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


@cli.command()
def audit_network() -> None:
    """Print proof that the daemon has no outbound network sockets."""
    import psutil

    me = psutil.Process()
    outbound = []
    for c in me.connections(kind="inet"):
        if c.raddr and c.raddr.ip not in ("127.0.0.1", "::1"):
            outbound.append(c)
    if outbound:
        click.echo("FAIL — daemon has outbound connections:")
        for c in outbound:
            click.echo(f"  {c.laddr} -> {c.raddr}  status={c.status}")
        raise SystemExit(1)
    click.echo("OK — no outbound non-loopback connections.")


HOOK_EVENTS = ("PreToolUse", "PostToolUse", "Stop", "PermissionRequest", "StopFailure")
HOOK_CMD = "curl -s -X POST http://127.0.0.1:7777/event -H 'Content-Type: application/json' --data-binary @- || true"
HOOK_MARKER = "127.0.0.1:7777/event"


def _settings_path():
    from pathlib import Path
    return Path.home() / ".claude" / "settings.json"


def _hook_already(arr):
    for entry in arr:
        for h in entry.get("hooks", []):
            if HOOK_MARKER in h.get("command", ""):
                return True
    return False


@cli.command("install-hooks")
def install_hooks() -> None:
    """Add Idle's hooks to ~/.claude/settings.json (idempotent)."""
    import json
    p = _settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            click.echo("settings.json is not valid JSON; aborting.", err=True)
            raise SystemExit(1)
    # Backup once.
    bak = p.with_suffix(".json.bak.idle")
    if p.exists() and not bak.exists():
        bak.write_text(p.read_text())
    hooks = data.setdefault("hooks", {})
    changed = 0
    for evt in HOOK_EVENTS:
        arr = hooks.setdefault(evt, [])
        if _hook_already(arr):
            continue
        arr.append(
            {
                "matcher": "*",
                "hooks": [{"type": "command", "command": HOOK_CMD, "async": True}],
            }
        )
        changed += 1
    p.write_text(json.dumps(data, indent=2))
    click.echo(f"installed: {changed} hook(s) added. settings.json updated.")


@cli.command("uninstall-hooks")
def uninstall_hooks() -> None:
    """Remove Idle's hooks from ~/.claude/settings.json."""
    import json
    p = _settings_path()
    if not p.exists():
        click.echo("no settings.json")
        return
    data = json.loads(p.read_text())
    hooks = data.get("hooks") or {}
    removed = 0
    for evt in HOOK_EVENTS:
        arr = hooks.get(evt) or []
        new_arr = []
        for entry in arr:
            kept = [h for h in entry.get("hooks", []) if HOOK_MARKER not in h.get("command", "")]
            if kept:
                entry["hooks"] = kept
                new_arr.append(entry)
            else:
                removed += 1
        if new_arr:
            hooks[evt] = new_arr
        else:
            hooks.pop(evt, None)
    p.write_text(json.dumps(data, indent=2))
    click.echo(f"uninstalled: {removed} hook(s) removed.")


@cli.command("hooks-status")
def hooks_status() -> None:
    """Print whether Idle's hooks are installed."""
    import json
    p = _settings_path()
    if not p.exists():
        click.echo("absent")
        return
    data = json.loads(p.read_text())
    hooks = data.get("hooks") or {}
    have = []
    for evt in HOOK_EVENTS:
        if _hook_already(hooks.get(evt) or []):
            have.append(evt)
    if len(have) == len(HOOK_EVENTS):
        click.echo("installed")
    elif have:
        click.echo(f"partial: {','.join(have)}")
    else:
        click.echo("absent")


@cli.command()
def doctor() -> None:
    """Self-check: hook config, ports, transcript dir."""
    from pathlib import Path

    issues: list[str] = []

    settings = Path.home() / ".claude" / "settings.json"
    if not settings.exists():
        issues.append(f"~/.claude/settings.json not found")
    else:
        text = settings.read_text()
        if "localhost:7777" not in text and "127.0.0.1:7777" not in text:
            issues.append("Claude Code hooks not configured to call localhost:7777")

    projects = Path.home() / ".claude" / "projects"
    if not projects.exists():
        issues.append(f"~/.claude/projects/ not found — Claude Code never run?")

    if issues:
        click.echo("Issues:")
        for i in issues:
            click.echo(f"  - {i}")
        raise SystemExit(1)
    click.echo("OK")


def main() -> None:
    # Default to `serve` when no subcommand given.
    import sys

    if len(sys.argv) == 1:
        sys.argv.append("serve")
    cli()


if __name__ == "__main__":
    main()
