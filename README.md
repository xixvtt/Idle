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

## Features

- **Single tap to cycle** — Idle view ↔ Stack view (all sessions)
- **Light, Dark, or System** — auto-switches with macOS appearance
- **Zero network** — your prompts and code never leave your machine
- **Drag anywhere** — top-strip handle, position persists across launches
- **Multi-session aware** — stacks every active Claude Code workspace
- **Timezone-aware "today"** — resets at your local midnight, not UTC

## Install

Grab the latest zip from [Releases](https://github.com/xixvtt/Idle/releases):

| Mac | File |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. Double-click the zip to unpack `Idle.app`
2. **Right-click `Idle.app` → Open → Open** (bypass Gatekeeper — the app is unsigned)
3. Pick your theme on first launch
4. Done. Idle lives in your menu bar from here on.

> The app is currently unsigned. Right-click → Open is needed only on first launch; macOS remembers your choice.

## How it works

```
       Claude Code
            │
   ┌────────┼────────┐
   │ hooks  │ JSONL  │
   ▼        ▼        ▼
  ┌──────────────────────┐
  │   Idle daemon (Py)   │   localhost:7777
  │   reads usage tokens │   (no network out)
  └──────────┬───────────┘
             │ WebSocket
             ▼
  ┌──────────────────────┐
  │  Idle.app (Electron) │
  │  floating overlay    │
  └──────────────────────┘
```

The daemon reads two local sources only:
- Claude Code's hook payloads (state changes)
- Transcript JSONL files under `~/.claude/projects/` (`usage` fields only — never `message.content`)

Everything stays on your laptop.

## Privacy

This is the whole pitch:

- **Zero outbound network.** Verified by `idle-daemon audit-network`.
- **No API key.** Idle does not call the Anthropic API.
- **No `message.content` reads.** Enforced by an AST test in CI.
- **Localhost-only IPC.** Daemon binds `127.0.0.1`, never `0.0.0.0`.
- **Open source (MIT).** Audit the daemon yourself.

> `grep -r "api.anthropic" daemon/` returns nothing. By design.

## Requirements

- macOS 12+
- [Claude Code](https://claude.com/claude-code) installed and running
- Python 3.11+ *(temporary — daemon will be bundled into the app in the next release)*

## Setup (V0)

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

## Develop

```bash
# Daemon
cd daemon
uv sync
uv run pytest              # tests
uv run idle-daemon serve   # run

# Desktop (separate terminal)
cd desktop
npm install
npm run electron:dev       # run with rebuild
npm run dist:arm           # produce Idle-*.zip in release/
```

## Roadmap

- [x] V0 — software-first overlay, Mac, dark + light + system themes
- [ ] V0.1 — bundle Python daemon into `Idle.app` (no separate install)
- [ ] V0.2 — automatic hook installer with diff approval
- [ ] V0.3 — code signing + notarization (no more Gatekeeper bypass)
- [ ] V1 — Windows + Linux builds
- [ ] V2 — Pro: per-session token history, multi-window, themes
- [ ] V3 — Hardware companion (transparent OLED + ESP32, BLE)

## What "Idle" stands for

Three meanings, take your pick:

1. AI agents spend most of their time **idle** (running in the background)
2. Developers spend a lot of time **idle** while waiting for Claude
3. The display sits **idle** in your corner until something interesting happens

## License

[MIT](LICENSE). Built with [Electron](https://www.electronjs.org/), [React](https://react.dev/), [aiohttp](https://docs.aiohttp.org/), and a stubborn refusal to send your data anywhere.
