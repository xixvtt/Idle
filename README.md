<div align="center">

# Idle

**Real-time monitor for your Claude Code usage.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/xixvtt/Idle?include_prereleases)](https://github.com/xixvtt/Idle/releases)
[![macOS](https://img.shields.io/badge/macOS-12%2B-black?logo=apple)](#install)

</div>

---

## What is this?

Idle is a tiny translucent capsule that sits in the corner of your screen and tracks your Claude Code usage in real time:

- **Today's total token usage** — live, across every session and project
- **Active session list** — which workspaces are running, waiting, or idle right now
- **Done alerts** — the moment Claude finishes a task

No tab switching. No browser. No API key.

```
┌────────────────────────────┐
│ ⚡ idle/daemon    RUNNING  │
│ ⚡ stock-agent    RUNNING  │
│ ⏸ algosnap       WAITING  │
├────────────────────────────┤
│ 1.87M today      +2.8k ↑   │
└────────────────────────────┘
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
4. Idle lives in your menu bar from here on

## Requirements

- macOS 12+
- [Claude Code](https://claude.com/claude-code) installed and running
- Python 3.11+ *(temporary — daemon will be bundled into the app in the next release)*

## Setup

The daemon isn't bundled yet. Until the next release:

```bash
# 1. Clone and run the daemon
git clone https://github.com/xixvtt/Idle.git
cd Idle/daemon
pip install uv      # if you don't have it
uv sync
uv run idle-daemon serve
```

```jsonc
// 2. Add these hooks to ~/.claude/settings.json
{
  "hooks": {
    "PreToolUse":        [{ "matcher": "*", "hooks": [{ "type": "command", "command": "curl -s -X POST http://127.0.0.1:7777/event -d @- || true", "async": true }] }],
    "PostToolUse":       [{ "matcher": "*", "hooks": [{ "type": "command", "command": "curl -s -X POST http://127.0.0.1:7777/event -d @- || true", "async": true }] }],
    "Stop":              [{ "matcher": "*", "hooks": [{ "type": "command", "command": "curl -s -X POST http://127.0.0.1:7777/event -d @- || true", "async": true }] }],
    "PermissionRequest": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "curl -s -X POST http://127.0.0.1:7777/event -d @- || true", "async": true }] }]
  }
}
```

```bash
# 3. Launch Idle.app
open /Applications/Idle.app   # or wherever you unzipped it
```
