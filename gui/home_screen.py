import tkinter as tk
from PIL import Image, ImageTk, ImageOps
from pathlib import Path
from services.weather_api import getData, getLocation, getTemperature, getHumidity
from colours import BG, BTN_BG, TITLE_FG, BTN_FG
from fonts import FONT_SMALL, FONT_MEDIUM , FONT_LARGE


class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.grid_propagate(False)
        self.update_idletasks()
        self.image_path = Path(__file__).parent.parent / "static" / "thumbnail.jpg"

        self.columnconfigure(0, weight=2, uniform="equal")
        self.columnconfigure(1, weight=3, uniform="equal")
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        left_panel = tk.Frame(self, bg=BG)
        left_panel.grid(row=0, column=0, rowspan=4, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=2)
        left_panel.rowconfigure(1, weight=1)
        left_panel.rowconfigure(2, weight=1)
        left_panel.rowconfigure(3, weight=1)

        title_block = tk.Frame(left_panel, bg=BG)
        title_block.grid(row=0, column=0, sticky="nsew", padx=40, pady=(50, 10))

        tk.Label(
            title_block,
            text="MindfulDesk",
            font=FONT_LARGE,
            fg=TITLE_FG,
            bg=BG,
            anchor="w"
        ).pack(anchor="w")

        tk.Label(
            title_block,
            text="Tools for focus, calm & healthy habits",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG,
            anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        tk.Frame(left_panel, bg=BTN_BG, height=1).grid(
            row=0, column=0, sticky="sew", padx=40
        )

        buttons = [
            ("Meditation", "MeditationScreen"),
            ("Timers",     "TimerScreen"),
            ("Hydration",  "HydrationScreen"),
            ("Settings",   "SettingsScreen"),
        ]
        for i, (label, screen) in enumerate(buttons):
            btn = tk.Button(
                left_panel,
                text=label,
                font=FONT_SMALL,
                fg=BTN_FG,
                bg=BTN_BG,
                relief="flat",
                bd=0,
                pady=14,
                anchor="w",
                padx=30,
                command=lambda s=screen: controller.show_frame(s)
            )
            btn.grid(row=i + 1, column=0, sticky="ew", padx=40, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BTN_BG))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BTN_BG))

        right_panel = tk.Frame(self, bg=BG)
        right_panel.grid(row=0, column=1, rowspan=4, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=0)

        self.image_label = tk.Label(
            right_panel, bg=BG,
            padx=0, pady=0, borderwidth=0, highlightthickness=0
        )
        self.image_label.grid(row=0, column=0, rowspan=2, sticky="nsew")

        tk.Frame(right_panel, bg=BTN_BG, height=1).grid(row=1, column=0, sticky="new")

        weather_bar = tk.Frame(right_panel, bg=BG, pady=20)
        weather_bar.grid(row=1, column=0, sticky="sew")
        weather_bar.columnconfigure(0, weight=1)
        weather_bar.columnconfigure(1, weight=0)

        left_weather = tk.Frame(weather_bar, bg=BG)
        left_weather.grid(row=0, column=0, sticky="w", padx=28)

        self.lbl_city = tk.Label(
            left_weather,
            text="—",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG,
            anchor="w"
        )
        self.lbl_city.pack(anchor="w")

        self.lbl_temp = tk.Label(
            left_weather,
            text="--°C",
            font=FONT_LARGE,
            fg=TITLE_FG,
            bg=BG,
            anchor="w"
        )
        self.lbl_temp.pack(anchor="w")

        self.lbl_feels = tk.Label(
            left_weather,
            text="Feels like --°C",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG,
            anchor="w"
        )
        self.lbl_feels.pack(anchor="w")

        right_weather = tk.Frame(weather_bar, bg=BG)
        right_weather.grid(row=0, column=1, sticky="e", padx=28)

        self.lbl_humidity = tk.Label(
            right_weather,
            text="Humidity\n--",
            font=FONT_SMALL,
            fg=TITLE_FG,
            bg=BG,
            justify="right"
        )
        self.lbl_humidity.pack(anchor="e")

        self.after(1, self.load_image)

    def load_image(self):
        w = self.image_label.winfo_width()
        h = self.image_label.winfo_height()
        if w < 2 or h < 2:
            self.after(50, self.load_image)
            return
        img = Image.open(self.image_path)
        img = ImageOps.fit(img, (w, h))
        image = ImageTk.PhotoImage(img)
        self.image_label.configure(image=image, width=w, height=h)
        self.image_label.image = image

    def load_weather(self):
        try:
            data = getData()
            city, country = getLocation(data)
            temp, feels_like = getTemperature(data)
            humidity = getHumidity(data)

            self.lbl_city.configure(text=f"{city}, {country}")
            self.lbl_temp.configure(text=f"{round(temp)}°C")
            self.lbl_feels.configure(text=f"Feels like {round(feels_like)}°C")
            self.lbl_humidity.configure(text=f"Humidity\n{humidity}%")
        except Exception as e:
            self.lbl_city.configure(text="Weather unavailable")
            self.lbl_temp.configure(text="--°C")
            self.lbl_feels.configure(text="--")
            self.lbl_humidity.configure(text="try changing location in settings")
            print(f"Weather error: {e}")

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.load_weather()