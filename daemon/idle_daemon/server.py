"""aiohttp HTTP + WebSocket server. Binds to 127.0.0.1 only."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from aiohttp import web

from . import persist, scanner, transcript
from .broadcast import Broadcaster, ws_handler
from .fsm import map_event_to_state
from .reaper import run_reaper
from .registry import (
    STATE_DONE,
    STATE_IDLE,
    SessionRegistry,
)

log = logging.getLogger(__name__)

HTTP_PORT = 7777
WS_PORT = 7778
DONE_TO_IDLE_DELAY_S = 5
RESCAN_INTERVAL_S = 30


class Daemon:
    def __init__(self) -> None:
        self.registry = SessionRegistry()
        self.broadcaster = Broadcaster()
        self._restore_persisted()
        self._bootstrap_scan()

    def _restore_persisted(self) -> None:
        st = persist.load()
        date = st.get("date")
        tokens = int(st.get("today_tokens", 0) or 0)
        if date:
            self.registry.restore_today(date, tokens)

    def _bootstrap_scan(self) -> None:
        try:
            total = scanner.scan_today_total()
            self.registry.set_today_tokens(total)
            log.info("bootstrap scan: today_tokens=%d", total)
        except Exception as e:
            log.warning("bootstrap scan failed: %s", e)

    async def rescan_loop(self) -> None:
        while True:
            await asyncio.sleep(RESCAN_INTERVAL_S)
            try:
                total = scanner.scan_today_total()
                if total != self.registry.today_tokens:
                    self.registry.set_today_tokens(total)
                    await self.broadcaster.send(
                        {
                            "type": "today_tokens_changed",
                            "today_tokens": total,
                        }
                    )
                    self._persist()
            except Exception as e:
                log.warning("rescan failed: %s", e)

    def _persist(self) -> None:
        persist.save(
            {
                "date": self.registry.today_date,
                "today_tokens": self.registry.today_tokens,
            }
        )

    def snapshot(self, *, include_per_session_tokens: bool = True) -> dict:
        return {
            "type": "snapshot",
            "today_tokens": self.registry.today_tokens,
            "tz": self.registry.tz_name(),
            "today_date": self.registry.today_date,
            "sessions": [
                s.to_dict(include_tokens=include_per_session_tokens)
                for s in self.registry.all()
            ],
        }

    async def handle_event(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return web.json_response({"ok": False, "error": "bad json"}, status=400)

        session_id = payload.get("session_id")
        if not session_id:
            return web.json_response({"ok": True, "ignored": "no session_id"})

        cwd = payload.get("cwd") or payload.get("workspace") or ""
        transcript_path = payload.get("transcript_path") or ""
        event_type = payload.get("event_type") or payload.get("hook_event_name") or ""

        session, is_new = self.registry.register(
            session_id=session_id,
            cwd=cwd,
            transcript_path=transcript_path,
        )

        # Update transcript_path if we learned a better one.
        if transcript_path and session.transcript_path != transcript_path:
            session.transcript_path = transcript_path

        if is_new:
            await self.broadcaster.send(
                {
                    "type": "session_added",
                    "session": session.to_dict(),
                    "today_tokens": self.registry.today_tokens,
                }
            )

        # Apply state mapping.
        new_state = map_event_to_state(event_type)
        if new_state and new_state != session.state:
            old = session.state
            session.state = new_state
            if new_state == "RUNNING" and not session.started_at:
                session.started_at = time.time()
            await self.broadcaster.send(
                {
                    "type": "session_state_changed",
                    "session_id": session_id,
                    "state": new_state,
                }
            )
            if new_state == STATE_DONE:
                duration = (
                    int(time.time() - session.started_at)
                    if session.started_at
                    else 0
                )
                await self.broadcaster.send(
                    {
                        "type": "session_done",
                        "session_id": session_id,
                        "duration_s": duration,
                        "delta": session.last_delta,
                    }
                )
                # Auto-revert DONE → IDLE after delay.
                asyncio.create_task(self._done_to_idle(session_id))

            _ = old  # placeholder; available for richer event payloads later

        self.registry.touch(session_id)

        # Tail transcript for any new assistant usage.
        if session.transcript_path:
            delta = transcript.tail_for_tokens(
                session.transcript_path,
                session.byte_offset,
            )
            session.byte_offset = delta.new_offset
            if delta.tokens > 0:
                self.registry.add_tokens(session_id, delta.tokens)
                # Refresh today_tokens from ground truth (filesystem scan)
                # instead of incrementing — see registry.add_tokens.
                try:
                    self.registry.set_today_tokens(scanner.scan_today_total())
                except Exception as e:
                    log.warning("inline scan failed: %s", e)
                await self.broadcaster.send(
                    {
                        "type": "session_token_delta",
                        "session_id": session_id,
                        "delta": delta.tokens,
                        "today_tokens": self.registry.today_tokens,
                    }
                )
                self._persist()

        return web.json_response({"ok": True})

    async def _done_to_idle(self, session_id: str) -> None:
        await asyncio.sleep(DONE_TO_IDLE_DELAY_S)
        s = self.registry.get(session_id)
        if s and s.state == STATE_DONE:
            s.state = STATE_IDLE
            s.started_at = None
            await self.broadcaster.send(
                {
                    "type": "session_state_changed",
                    "session_id": session_id,
                    "state": STATE_IDLE,
                }
            )


def build_app(daemon: Daemon) -> web.Application:
    app = web.Application()

    async def ws_route(request: web.Request) -> web.WebSocketResponse:
        return await ws_handler(request, daemon.broadcaster, daemon.snapshot)

    app.router.add_post("/event", daemon.handle_event)
    app.router.add_get("/healthz", lambda r: web.json_response({"ok": True}))
    app.router.add_get("/ws", ws_route)
    return app


async def run() -> None:
    daemon = Daemon()
    app = build_app(daemon)

    runner = web.AppRunner(app)
    await runner.setup()

    http_site = web.TCPSite(runner, host="127.0.0.1", port=HTTP_PORT)
    await http_site.start()
    log.info("HTTP listening on 127.0.0.1:%d", HTTP_PORT)

    # We expose WebSocket on the same port (/ws). The "ws on 7778" plan from
    # the design doc collapses to a single port here for simplicity.

    async def on_state_change(session_id: str, new_state: str) -> None:
        await daemon.broadcaster.send(
            {
                "type": "session_state_changed",
                "session_id": session_id,
                "state": new_state,
            }
        )

    async def on_remove(session_id: str) -> None:
        await daemon.broadcaster.send(
            {"type": "session_removed", "session_id": session_id}
        )

    reaper_task = asyncio.create_task(
        run_reaper(daemon.registry, on_state_change, on_remove)
    )
    rescan_task = asyncio.create_task(daemon.rescan_loop())

    try:
        await asyncio.Event().wait()
    finally:
        reaper_task.cancel()
        rescan_task.cancel()
        await runner.cleanup()
