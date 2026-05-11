import type { SessionView } from "../types";

const ICONS: Record<string, string> = {
  RUNNING: "⚡",
  IDLE: "○",
  WAITING: "⏸",
  DONE: "✓",
  ERROR: "⚠",
};

interface Props {
  sessions: SessionView[];
  today: number;
  deltaFlash: boolean;
  delta: number;
}

export function StackView({ sessions, today, deltaFlash, delta }: Props) {
  const visible = sessions.slice(0, 5);
  const hidden = sessions.length - visible.length;

  return (
    <>
      {visible.length === 0 ? (
        <div className="row empty">No active Claude sessions</div>
      ) : (
        visible.map((s) => (
          <div className="row" key={s.session_id}>
            <span className={`icon state-${s.state}`}>
              {ICONS[s.state] ?? "·"}
            </span>
            <span className="name">{s.cwd}</span>
            <span className="state">{s.state}</span>
          </div>
        ))
      )}
      {hidden > 0 ? (
        <div className="row empty">+{hidden} more (Pro)</div>
      ) : null}
      <div className="divider" />
      <div className="row">
        <span className="total">{formatTokens(today)} today</span>
        <span className={`delta ${deltaFlash ? "flash" : ""}`}>
          +{formatTokens(delta)} ↑
        </span>
      </div>
    </>
  );
}

function formatTokens(n: number): string {
  if (n < 1000) return String(n);
  if (n < 1_000_000) return `${(n / 1000).toFixed(1).replace(/\.0$/, "")}k`;
  return `${(n / 1_000_000).toFixed(2)}M`;
}
