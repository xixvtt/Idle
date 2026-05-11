export type SessionState =
  | "RUNNING"
  | "IDLE"
  | "WAITING"
  | "DONE"
  | "ERROR";

export interface SessionView {
  session_id: string;
  cwd: string;
  state: SessionState;
  tokens?: number;
}

export interface DaemonSnapshot {
  type: "snapshot";
  today_tokens: number;
  tz?: string;
  today_date?: string;
  sessions: SessionView[];
}

export type DaemonEvent =
  | DaemonSnapshot
  | { type: "session_added"; session: SessionView; today_tokens: number }
  | { type: "session_state_changed"; session_id: string; state: SessionState }
  | {
      type: "session_token_delta";
      session_id: string;
      delta: number;
      today_tokens: number;
    }
  | { type: "today_tokens_changed"; today_tokens: number }
  | {
      type: "session_done";
      session_id: string;
      duration_s: number;
      delta: number;
    }
  | { type: "session_removed"; session_id: string };
