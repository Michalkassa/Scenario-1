import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path

from colours import BG, BTN_FG, TITLE_FG, BTN_BG
from fonts import FONT_SMALL, FONT_MEDIUM, FONT_LARGE

from services.weather_api import get_data, get_temperature, get_humidity
from hydration.hydration_calculator import calculate_goal, ActivityLevel

SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"


class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        outer = tk.Frame(self, bg=BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            outer,
            text="Settings",
            font=FONT_LARGE,
            fg=TITLE_FG,
            bg=BG
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

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

        tk.Button(
            outer,
            text="← Back",
            font=FONT_SMALL,
            fg=BTN_FG,
            bg=BG,
            relief="flat",
            bd=0,
            command=lambda: controller.show_frame("HomeScreen")
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(20, 0))

        self.load_settings()

    def load_settings(self):
        if not SETTINGS_PATH.exists():
            return
        with open(SETTINGS_PATH) as f:
            data = json.load(f)
        self.city_var.set(data.get("city", ""))
        if data.get("goal"):
            self.manual_goal_var.set(data["goal"])

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