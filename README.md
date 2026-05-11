# Idle

Ambient display for Claude Code. Floating, always-on-top overlay showing your sessions and token usage in real time.

**Privacy by design**: zero network, zero API key. All data stays on your laptop.

## What's here

- `daemon/` — Python daemon. Reads Claude Code hooks + transcript JSONL files, exposes WebSocket. Open source MIT.
- `desktop/` — Electron overlay app. Connects to daemon, renders floating window.
- `docs/` — Install guide, privacy notes, protocol spec.

## Status

V0 (software-only) in active development. See `docs/` for design + protocol.
Hardware version ([Idle Mini](#)) follows once software validates.

## Quickstart (dev)

```bash
# Daemon
cd daemon
uv sync
uv run idle-daemon

# Desktop (separate terminal)
cd desktop
npm install
npm run dev
```

## License

MIT (see LICENSE)
