<div align="center">

🌐 **English** | [中文](README.zh.md) | [Español](README.es.md)

# Idle — Claude Code Token Monitor

**A real-time token usage monitor and session tracker for [Claude Code](https://claude.com/claude-code) on macOS.**
Watch every Claude Code session, every token, every cost — live, from a floating window in the corner of your screen.

<img src="docs/images/hero.png" alt="Idle Claude Code token monitor floating next to a macOS widget" width="720" />

[![Last commit](https://img.shields.io/github/last-commit/xixvtt/Idle)](https://github.com/xixvtt/Idle/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## What Idle does

Idle is a free, open-source **Claude Code token usage monitor**. It runs as a translucent floating overlay on macOS and tracks:

- **Today's total Claude Code token usage** — live count across every session and every project
- **Active session tracker** — see which Claude Code workspaces are running, waiting, or idle in real time
- **Multi-session monitoring** — stack view of every open Claude Code session, one row each
- **Done alerts** — notified the instant a Claude Code task finishes

If you live in YOLO mode and burn through your daily Claude token quota without realizing, Idle is the cure. No browser tab, no dashboard, no API key — just a glanceable usage monitor on your desktop.

<div align="center">
  <img src="docs/images/solo.png" alt="Idle showing today's Claude Code token usage in idle mode" width="380" />
</div>

## Why Idle for Claude Code

| Problem | Idle's fix |
|---|---|
| Anthropic doesn't expose a per-day token usage view | Idle reads your local Claude Code transcripts and computes today's total live |
| Running multiple `claude` sessions makes usage impossible to track | Idle stacks every active session in one window |
| You only learn you've hit the limit when Claude stops responding | Idle shows your live token count at all times |
| Other monitors require API keys or send data to the cloud | Idle is 100% local — zero network, zero API key |

## Install (zero setup)

Download the latest release: **[Releases page →](https://github.com/xixvtt/Idle/releases)**

| Mac | File |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. Double-click the zip to unpack `Idle.app`
2. **Right-click `Idle.app` → Open → Open** (the app is unsigned — Gatekeeper asks once)
3. Pick your theme on first launch
4. Use Claude Code normally — token tracking starts immediately

No Python, no terminal, no JSON edits. The bundled daemon and Claude Code hooks install themselves.

### "Apple cannot verify Idle is free of malware" / "Idle is damaged"

This is macOS Gatekeeper blocking unsigned apps. Run this in Terminal to clear the quarantine flag:

```bash
xattr -cr /Applications/Idle.app
# or, if you unzipped it somewhere else:
xattr -cr ~/Downloads/Idle.app
```

Then double-click `Idle.app` normally.

If macOS still refuses, open **System Settings → Privacy & Security**, scroll to the bottom — you'll see "Idle was blocked…" with an **Open Anyway** button. Click it once.

> Idle will be properly code-signed and notarized by Apple in a future release. The current build is unsigned because Apple Developer membership costs $99/year — once Idle has enough users, we'll cover that and these steps disappear.

## Requirements

- macOS 12 or newer
- [Claude Code](https://claude.com/claude-code) installed

## How Idle monitors Claude Code (technical)

Idle uses two local data sources only:

1. **Claude Code hooks** — Claude Code fires shell hooks on tool use, permission requests, and task completion. Idle's bundled daemon receives these on `127.0.0.1:7777` to track session state in real time.
2. **Transcript JSONL files** — Claude Code writes a full session transcript at `~/.claude/projects/`. Idle parses only the `usage` field (input + output + cache-creation tokens) from each assistant message, filtered to today's local-timezone date.

The token total is recomputed from these files on launch and every 30 seconds, so it's always accurate — even after restart.

## Privacy

- **Zero outbound network.** The daemon binds `127.0.0.1` only.
- **No API key required.** Idle does not call the Anthropic API.
- **No prompt or response content is ever read.** Only token-count fields. Enforced by an AST test.
- **Open source (MIT).** Audit it yourself.

## Star this repo ⭐

If Idle saves you time or money on Claude Code, please star the repo — it's the single biggest signal that helps other Claude Code users find this project. Issues, PRs, and feedback are all welcome.

---

**Keywords:** Claude Code, Claude Code token monitor, Claude Code usage tracker, Anthropic token usage, Claude Code dashboard, monitor Claude Code, Claude Code session manager, Claude Code limit tracker, Claude Code macOS, Claude Code overlay, ambient display for Claude Code.
