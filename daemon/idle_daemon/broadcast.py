"""WebSocket broadcaster — keeps the set of connected clients and pushes events."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from aiohttp import WSMsgType, web

log = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self) -> None:
        self._clients: set[web.WebSocketResponse] = set()
        self._lock = asyncio.Lock()

    async def register(self, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            self._clients.add(ws)

    async def unregister(self, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def send(self, payload: dict[str, Any]) -> None:
        if not self._clients:
            return
        data = json.dumps(payload)
        dead: list[web.WebSocketResponse] = []
        # Snapshot clients to avoid holding lock during network IO.
        async with self._lock:
            clients = list(self._clients)
        for ws in clients:
            if ws.closed:
                dead.append(ws)
                continue
            try:
                await ws.send_str(data)
            except ConnectionResetError:
                dead.append(ws)
            except Exception as e:
                log.warning("broadcast send failed: %s", e)
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.discard(ws)


async def ws_handler(
    request: web.Request,
    broadcaster: Broadcaster,
    snapshot_fn,
) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    await broadcaster.register(ws)
    try:
        # Send initial snapshot.
        await ws.send_str(json.dumps(snapshot_fn()))
        async for msg in ws:
            if msg.type == WSMsgType.ERROR:
                log.warning("ws error: %s", ws.exception())
                break
            # Currently we don't accept client → server messages.
    finally:
        await broadcaster.unregister(ws)
    return ws
