type ThemePref = "light" | "dark" | "system";

interface Props {
  onPick: (pref: ThemePref) => void;
}

export function WelcomeView({ onPick }: Props) {
  return (
    <div className="welcome">
      <h2>Welcome to Idle</h2>
      <p>Pick a look. You can change this anytime from the tray menu.</p>
      <div className="theme-row">
        <button className="theme-btn" onClick={() => onPick("system")}>
          ⌥ System
        </button>
        <button className="theme-btn" onClick={() => onPick("light")}>
          ☀ Light
        </button>
        <button className="theme-btn" onClick={() => onPick("dark")}>
          ☾ Dark
        </button>
      </div>
    </div>
  );
}
