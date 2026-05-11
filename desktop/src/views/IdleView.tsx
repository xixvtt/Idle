interface Props {
  today: number;
  connected: boolean;
  tz: string;
}

export function IdleView({ today, connected, tz }: Props) {
  const label = connected ? (tz ? `Today · ${tz}` : "Today") : "daemon offline";
  return (
    <>
      <div className="idle-row">
        <span className="label">{label}</span>
        <span className="total">{formatTokens(today)}</span>
      </div>
      <div className="idle-row">
        <span className="label">tap for sessions →</span>
      </div>
    </>
  );
}

function formatTokens(n: number): string {
  if (n < 1000) return String(n);
  if (n < 1_000_000) return `${(n / 1000).toFixed(1).replace(/\.0$/, "")}k`;
  return `${(n / 1_000_000).toFixed(2)}M`;
}
