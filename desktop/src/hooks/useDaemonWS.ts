import { useEffect, useRef, useState } from "react";
import type { DaemonEvent, SessionView } from "../types";

const DAEMON_URL = "ws://127.0.0.1:7777/ws";
const RECONNECT_MS = 1500;

export interface DaemonState {
  connected: boolean;
  today_tokens: number;
  tz: string;
  sessions: SessionView[];
  lastDelta: { value: number; at: number } | null;
  doneOverlay: {
    session_id: string;
    duration_s: number;
    delta: number;
  } | null;
}

const initial: DaemonState = {
  connected: false,
  today_tokens: 0,
  tz: "",
  sessions: [],
  lastDelta: null,
  doneOverlay: null,
};

export function useDaemonWS(): DaemonState {
  const [state, setState] = useState<DaemonState>(initial);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    let stopped = false;
    let ws: WebSocket | null = null;

    function connect() {
      if (stopped) return;
      ws = new WebSocket(DAEMON_URL);

      ws.onopen = () => {
        setState((s) => ({ ...s, connected: true }));
      };

      ws.onmessage = (e) => {
        let msg: DaemonEvent;
        try {
          msg = JSON.parse(e.data);
        } catch {
          return;
        }
        setState((s) => applyEvent(s, msg));
      };

      ws.onclose = () => {
        setState((s) => ({ ...s, connected: false }));
        if (!stopped) {
          timerRef.current = window.setTimeout(connect, RECONNECT_MS);
        }
      };

      ws.onerror = () => {
        // onclose will follow.
      };
    }

    connect();

    return () => {
      stopped = true;
      if (timerRef.current != null) {
        clearTimeout(timerRef.current);
      }
      ws?.close();
    };
  }, []);

  return state;
}

function applyEvent(s: DaemonState, msg: DaemonEvent): DaemonState {
  switch (msg.type) {
    case "snapshot":
      return {
        ...s,
        today_tokens: msg.today_tokens,
        tz: msg.tz ?? s.tz,
        sessions: msg.sessions,
      };

    case "today_tokens_changed":
      return { ...s, today_tokens: msg.today_tokens };

    case "session_added":
      return {
        ...s,
        today_tokens: msg.today_tokens,
        sessions: upsert(s.sessions, msg.session),
      };

    case "session_state_changed":
      return {
        ...s,
        sessions: s.sessions.map((x) =>
          x.session_id === msg.session_id ? { ...x, state: msg.state } : x,
        ),
      };

    case "session_token_delta":
      return {
        ...s,
        today_tokens: msg.today_tokens,
        sessions: s.sessions.map((x) =>
          x.session_id === msg.session_id
            ? { ...x, tokens: (x.tokens ?? 0) + msg.delta }
            : x,
        ),
        lastDelta: { value: msg.delta, at: Date.now() },
      };

    case "session_done":
      return {
        ...s,
        doneOverlay: {
          session_id: msg.session_id,
          duration_s: msg.duration_s,
          delta: msg.delta,
        },
      };

    case "session_removed":
      return {
        ...s,
        sessions: s.sessions.filter((x) => x.session_id !== msg.session_id),
      };

    default:
      return s;
  }
}

function upsert(list: SessionView[], item: SessionView): SessionView[] {
  const idx = list.findIndex((x) => x.session_id === item.session_id);
  if (idx === -1) return [...list, item];
  const copy = list.slice();
  copy[idx] = { ...copy[idx], ...item };
  return copy;
}
