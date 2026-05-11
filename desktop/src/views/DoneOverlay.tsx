interface Props {
  task: string | null;
  duration_s: number;
  delta: number;
}

export function DoneOverlay({ task, duration_s, delta }: Props) {
  return (
    <>
      <div className="row">
        <span className="icon state-DONE">✓</span>
        <span className="name">{task ?? "session"}</span>
        <span className="state">DONE</span>
      </div>
      <div className="row">
        <span className="empty">{formatDuration(duration_s)}</span>
        <span className="total">+{formatTokens(delta)} tok</span>
      </div>
    </>
  );
}

function formatDuration(s: number): string {
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}m${String(sec).padStart(2, "0")}s`;
}

function formatTokens(n: number): string {
  if (n < 1000) return String(n);
  if (n < 1_000_000) return `${(n / 1000).toFixed(1).replace(/\.0$/, "")}k`;
  return `${(n / 1_000_000).toFixed(2)}M`;
}
