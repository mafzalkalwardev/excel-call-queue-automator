import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
try:
    from ttkbootstrap.widgets.scrolled import ScrolledText
except ImportError:
    try:
        from ttkbootstrap.scrolled import ScrolledText
    except ImportError:
        ScrolledText = None

import pandas as pd
import pyautogui
import time
import random
from datetime import datetime
from pynput import keyboard, mouse
import csv
import os
import json
import threading

# ===== CONFIG ===== #
CONFIG_FILE = "dialer_config.json"
LOG_FILE = "call_logs.csv"
TYPE_DELAY = 0.05

pyautogui.FAILSAFE = True

DEFAULT_CONFIG = {
    "number_field": [1514, 315],
    "call_button": [1848, 309],
    "end_call_button": [1693, 934],
    "excel_path": "",
    "initial_delay": 5
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in cfg:
                        cfg[k] = v
                return cfg
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def log_call(number, status):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Time", "Phone", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), number, status])


def get_completed_numbers():
    if not os.path.exists(LOG_FILE):
        return set()
    completed = set()
    try:
        with open(LOG_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Status") == "ENDED":
                    completed.add(row["Phone"])
    except:
        pass
    return completed


def load_call_logs():
    logs = []
    if not os.path.exists(LOG_FILE):
        return logs
    try:
        with open(LOG_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                logs.append(row)
    except:
        pass
    return logs


# ===== MAIN APP ===== #
class AutoDialerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Call Queue Automator")
        self.root.geometry("1020x730")
        self.root.minsize(900, 650)

        self.config = load_config()
        self.contacts = []
        self.current_index = 0
        self.call_active = False
        self.running = False
        self.listener = None
        self.coord_target = None
        self.mouse_listener = None

        self.BG      = "#111827"
        self.BG2     = "#1e2a35"
        self.FG      = "#e2e8f0"
        self.ACCENT  = "#00ff88"
        self.ACCENT2 = "#7ecfff"
        self.WARN    = "#ffd166"
        self.DANGER  = "#ef4444"
        self.MUTED   = "#64748b"
        self.FONT    = ("Courier New", 10)
        self.FONT_B  = ("Courier New", 10, "bold")
        self.FONT_LG = ("Courier New", 14, "bold")
        self.FONT_XL = ("Courier New", 19, "bold")
        self.FONT_SM = ("Courier New", 9)

        self.root.configure(bg=self.BG)
        self._build_ui()
        self._load_logs_table()

    def _lf(self, parent, text, fg=None):
        """Safe LabelFrame using pure tkinter — no bootstyle."""
        return tk.LabelFrame(
            parent, text=text,
            bg=self.BG2, fg=fg or self.ACCENT2,
            font=("Courier New", 9, "bold"),
            bd=1, relief="groove",
            highlightbackground=self.MUTED
        )

    def _btn(self, parent, text, command, color=None, width=None, state=NORMAL):
        color = color or self.ACCENT2
        kw = dict(
            text=text, command=command,
            bg=self.BG2, fg=color,
            activebackground="#1e3a5f", activeforeground=color,
            font=self.FONT_B, bd=1, relief="flat",
            highlightbackground=color, highlightthickness=1,
            cursor="hand2", state=state, padx=10, pady=5
        )
        if width:
            kw["width"] = width
        return tk.Button(parent, **kw)

    # ────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg="#0d1520", height=52)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="📞  Call Queue Automator",
                 font=("Courier New", 18, "bold"),
                 bg="#0d1520", fg=self.ACCENT).pack(side=LEFT, padx=18, pady=10)
        tk.Label(hdr, text="Coordinate Dialer",
                 font=self.FONT_SM, bg="#0d1520", fg=self.MUTED).pack(side=LEFT)

        self.status_badge = tk.Label(hdr, text="● IDLE",
                                     font=self.FONT_B, bg="#0d1520", fg=self.MUTED)
        self.status_badge.pack(side=RIGHT, padx=18)

        # Style tabs
        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("TNotebook",      background=self.BG,     borderwidth=0)
        sty.configure("TNotebook.Tab",  background="#0d1520",   foreground=self.MUTED,
                      font=self.FONT, padding=[14, 6])
        sty.map("TNotebook.Tab",
                background=[("selected", self.BG2)],
                foreground=[("selected", self.ACCENT)])

        nb = ttk.Notebook(self.root)
        nb.pack(fill=BOTH, expand=True, padx=10, pady=(6, 10))

        self.tab_dialer = tk.Frame(nb, bg=self.BG)
        self.tab_coords = tk.Frame(nb, bg=self.BG)
        self.tab_logs   = tk.Frame(nb, bg=self.BG)

        nb.add(self.tab_dialer, text="  🚀 Dialer  ")
        nb.add(self.tab_coords, text="  🎯 Coordinates  ")
        nb.add(self.tab_logs,   text="  📋 Call Logs  ")

        self._build_dialer_tab()
        self._build_coords_tab()
        self._build_logs_tab()

    # ── DIALER TAB ──────────────────────────────────
    def _build_dialer_tab(self):
        f = self.tab_dialer

        # File
        fc = self._lf(f, "  📂  Phone List (Excel File)", fg=self.ACCENT2)
        fc.pack(fill=X, padx=16, pady=(14, 6))
        fc.columnconfigure(0, weight=1)

        self.excel_var = tk.StringVar(value=self.config.get("excel_path", ""))
        tk.Entry(fc, textvariable=self.excel_var,
                 bg="#0d1520", fg=self.FG, insertbackground=self.ACCENT,
                 font=self.FONT, bd=0, highlightthickness=1,
                 highlightbackground=self.MUTED, relief="flat"
                 ).grid(row=0, column=0, sticky="ew", padx=(10, 8), pady=10, ipady=5)

        self._btn(fc, "Browse", self._browse_file, color=self.ACCENT2).grid(
            row=0, column=1, padx=(0, 10), pady=10)

        # Settings
        sc = self._lf(f, "  ⚙️  Settings")
        sc.pack(fill=X, padx=16, pady=6)

        tk.Label(sc, text="Start Delay (sec):", font=self.FONT,
                 bg=self.BG2, fg=self.FG).pack(side=LEFT, padx=(10, 6), pady=8)
        self.delay_var = tk.IntVar(value=self.config.get("initial_delay", 5))
        tk.Spinbox(sc, from_=2, to=30, textvariable=self.delay_var, width=5,
                   font=self.FONT, bg="#0d1520", fg=self.ACCENT,
                   buttonbackground=self.BG2, insertbackground=self.ACCENT
                   ).pack(side=LEFT, pady=8)

        # Progress
        pc = self._lf(f, "  📊  Progress", fg=self.ACCENT2)
        pc.pack(fill=X, padx=16, pady=6)

        sr = tk.Frame(pc, bg=self.BG2)
        sr.pack(fill=X, padx=10, pady=(8, 4))

        def stat(parent, lbl, col):
            tk.Label(parent, text=lbl, font=self.FONT, bg=self.BG2, fg=self.MUTED).pack(side=LEFT)
            v = tk.Label(parent, text="—", font=self.FONT_B, bg=self.BG2, fg=col)
            v.pack(side=LEFT, padx=(2, 18))
            return v

        self.lbl_total     = stat(sr, "Total:",     self.ACCENT2)
        self.lbl_done      = stat(sr, "Completed:", self.ACCENT)
        self.lbl_remaining = stat(sr, "Remaining:", self.WARN)

        ps = ttk.Style()
        ps.configure("G.Horizontal.TProgressbar",
                     troughcolor="#0d1520", background=self.ACCENT, thickness=14)
        self.progress_bar = ttk.Progressbar(pc, style="G.Horizontal.TProgressbar",
                                            mode="determinate")
        self.progress_bar.pack(fill=X, padx=10, pady=(0, 10))

        # Current call
        cc = self._lf(f, "  📞  Current Call", fg=self.WARN)
        cc.pack(fill=X, padx=16, pady=6)
        self.lbl_current = tk.Label(cc, text="No active call",
                                    font=self.FONT_LG, bg=self.BG2, fg=self.WARN)
        self.lbl_current.pack(pady=10)

        # Buttons
        bf = tk.Frame(f, bg=self.BG)
        bf.pack(fill=X, padx=16, pady=(10, 4))

        self.btn_load  = self._btn(bf, "⬇  Load Numbers",  self._load_numbers, color=self.ACCENT2, width=18)
        self.btn_start = self._btn(bf, "▶  Start Dialer",  self._start_dialer, color=self.ACCENT,  width=18, state=DISABLED)
        self.btn_next  = self._btn(bf, "⏭  Next Call (X)", self._manual_next,  color=self.WARN,    width=18, state=DISABLED)
        self.btn_stop  = self._btn(bf, "⏹  Stop",          self._stop_dialer,  color=self.DANGER,  width=12, state=DISABLED)

        for b in (self.btn_load, self.btn_start, self.btn_next, self.btn_stop):
            b.pack(side=LEFT, padx=4)

        # Console
        lc = self._lf(f, "  🖥️  Activity Log")
        lc.pack(fill=BOTH, expand=True, padx=16, pady=(6, 10))

        self.console = tk.Text(lc, height=8, font=("Courier New", 9),
                               bg="#050e18", fg=self.ACCENT,
                               insertbackground=self.ACCENT,
                               bd=0, relief="flat", state=DISABLED,
                               wrap="word", padx=8, pady=6)
        cs = tk.Scrollbar(lc, command=self.console.yview,
                          bg=self.BG2, troughcolor="#0d1520")
        self.console.configure(yscrollcommand=cs.set)
        cs.pack(side=RIGHT, fill=Y)
        self.console.pack(fill=BOTH, expand=True, padx=(8, 0), pady=8)

    # ── COORDINATES TAB ─────────────────────────────
    def _build_coords_tab(self):
        f = self.tab_coords

        tk.Label(f, text="Screen Coordinate Setup",
                 font=self.FONT_XL, bg=self.BG, fg=self.ACCENT).pack(pady=(20, 4))
        tk.Label(f, text="Click  🎯 Pick  then click the matching element on your screen.",
                 font=self.FONT_SM, bg=self.BG, fg=self.MUTED).pack(pady=(0, 14))

        cc = self._lf(f, "  🖱️  Coordinate Settings", fg=self.ACCENT2)
        cc.pack(fill=X, padx=50, pady=6)
        cc.columnconfigure(1, weight=1)

        fields = [
            ("number_field",    "📱  Number Input Field", "Where the phone number is typed"),
            ("call_button",     "📞  Call / Dial Button",  "Button that starts the call"),
            ("end_call_button", "🔴  End Call Button",     "Button that hangs up the call"),
        ]

        self.coord_vars = {}
        for i, (key, label, hint) in enumerate(fields):
            tk.Label(cc, text=label, font=self.FONT_B,
                     bg=self.BG2, fg=self.FG).grid(
                row=i, column=0, sticky=W, pady=10, padx=(12, 8))

            x_var = tk.IntVar(value=self.config[key][0])
            y_var = tk.IntVar(value=self.config[key][1])
            self.coord_vars[key] = (x_var, y_var)

            cf2 = tk.Frame(cc, bg=self.BG2)
            cf2.grid(row=i, column=1, sticky=W, pady=6)

            for lbl_txt, var in [("X:", x_var), ("Y:", y_var)]:
                tk.Label(cf2, text=lbl_txt, font=self.FONT,
                         bg=self.BG2, fg=self.MUTED).pack(side=LEFT)
                tk.Entry(cf2, textvariable=var, width=7,
                         font=("Courier New", 11, "bold"),
                         bg="#0d1520", fg=self.ACCENT,
                         insertbackground=self.ACCENT,
                         relief="flat", bd=0,
                         highlightthickness=1,
                         highlightbackground=self.MUTED
                         ).pack(side=LEFT, padx=(2, 12), ipady=4)

            self._btn(cc, "🎯 Pick",
                      lambda k=key: self._pick_coordinate(k),
                      color=self.WARN, width=10).grid(row=i, column=2, padx=10)

            tk.Label(cc, text=hint, font=self.FONT_SM,
                     bg=self.BG2, fg=self.MUTED).grid(
                row=i, column=3, sticky=W, padx=(8, 12))

        self.coord_status = tk.Label(f, text="",
                                     font=self.FONT_B, bg=self.BG, fg=self.WARN)
        self.coord_status.pack(pady=8)

        self._btn(f, "💾  Save Coordinates", self._save_coords,
                  color=self.ACCENT, width=24).pack(pady=(4, 6))

        # Test section
        tc = self._lf(f, "  🧪  Test Mouse Position")
        tc.pack(fill=X, padx=50, pady=(12, 6))

        tk.Label(tc, text="Moves mouse to position (does NOT click) — visual check only.",
                 font=self.FONT_SM, bg=self.BG2, fg=self.MUTED).pack(anchor=W, padx=10, pady=(8, 4))

        tr = tk.Frame(tc, bg=self.BG2)
        tr.pack(pady=8)
        for key, lbl in [("number_field", "Number Field"),
                         ("call_button",  "Call Button"),
                         ("end_call_button", "End Call")]:
            self._btn(tr, f"→ {lbl}",
                      lambda k=key: self._test_move(k),
                      color=self.ACCENT2, width=16).pack(side=LEFT, padx=6)

    # ── LOGS TAB ────────────────────────────────────
    def _build_logs_tab(self):
        f = self.tab_logs

        top = tk.Frame(f, bg=self.BG)
        top.pack(fill=X, padx=16, pady=(12, 4))

        tk.Label(top, text="Call History", font=self.FONT_LG,
                 bg=self.BG, fg=self.ACCENT2).pack(side=LEFT)

        for txt, cmd, col in [
            ("📤 Export CSV", self._export_logs,     self.ACCENT),
            ("🗑 Clear Logs", self._clear_logs,       self.DANGER),
            ("🔄 Refresh",    self._load_logs_table,  self.ACCENT2),
        ]:
            self._btn(top, txt, cmd, color=col, width=14).pack(side=RIGHT, padx=4)

        stats = tk.Frame(f, bg=self.BG)
        stats.pack(fill=X, padx=16, pady=4)
        self.lbl_log_total = tk.Label(stats, text="Total: 0",
                                      font=self.FONT, bg=self.BG, fg=self.ACCENT2)
        self.lbl_log_total.pack(side=LEFT, padx=10)
        self.lbl_log_ended = tk.Label(stats, text="Completed: 0",
                                      font=self.FONT, bg=self.BG, fg=self.ACCENT)
        self.lbl_log_ended.pack(side=LEFT, padx=10)

        tf = tk.Frame(f, bg=self.BG)
        tf.pack(fill=BOTH, expand=True, padx=16, pady=(4, 12))

        ts = ttk.Style()
        ts.configure("dark.Treeview",
                     background="#0d1520", foreground=self.FG,
                     fieldbackground="#0d1520",
                     rowheight=26, font=self.FONT)
        ts.configure("dark.Treeview.Heading",
                     background=self.BG2, foreground=self.ACCENT2,
                     font=self.FONT_B)
        ts.map("dark.Treeview", background=[("selected", "#1e3a5f")])

        sb = tk.Scrollbar(tf, bg=self.BG2, troughcolor="#0d1520")
        sb.pack(side=RIGHT, fill=Y)

        self.log_tree = ttk.Treeview(tf, columns=("Time", "Phone", "Status"),
                                     show="headings", style="dark.Treeview",
                                     yscrollcommand=sb.set)
        sb.config(command=self.log_tree.yview)

        self.log_tree.heading("Time",   text="Time")
        self.log_tree.heading("Phone",  text="Phone")
        self.log_tree.heading("Status", text="Status")
        self.log_tree.column("Time",   width=200)
        self.log_tree.column("Phone",  width=160)
        self.log_tree.column("Status", width=120)
        self.log_tree.tag_configure("ENDED",   background="#0a2010", foreground="#00ff88")
        self.log_tree.tag_configure("STARTED", background="#1a1600", foreground="#ffd166")
        self.log_tree.pack(fill=BOTH, expand=True)

    # ────────────────────────────────────────────────
    # COORDINATE PICKER
    # ────────────────────────────────────────────────
    def _pick_coordinate(self, key):
        self.coord_target = key
        self.coord_status.config(
            text=f"⏳  Minimizing... click your target on screen  (picking: {key})",
            fg=self.WARN)
        self.root.after(800, self._start_mouse_listener)

    def _start_mouse_listener(self):
        self.root.iconify()

        def on_click(x, y, button, pressed):
            if pressed:
                key = self.coord_target
                if key:
                    self.coord_vars[key][0].set(int(x))
                    self.coord_vars[key][1].set(int(y))
                    self.root.after(0, lambda: self.coord_status.config(
                        text=f"✅  Captured '{key}':  X={int(x)},  Y={int(y)}",
                        fg=self.ACCENT))
                    self.root.after(300, self.root.deiconify)
                return False

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

    def _test_move(self, key):
        x = self.coord_vars[key][0].get()
        y = self.coord_vars[key][1].get()
        pyautogui.moveTo(x, y, duration=0.4)
        self.coord_status.config(
            text=f"🖱️  Mouse moved to ({x}, {y})", fg=self.ACCENT2)

    def _save_coords(self):
        for key, (x_var, y_var) in self.coord_vars.items():
            self.config[key] = [x_var.get(), y_var.get()]
        self.config["initial_delay"] = self.delay_var.get()
        self.config["excel_path"]    = self.excel_var.get()
        save_config(self.config)
        self.coord_status.config(text="✅  All coordinates saved!", fg=self.ACCENT)
        messagebox.showinfo("Saved", "✅ Coordinates saved to dialer_config.json")

    # ────────────────────────────────────────────────
    # DIALER LOGIC
    # ────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if path:
            self.excel_var.set(path)
            self.config["excel_path"] = path

    def _load_numbers(self):
        path = self.excel_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Please select a valid Excel file first.")
            return
        try:
            df = pd.read_excel(path)
            df.columns = df.columns.str.strip()

            possible_columns = ['Phone', 'phone', 'PHONE', 'Phone Number', 'Mobile', 'Number']
            phone_col = None
            for col in df.columns:
                if col.strip() in possible_columns:
                    phone_col = col
                    break

            if phone_col is None:
                messagebox.showerror("Error",
                    f"No phone column found.\nAvailable: {list(df.columns)}\n\n"
                    "Rename your column to: Phone, Mobile, or Number")
                return

            df = df[df[phone_col].notna()]
            df[phone_col] = (df[phone_col].astype(str)
                             .str.replace(r'\D+', '', regex=True).str.strip())
            df = df[df[phone_col] != ""]
            all_contacts = [p for p in df[phone_col] if len(p) == 10]

            if not all_contacts:
                messagebox.showerror("Error", "No valid 10-digit numbers found.")
                return

            completed = get_completed_numbers()
            self.contacts = [p for p in all_contacts
                             if f"+1{p}" not in completed and p not in completed]
            self.current_index = 0

            total = len(all_contacts)
            done  = len(completed)
            rem   = len(self.contacts)

            self.lbl_total.config(text=str(total))
            self.lbl_done.config(text=str(done))
            self.lbl_remaining.config(text=str(rem))
            self._update_progress(total - rem, total)
            self._log(f"✅ Loaded {total} | Done: {done} | Remaining: {rem}")

            if rem == 0:
                messagebox.showinfo("All Done", "All numbers in this file are already completed!")
            else:
                self.btn_start.config(state=NORMAL)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _start_dialer(self):
        if not self.contacts:
            messagebox.showwarning("Warning", "No contacts loaded.")
            return
        self.config["initial_delay"] = self.delay_var.get()
        self.config["excel_path"]    = self.excel_var.get()
        save_config(self.config)

        self.running = True
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.btn_next.config(state=NORMAL)
        self._set_status("STARTING", self.WARN)

        threading.Thread(target=self._dialer_thread, daemon=True).start()

    def _dialer_thread(self):
        delay = self.config.get("initial_delay", 5)
        self._log(f"🚀 Starting in {delay}s — switch to your calling window now!")
        for i in range(delay, 0, -1):
            self._log(f"   ⏳ {i}...")
            time.sleep(1)
        if not self.running:
            return
        self._make_call(self.contacts[self.current_index])
        self._set_status("ACTIVE", self.ACCENT)

        def on_press(key):
            try:
                if key.char and key.char.lower() == 'x' and self.running:
                    self._log("⌨️  X pressed → Hangup + Next")
                    threading.Thread(target=self._hangup_and_next, daemon=True).start()
            except AttributeError:
                if key == keyboard.Key.esc:
                    self._stop_dialer()
                    return False

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        self.listener.join()

    def _make_call(self, number):
        formatted = f"+1{number}" if len(number) == 10 else number
        cfg = self.config
        self._log(f"📞 Dialing {formatted} ...")
        self.root.after(0, lambda: self.lbl_current.config(text=f"Calling: {formatted}"))

        nx, ny = cfg["number_field"]
        pyautogui.click(nx, ny, clicks=2)
        time.sleep(random.uniform(0.2, 0.4))
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(random.uniform(0.15, 0.3))
        pyautogui.write(formatted, interval=TYPE_DELAY)
        time.sleep(random.uniform(0.2, 0.35))

        cx, cy = cfg["call_button"]
        pyautogui.click(cx, cy, clicks=2)
        self.call_active = True
        log_call(formatted, "STARTED")
        self._log(f"✅ Call started: {formatted}")

    def _hangup_call(self):
        if self.call_active:
            ex, ey = self.config["end_call_button"]
            pyautogui.click(ex, ey)
            time.sleep(0.7)
            self.call_active = False
            self._log("📴 Call ended")

    def _hangup_and_next(self):
        if self.current_index >= len(self.contacts):
            return
        prev      = self.contacts[self.current_index]
        formatted = f"+1{prev}" if len(prev) == 10 else prev
        self._hangup_call()
        log_call(formatted, "ENDED")
        self._log(f"📝 Logged ENDED: {formatted}")

        self.current_index += 1
        total  = len(self.contacts)
        done_n = len(get_completed_numbers())
        rem    = max(total - self.current_index, 0)

        self.root.after(0, lambda: self.lbl_done.config(text=str(done_n)))
        self.root.after(0, lambda: self.lbl_remaining.config(text=str(rem)))
        self._update_progress(self.current_index, total)
        self.root.after(0, self._load_logs_table)

        if self.current_index >= total:
            self._log("🎯 All calls completed!")
            self.root.after(0, lambda: self.lbl_current.config(text="✅  All calls done!"))
            self._set_status("DONE", self.ACCENT)
            self.root.after(500, self._on_all_done)
            return

        self._make_call(self.contacts[self.current_index])

    def _manual_next(self):
        if not self.running:
            return
        threading.Thread(target=self._hangup_and_next, daemon=True).start()

    def _stop_dialer(self):
        self.running     = False
        self.call_active = False
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        self.root.after(0, lambda: self.btn_start.config(state=NORMAL))
        self.root.after(0, lambda: self.btn_stop.config(state=DISABLED))
        self.root.after(0, lambda: self.btn_next.config(state=DISABLED))
        self.root.after(0, lambda: self.lbl_current.config(text="Stopped"))
        self._set_status("IDLE", self.MUTED)
        self._log("⛔ Dialer stopped")

    def _on_all_done(self):
        self.running = False
        self.root.after(0, lambda: self.btn_start.config(state=NORMAL))
        self.root.after(0, lambda: self.btn_stop.config(state=DISABLED))
        self.root.after(0, lambda: self.btn_next.config(state=DISABLED))
        self._load_logs_table()

        answer = messagebox.askyesnocancel(
            "🎉 All Calls Completed!",
            "All phone numbers have been dialed!\n\n"
            "YES    → Load a new Excel file\n"
            "NO     → Repeat the same list from the top\n"
            "CANCEL → Exit the application"
        )
        if answer is True:
            self._browse_file()
            self._load_numbers()
        elif answer is False:
            self._log("🔄 Repeating same list from the top...")
            self.current_index = 0
            self.lbl_remaining.config(text=str(len(self.contacts)))
            self.btn_start.config(state=NORMAL)
        else:
            self.root.quit()

    # ────────────────────────────────────────────────
    # LOGS
    # ────────────────────────────────────────────────
    def _load_logs_table(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        logs  = load_call_logs()
        ended = sum(1 for r in logs if r.get("Status") == "ENDED")
        self.root.after(0, lambda: self.lbl_log_total.config(text=f"Total: {len(logs)}"))
        self.root.after(0, lambda: self.lbl_log_ended.config(text=f"Completed: {ended}"))
        for row in reversed(logs):
            tag = row.get("Status", "")
            self.log_tree.insert("", END,
                                 values=(row.get("Time",""), row.get("Phone",""), tag),
                                 tags=(tag,))

    def _clear_logs(self):
        if messagebox.askyesno("Clear Logs", "Delete all call logs? Cannot be undone."):
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
            self._load_logs_table()
            self._log("🗑 Logs cleared")

    def _export_logs(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="call_logs_export.csv"
        )
        if path and os.path.exists(LOG_FILE):
            import shutil
            shutil.copy(LOG_FILE, path)
            messagebox.showinfo("Exported", f"Logs exported to:\n{path}")

    # ────────────────────────────────────────────────
    # UTILITY
    # ────────────────────────────────────────────────
    def _log(self, msg):
        def _write():
            self.console.configure(state=NORMAL)
            ts = datetime.now().strftime("%H:%M:%S")
            self.console.insert(END, f"[{ts}]  {msg}\n")
            self.console.see(END)
            self.console.configure(state=DISABLED)
        self.root.after(0, _write)

    def _set_status(self, text, color):
        self.root.after(0, lambda: self.status_badge.config(text=f"● {text}", fg=color))

    def _update_progress(self, done, total):
        if total > 0:
            pct = (done / total) * 100
            self.root.after(0, lambda: self.progress_bar.configure(value=pct))


# ───── ENTRY POINT ─────
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app  = AutoDialerApp(root)
    root.mainloop()
