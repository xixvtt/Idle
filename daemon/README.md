# idle-daemon

Local-only background process that watches Claude Code hooks and transcripts, then pushes session state over WebSocket to the Idle Desktop app.

## Run (dev)

```bash
uv sync
uv run idle-daemon serve --debug
```

## Endpoints

- `POST 127.0.0.1:7777/event` — hook ingress (Claude Code → daemon)
- `GET  127.0.0.1:7777/ws` — WebSocket push (daemon → Idle Desktop)
- `GET  127.0.0.1:7777/healthz` — liveness probe

## Privacy

- Reads transcript JSONL files ONLY for the `usage` field
- Never accesses `message.content` (enforced by `tests/test_no_content_read.py`)
- Binds 127.0.0.1 only
- No outbound network — verify with `uv run idle-daemon audit-network`

## Tests

```bash
uv run pytest
```
