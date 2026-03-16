import tkinter as tk
import json
from pathlib import Path
from colours import BG, BTN_FG, TITLE_FG, BTN_BG
from fonts import FONT_SMALL, FONT_MEDIUM, FONT_LARGE

SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"

class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        container = tk.Frame(self, bg=BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Settings", font=FONT_LARGE, fg=TITLE_FG, bg=BG).pack(anchor="w", pady=(0, 24))
        tk.Label(container, text="Weather location", font=FONT_MEDIUM, fg=TITLE_FG, bg=BG).pack(anchor="w", pady=(0, 6))

        self.city_var = tk.StringVar()
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH) as f:
                self.city_var.set(json.load(f).get("city", ""))

        tk.Entry(
            container,
            textvariable=self.city_var,
            font=FONT_MEDIUM,
            fg=TITLE_FG,
            bg=BTN_BG,
            insertbackground=TITLE_FG,
            relief="flat",
            bd=0,
            width=28
        ).pack(ipady=10, ipadx=12, pady=(0, 16))

        self.feedback = tk.Label(container, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.feedback.pack(anchor="w", pady=(0, 8))

        btn = tk.Button(
            container,
            text="Save",
            font=FONT_MEDIUM,
            fg=BTN_FG,
            bg=BTN_BG,
            relief="flat",
            bd=0,
            padx=24,
            pady=9,
            command=self.on_save
        )
        btn.pack(anchor="w")

        tk.Button(
            container,
            text="← Back",
            font=FONT_SMALL,
            fg=BTN_FG,
            bg=BG,
            relief="flat",
            bd=0,
            pady=8,
            command=lambda: controller.show_frame("HomeScreen")
        ).pack(anchor="w", pady=(10, 0))

    def on_save(self):
        city = self.city_var.get().strip()
        if not city:
            self.feedback.configure(text="Please enter a city.")
            return
        with open(SETTINGS_PATH, "w") as f:
            json.dump({"city": city}, f, indent=2)
        self.feedback.configure(text=f"Saved — {city}")