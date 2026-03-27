import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path

from colours import BG, BTN_FG, TITLE_FG, BTN_BG
from fonts import FONT_SMALL, FONT_MEDIUM, FONT_LARGE
from .sound import sound_manager

from services.weather_api import get_data, get_temperature, get_humidity
from hydration.hydration_calculator import calculate_goal, ActivityLevel

SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"


class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.available_tracks = sound_manager.list_music_tracks()
        self.track_options = ["None"] + self.available_tracks
        self.sound_enabled_var = tk.BooleanVar(value=True)
        self.sound_volume_var = tk.IntVar(value=sound_manager.get_volume())
        self.background_track_var = tk.StringVar(value="None")

        # Create scrollable canvas
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        outer = tk.Frame(canvas, bg=BG)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=1)
        
        canvas_window = canvas.create_window((0, 0), window=outer, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=40, pady=(20, 16))
        scrollbar.pack(side="right", fill="y")
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width() - 40)
        
        outer.bind("<Configure>", on_configure)
        self.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))

        tk.Label(
            outer,
            text="Settings",
            font=FONT_LARGE,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        tk.Button(
            outer,
            text="Home",
            font=FONT_SMALL,
            fg='#5CDB95',
            bg=BG,
            relief="flat",
            bd=0,
            command=lambda: controller.show_frame("HomeScreen")
        ).grid(row=0, column=1, sticky="e", pady=(0, 20))

        left = tk.Frame(outer, bg=BG)
        left.grid(row=1, column=0, sticky="nw", padx=(0, 40))

        right = tk.Frame(outer, bg=BG)
        right.grid(row=1, column=1, sticky="nw")

        def separator(parent, row):
            ttk.Separator(parent, orient="horizontal").grid(
                row=row, column=0, columnspan=2, sticky="ew", pady=(4, 10)
            )

        def label(parent, row, text):
            tk.Label(
                parent,
                text=text,
                font=FONT_SMALL,
                fg=TITLE_FG,
                bg=BG
            ).grid(row=row, column=0, sticky="w")

        def entry(parent, row, var, width=16):
            tk.Entry(
                parent,
                textvariable=var,
                font=FONT_SMALL,
                fg=TITLE_FG,
                bg=BTN_BG,
                insertbackground=TITLE_FG,
                relief="flat",
                bd=0,
                width=width
            ).grid(row=row, column=1, sticky="w", ipady=6, ipadx=8, padx=(10, 0), pady=4)

        def save_btn(parent, row, cmd):
            tk.Button(
                parent,
                text="Save",
                font=FONT_SMALL,
                fg=BTN_FG,
                bg=BTN_BG,
                relief="flat",
                bd=0,
                padx=18,
                pady=6,
                command=cmd
            ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 0))

        tk.Label(
            left,
            text="Location",
            font=FONT_MEDIUM,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        separator(left, 1)

        label(left, 2, "City")
        self.city_var = tk.StringVar()
        entry(left, 2, self.city_var, 20)

        self.city_feedback = tk.Label(left, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.city_feedback.grid(row=3, column=0, columnspan=2, sticky="w")

        save_btn(left, 4, self.save_location)

        tk.Label(
            left,
            text="Manual Goal",
            font=FONT_MEDIUM,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(24, 0))

        separator(left, 6)

        label(left, 7, "Goal (ml)")
        self.manual_goal_var = tk.StringVar()
        entry(left, 7, self.manual_goal_var)

        self.manual_feedback = tk.Label(left, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.manual_feedback.grid(row=8, column=0, columnspan=2, sticky="w")

        save_btn(left, 9, self.save_manual_goal)

        tk.Label(
            right,
            text="Calculated Goal",
            font=FONT_MEDIUM,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        separator(right, 1)

        label(right, 2, "Weight (kg)")
        self.weight_var = tk.StringVar()
        entry(right, 2, self.weight_var)

        label(right, 3, "Height (cm)")
        self.height_var = tk.StringVar()
        entry(right, 3, self.height_var)

        label(right, 4, "Activity")
        self.activity_var = tk.StringVar(value="Moderate")

        menu = tk.OptionMenu(
            right,
            self.activity_var,
            "Sedentary",
            "Light",
            "Moderate",
            "Vigorous",
            "Elite"
        )

        menu.config(
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BTN_BG,
            activebackground=BTN_BG,
            relief="flat",
            bd=0
        )

        menu["menu"].config(font=FONT_SMALL, bg=BTN_BG, fg=TITLE_FG)

        menu.grid(row=4, column=1, sticky="w", padx=(10, 0), pady=4)

        label(right, 5, "Exercise (hrs/day)")
        self.exercise_var = tk.StringVar()
        entry(right, 5, self.exercise_var)

        self.calc_feedback = tk.Label(right, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.calc_feedback.grid(row=6, column=0, columnspan=2, sticky="w")

        save_btn(right, 7, self.save_calculated_goal)

        tk.Label(
            right,
            text="Sound",
            font=FONT_MEDIUM,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(24, 0))

        separator(right, 9)

        sound_row = tk.Frame(right, bg=BG)
        sound_row.grid(row=10, column=0, columnspan=2, sticky="w")

        tk.Label(sound_row, text="♪", font=("Georgia", 20), fg=TITLE_FG, bg=BG).pack(side="left", padx=(0, 8))

        tk.Checkbutton(
            sound_row,
            text="Enable audio",
            variable=self.sound_enabled_var,
            command=self._on_sound_toggle,
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG,
            activebackground=BG,
            activeforeground=TITLE_FG,
            selectcolor=BG,
            relief="flat",
            bd=0
        ).pack(side="left")

        label(right, 11, "Volume")
        tk.Scale(
            right,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.sound_volume_var,
            command=self._on_volume_change,
            fg=TITLE_FG,
            bg=BG,
            activebackground=BG,
            highlightthickness=0,
            troughcolor=BTN_BG,
            length=190
        ).grid(row=11, column=1, sticky="w", padx=(10, 0), pady=4)

        label(right, 12, "Background track")
        self.track_menu = self._build_track_menu(right, self.background_track_var)
        self.track_menu.grid(row=12, column=1, sticky="w", padx=(10, 0), pady=4)

        self.sound_feedback = tk.Label(right, text="", font=FONT_SMALL, fg=TITLE_FG, bg=BG)
        self.sound_feedback.grid(row=13, column=0, columnspan=2, sticky="w")

        save_btn(right, 14, self.save_sound_settings)

        self.load_settings()

    def load_settings(self):
        if not SETTINGS_PATH.exists():
            self.sound_enabled_var.set(sound_manager.is_enabled())
            self.sound_volume_var.set(sound_manager.get_volume())
            self.background_track_var.set(self._display_track(sound_manager.get_background_track()))
            return
        with open(SETTINGS_PATH) as f:
            data = json.load(f)
        self.city_var.set(data.get("city", ""))
        if data.get("goal"):
            self.manual_goal_var.set(data["goal"])
        self.sound_enabled_var.set(bool(data.get("sound_enabled", True)))
        self.sound_volume_var.set(int(data.get("sound_volume", sound_manager.get_volume())))
        self.background_track_var.set(self._display_track(sound_manager.get_background_track()))

    def _build_track_menu(self, parent, variable):
        menu = tk.OptionMenu(parent, variable, *self.track_options)
        menu.config(
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BTN_BG,
            activebackground=BTN_BG,
            relief="flat",
            bd=0,
            width=16
        )
        menu["menu"].config(font=FONT_SMALL, bg=BTN_BG, fg=TITLE_FG)
        return menu

    def _display_track(self, track_name):
        if track_name and track_name in self.track_options:
            return track_name
        return "None"

    def _selected_track_value(self, variable):
        selected = variable.get().strip()
        if selected == "None":
            return ""
        return selected

    def _load_data(self):
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH) as f:
                return json.load(f)
        return {}

    def _write_data(self, updates):
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = self._load_data()
        data.update(updates)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def save_location(self):
        city = self.city_var.get().strip()
        if not city:
            self.city_feedback.configure(text="Enter a city")
            return
        self._write_data({"city": city})
        self.city_feedback.configure(text="Saved")

    def save_manual_goal(self):
        try:
            goal = int(self.manual_goal_var.get())
        except ValueError:
            self.manual_feedback.configure(text="Enter a number")
            return
        self._write_data({"goal": goal})
        self.manual_feedback.configure(text=f"Saved — {goal} ml")

    def save_calculated_goal(self):
        try:
            data = get_data()
            goal_litres = calculate_goal(
                BW=float(self.weight_var.get()),
                H=float(self.height_var.get()),
                PA=ActivityLevel[self.activity_var.get().upper()],
                D_ex=float(self.exercise_var.get()),
                T= get_temperature(data) or 20,
                RH= get_humidity(data) or 50,
            )
            goal = int(goal_litres * 1000)
        except (ValueError or KeyError) as e:
            print(e)
            self.calc_feedback.configure(text="Fill all fields")
            return
        self._write_data({"goal": goal})
        self.calc_feedback.configure(text=f"Saved — {goal} ml")

    def _on_sound_toggle(self):
        enabled = bool(self.sound_enabled_var.get())
        sound_manager.set_enabled(enabled)

    def _on_volume_change(self, value):
        try:
            sound_manager.set_volume(int(float(value)))
        except (TypeError, ValueError):
            pass

    def save_sound_settings(self):
        enabled = bool(self.sound_enabled_var.get())
        volume = int(self.sound_volume_var.get())
        background_track = self._selected_track_value(self.background_track_var)
        self._write_data(
            {
                "sound_enabled": enabled,
                "sound_volume": volume,
                "music_track_global": background_track,
            }
        )
        sound_manager.set_enabled(enabled)
        sound_manager.set_volume(volume)
        sound_manager.set_background_track(background_track)
        sound_manager.refresh_active_music()
        self.sound_feedback.configure(text="Saved")