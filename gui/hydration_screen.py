import tkinter as tk
import json
from pathlib import Path
from datetime import datetime
from colours import BG, BTN_FG, TITLE_FG, BTN_BG
from fonts import FONT_SMALL, FONT_MEDIUM, FONT_LARGE

HYDRATION_PATH = Path(__file__).parent.parent / "data" / "hydration.json"
SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"


class HydrationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.build_ui()

    def load_hydration_data(self):
        if HYDRATION_PATH.exists():
            with open(HYDRATION_PATH) as f:
                return json.load(f)
        return {"goal": 2000, "log": []}
    
    def load_settings_data(self):
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH) as f:
                return json.load(f)
        return {"goal": 2000, "city": "london"}

    def save_hydration_data(self, data):
        HYDRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HYDRATION_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def today_total(self, log):
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(e["amount"] for e in log if e["date"] == today)

    def build_ui(self):
        hydration_data = self.load_hydration_data()
        settings_data = self.load_settings_data()
        today_total = self.today_total(hydration_data["log"])
        goal        = settings_data["goal"]
        remaining   = max(0, goal - today_total)

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=40, pady=(20, 0))
        tk.Label(header, text="Hydration", font=FONT_MEDIUM, fg=TITLE_FG, bg=BG).pack(side="left")
        tk.Button(
            header, text="← Back", font=FONT_SMALL, fg=BTN_FG, bg=BG,
            relief="flat", bd=0,
            command=lambda: self.controller.show_frame("HomeScreen")
        ).pack(side="right")

        tk.Frame(self, bg=BTN_BG, height=1).pack(fill="x", padx=40, pady=(8, 0))

        hero = tk.Frame(self, bg=BG)
        hero.pack(fill="x", padx=40, pady=(24, 0))

        tk.Label(
            hero,
            text=f"{remaining} ml",
            font=("Georgia", 64, "bold"),
            fg=TITLE_FG,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            hero,
            text="remaining today",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            hero,
            text=f"{today_total} ml of {goal} ml consumed",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG
        ).pack(anchor="w", pady=(0, 16))

        self.bar_canvas = tk.Canvas(self, height=18, bg=BG, highlightthickness=0)
        self.bar_canvas.pack(fill="x", padx=40, pady=(0, 20))
        self.bar_canvas.bind("<Configure>", lambda e: self.draw_bar(today_total, goal))
        self.after(10, lambda: self.draw_bar(today_total, goal))

        tk.Frame(self, bg=BTN_BG, height=1).pack(fill="x", padx=40)

        log_row = tk.Frame(self, bg=BG)
        log_row.pack(fill="x", padx=40, pady=(14, 14))

        for ml in [150, 250, 330, 500]:
            tk.Button(
                log_row, text=f"{ml}", font=FONT_SMALL, fg=BTN_FG, bg=BTN_BG,
                relief="flat", bd=0, padx=16, pady=8,
                command=lambda v=ml: self.add_drink(v)
            ).pack(side="left", padx=(0, 8))

        tk.Frame(log_row, bg=BTN_BG, width=1).pack(side="left", fill="y", padx=(4, 12))

        self.drink_var = tk.StringVar()
        tk.Entry(
            log_row, textvariable=self.drink_var, font=FONT_SMALL,
            fg=TITLE_FG, bg=BTN_BG, insertbackground=TITLE_FG,
            relief="flat", bd=0, width=6
        ).pack(side="left", ipady=8, ipadx=10)

        tk.Label(log_row, text="ml", font=FONT_SMALL, fg=TITLE_FG, bg=BG).pack(side="left", padx=(6, 8))

        tk.Button(
            log_row, text="Add", font=FONT_SMALL, fg=BTN_FG, bg=BTN_BG,
            relief="flat", bd=0, padx=16, pady=8,
            command=lambda: self.add_drink(None)
        ).pack(side="left")

        self.log_feedback = tk.Label(self, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.log_feedback.pack(anchor="w", padx=40)

        tk.Frame(self, bg=BTN_BG, height=1).pack(fill="x", padx=40, pady=(10, 0))

        table_section = tk.Frame(self, bg=BG)
        table_section.pack(fill="both", expand=True, padx=40, pady=(14, 0))

        header_row = tk.Frame(table_section, bg=BTN_BG)
        header_row.pack(fill="x")
        for col, w in [("Date", 12), ("Time", 8), ("Amount", 10), ("Day total", 12), ("", 4)]:
            tk.Label(
                header_row, text=col, font=FONT_SMALL, fg=TITLE_FG, bg=BTN_BG,
                width=w, anchor="w", padx=8, pady=6
            ).pack(side="left")

        self.table_frame = tk.Frame(table_section, bg=BG)
        self.table_frame.pack(fill="x")
        self.refresh_table(hydration_data["log"])

    def draw_bar(self, consumed, goal):
        w = self.bar_canvas.winfo_width()
        if w < 2:
            return
        self.bar_canvas.delete("all")
        self.bar_canvas.create_rectangle(0, 0, w, 18, fill=BTN_BG, outline="")
        pct = min(consumed / goal, 1.0) if goal else 0
        if pct > 0:
            self.bar_canvas.create_rectangle(0, 0, int(w * pct), 18, fill=TITLE_FG, outline="")

    def refresh_table(self, log):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        recent_indices = list(reversed(range(len(log))))[:5]
        for idx in recent_indices:
            entry = log[idx]
            tk.Frame(self.table_frame, bg=BTN_BG, height=1).pack(fill="x")
            row = tk.Frame(self.table_frame, bg=BG)
            row.pack(fill="x")
            for val, w in [
                (entry["date"],                12),
                (entry["time"],                 8),
                (f"{entry['amount']} ml",      10),
                (f"{entry['daily_total']} ml", 12),
            ]:
                tk.Label(
                    row, text=val, font=FONT_SMALL, fg=TITLE_FG, bg=BG,
                    width=w, anchor="w", padx=8, pady=8
                ).pack(side="left")
            tk.Button(
                row, text="✕", font=FONT_SMALL, fg=BTN_FG, bg=BG,
                relief="flat", bd=0, padx=8, pady=4,
                command=lambda i=idx: self.delete_entry(i)
            ).pack(side="left")

    def reload(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()

    def delete_entry(self, index):
        hydration_data = self.load_hydration_data()
        hydration_data["log"].pop(index)
        self.save_hydration_data(hydration_data)
        self.reload()

    def add_drink(self, amount):
        if amount is None:
            try:
                amount = int(self.drink_var.get().strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                self.log_feedback.configure(text="Enter a valid amount.")
                return
        hydration_data = self.load_hydration_data()
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        daily_total = self.today_total(hydration_data["log"]) + amount
        hydration_data["log"].append({
            "date":        today,
            "time":        now.strftime("%H:%M"),
            "amount":      amount,
            "daily_total": daily_total,
        })
        self.save_hydration_data(hydration_data)
        self.reload()

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.reload()