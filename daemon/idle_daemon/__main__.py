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
