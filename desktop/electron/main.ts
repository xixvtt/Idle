import {
  app,
  BrowserWindow,
  Tray,
  Menu,
  nativeImage,
  nativeTheme,
  screen,
  ipcMain,
} from "electron";
import * as path from "path";
import * as fs from "fs";

const isDev = !!process.env.VITE_DEV_SERVER_URL;

const stateFile = path.join(app.getPath("userData"), "window.json");

export type ThemePref = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

interface WindowState {
  x?: number;
  y?: number;
  themePref?: ThemePref;
  onboarded?: boolean;
}

function loadWindowState(): WindowState {
  try {
    return JSON.parse(fs.readFileSync(stateFile, "utf-8"));
  } catch {
    return {};
  }
}

function saveWindowState(patch: Partial<WindowState>) {
  try {
    const current = loadWindowState();
    fs.writeFileSync(stateFile, JSON.stringify({ ...current, ...patch }));
  } catch {
    // ignore
  }
}

function resolveTheme(pref: ThemePref): ResolvedTheme {
  if (pref === "light") return "light";
  if (pref === "dark") return "dark";
  return nativeTheme.shouldUseDarkColors ? "dark" : "light";
}

let win: BrowserWindow | null = null;
let tray: Tray | null = null;
let visible = true;
let themePref: ThemePref = "system";
let onboarded = false;

function createWindow() {
  const saved = loadWindowState();

  // Default: top-right corner. Tight initial size — renderer auto-resizes
  // once the capsule measures its content.
  const primary = screen.getPrimaryDisplay();
  const W = 280;
  const H = 60;
  const margin = 16;

  const x =
    saved.x ?? primary.workArea.x + primary.workArea.width - W - margin;
  const y = saved.y ?? primary.workArea.y + margin;

  win = new BrowserWindow({
    width: W,
    height: H,
    x,
    y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    hasShadow: false,
    resizable: false,
    skipTaskbar: true,
    focusable: true,
    backgroundColor: "#00000000",
    roundedCorners: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  win.setAlwaysOnTop(true, "floating");

  if (isDev) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL!);
  } else {
    win.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }

  win.on("moved", () => {
    if (!win) return;
    const [x, y] = win.getPosition();
    saveWindowState({ x, y });
  });
}

function pushTheme() {
  if (!win) return;
  win.webContents.send("idle:theme", {
    pref: themePref,
    resolved: resolveTheme(themePref),
    onboarded,
  });
}

function createTray() {
  // 16x16 placeholder. Replace with a real icon later.
  const empty = nativeImage.createEmpty();
  tray = new Tray(empty);
  tray.setTitle("Idle");
  rebuildMenu();
}

function rebuildMenu() {
  if (!tray) return;
  const menu = Menu.buildFromTemplate([
    {
      label: visible ? "Hide overlay" : "Show overlay",
      click: () => toggleVisible(),
    },
    { type: "separator" },
    {
      label: "Theme",
      submenu: [
        {
          label: "Light",
          type: "radio",
          checked: themePref === "light",
          click: () => setThemePref("light"),
        },
        {
          label: "Dark",
          type: "radio",
          checked: themePref === "dark",
          click: () => setThemePref("dark"),
        },
        {
          label: "System",
          type: "radio",
          checked: themePref === "system",
          click: () => setThemePref("system"),
        },
      ],
    },
    { type: "separator" },
    { label: "Quit", click: () => app.quit() },
  ]);
  tray.setContextMenu(menu);
}

function setThemePref(pref: ThemePref) {
  themePref = pref;
  saveWindowState({ themePref: pref });
  pushTheme();
  rebuildMenu();
}

function toggleVisible() {
  if (!win) return;
  visible = !visible;
  if (visible) win.show();
  else win.hide();
  rebuildMenu();
}

app.whenReady().then(() => {
  if (process.platform === "darwin") {
    app.dock?.hide();
  }

  const saved = loadWindowState();
  themePref = saved.themePref ?? "system";
  onboarded = !!saved.onboarded;

  createWindow();
  createTray();

  if (win) {
    win.webContents.on("did-finish-load", () => pushTheme());
  }

  nativeTheme.on("updated", () => {
    if (themePref === "system") pushTheme();
  });

  ipcMain.on("idle:resize", (_evt, w: number, h: number) => {
    if (!win) return;
    const width = Math.max(220, Math.min(560, Math.round(w)));
    const height = Math.max(40, Math.min(800, Math.round(h)));
    win.setContentSize(width, height, false);
  });

  ipcMain.on("idle:setTheme", (_evt, pref: ThemePref) => {
    setThemePref(pref);
  });

  ipcMain.on("idle:chooseTheme", (_evt, pref: ThemePref) => {
    themePref = pref;
    onboarded = true;
    saveWindowState({ themePref: pref, onboarded: true });
    pushTheme();
    rebuildMenu();
  });
});

app.on("window-all-closed", () => {
  // Keep app alive via tray icon — do not quit.
});
