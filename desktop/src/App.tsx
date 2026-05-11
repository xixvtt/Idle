import { useEffect, useRef, useState } from "react";
import { useDaemonWS } from "./hooks/useDaemonWS";
import { StackView } from "./views/StackView";
import { IdleView } from "./views/IdleView";
import { DoneOverlay } from "./views/DoneOverlay";
import { WelcomeView } from "./views/WelcomeView";

type ViewMode = "stack" | "idle";
type ThemePref = "light" | "dark" | "system";
type ResolvedTheme = "light" | "dark";

const DELTA_FLASH_MS = 2000;
const DONE_HOLD_MS = 4000;

declare global {
  interface Window {
    idle?: {
      daemonUrl: string;
      version: string;
      resize: (w: number, h: number) => void;
      setTheme: (pref: ThemePref) => void;
      chooseTheme: (pref: ThemePref) => void;
      onTheme: (
        cb: (p: {
          pref: ThemePref;
          resolved: ResolvedTheme;
          onboarded: boolean;
        }) => void,
      ) => () => void;
    };
  }
}

export function App() {
  const daemon = useDaemonWS();
  const [view, setView] = useState<ViewMode>("idle");
  const [theme, setTheme] = useState<ResolvedTheme>("dark");
  const [needsOnboard, setNeedsOnboard] = useState(false);

  const initializedRef = useRef(false);
  useEffect(() => {
    const off = window.idle?.onTheme((p) => {
      setTheme(p.resolved);
      if (!initializedRef.current) {
        setNeedsOnboard(!p.onboarded);
        initializedRef.current = true;
      } else if (p.onboarded) {
        setNeedsOnboard(false);
      }
    });
    return off;
  }, []);

  // Apply theme class to document body for CSS variables.
  useEffect(() => {
    document.body.classList.toggle("theme-dark", theme === "dark");
    document.body.classList.toggle("theme-light", theme === "light");
  }, [theme]);

  const [flashUntil, setFlashUntil] = useState(0);
  useEffect(() => {
    if (daemon.lastDelta) {
      setFlashUntil(daemon.lastDelta.at + DELTA_FLASH_MS);
      const t = setTimeout(() => setFlashUntil(0), DELTA_FLASH_MS);
      return () => clearTimeout(t);
    }
  }, [daemon.lastDelta?.at]);

  const [doneVisible, setDoneVisible] = useState<typeof daemon.doneOverlay>(
    null,
  );
  useEffect(() => {
    if (daemon.doneOverlay) {
      setDoneVisible(daemon.doneOverlay);
      const t = setTimeout(() => setDoneVisible(null), DONE_HOLD_MS);
      return () => clearTimeout(t);
    }
  }, [daemon.doneOverlay]);

  const cycleView = (e: React.MouseEvent) => {
    if (needsOnboard) return;
    if (e.target instanceof HTMLElement && e.target.closest(".drag-handle"))
      return;
    if (e.target instanceof HTMLElement && e.target.closest("button")) return;
    setView((v) => (v === "stack" ? "idle" : "stack"));
  };

  const flashOn = flashUntil > Date.now();

  const capsuleRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const el = capsuleRef.current;
    if (!el || !window.idle?.resize) return;
    const ro = new ResizeObserver(() => {
      const r = el.getBoundingClientRect();
      window.idle!.resize(Math.ceil(r.width), Math.ceil(r.height));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [needsOnboard, view]);

  const onPickTheme = (pref: ThemePref) => {
    window.idle?.chooseTheme(pref);
    setNeedsOnboard(false);
  };

  const isDone = !!doneVisible;
  const capsuleClass = isDone ? "capsule capsule-done" : "capsule";

  return (
    <div ref={capsuleRef} className={capsuleClass} onClick={cycleView}>
      <div className="drag-handle" />
      {needsOnboard ? (
        <WelcomeView onPick={onPickTheme} />
      ) : isDone ? (
        <DoneOverlay
          task={
            daemon.sessions.find((x) => x.session_id === doneVisible!.session_id)
              ?.cwd ?? null
          }
          duration_s={doneVisible!.duration_s}
          delta={doneVisible!.delta}
        />
      ) : view === "stack" ? (
        <StackView
          sessions={daemon.sessions}
          today={daemon.today_tokens}
          deltaFlash={flashOn}
          delta={daemon.lastDelta?.value ?? 0}
        />
      ) : (
        <IdleView
          today={daemon.today_tokens}
          connected={daemon.connected}
          tz={daemon.tz}
        />
      )}
    </div>
  );
}
