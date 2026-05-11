<div align="center">

# Idle

**Real-time monitor for your Claude Code usage.**

[![Last commit](https://img.shields.io/github/last-commit/xixvtt/Idle)](https://github.com/xixvtt/Idle/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## What is this?

Idle is a tiny translucent capsule that sits in the corner of your screen and tracks your Claude Code usage in real time:

- **Today's total token usage** — live, across every session and project
- **Active session list** — which workspaces are running, waiting, or idle right now
- **Done alerts** — the moment Claude finishes a task

No tab switching. No browser. No API key.

```
┌─────────────────────────────┐
│ session 1           RUNNING │
│ session 2           RUNNING │
│ session 3           WAITING │
├─────────────────────────────┤
│ 1.2M today         +2.8k up │
└─────────────────────────────┘
```

## Install

Grab the latest zip from [Releases](https://github.com/xixvtt/Idle/releases):

| Mac | File |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. Double-click the zip to unpack `Idle.app`
2. **Right-click `Idle.app` → Open → Open** (bypass Gatekeeper — the app is unsigned)
3. Pick your theme on first launch
4. Use Claude Code normally — Idle starts tracking immediately

That's it. No Python, no terminal, no JSON edits — the bundled daemon and Claude Code hooks install themselves.

## Requirements

- macOS 12+
- [Claude Code](https://claude.com/claude-code) installed

## Star this repo ⭐

If Idle saves you time, please star the repo — it's the single biggest signal that helps more developers find this project. Issues, PRs, and feedback are all welcome.
