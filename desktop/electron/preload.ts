import { contextBridge, ipcRenderer } from "electron";

type ThemePref = "light" | "dark" | "system";
type ResolvedTheme = "light" | "dark";

interface ThemePayload {
  pref: ThemePref;
  resolved: ResolvedTheme;
  onboarded: boolean;
}

contextBridge.exposeInMainWorld("idle", {
  daemonUrl: "ws://127.0.0.1:7777/ws",
  version: "0.0.1",
  resize: (w: number, h: number) => ipcRenderer.send("idle:resize", w, h),
  setTheme: (pref: ThemePref) => ipcRenderer.send("idle:setTheme", pref),
  chooseTheme: (pref: ThemePref) =>
    ipcRenderer.send("idle:chooseTheme", pref),
  onTheme: (cb: (p: ThemePayload) => void) => {
    const handler = (_e: unknown, p: ThemePayload) => cb(p);
    ipcRenderer.on("idle:theme", handler);
    return () => ipcRenderer.off("idle:theme", handler);
  },
});

export {};
