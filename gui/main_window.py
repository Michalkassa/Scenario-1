import tkinter as tk

from .home_screen import HomeScreen
from .hydration_screen import HydrationScreen
from .meditation_screen import MeditationScreen
from .timer_screen import TimerScreen
from .settings_screen import SettingsScreen
from .sound import sound_manager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MindfulDesk")
        self.root.geometry("800x600")
        self.root.resizable(False,False)

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.container.columnconfigure(0, weight=1) 
        self.container.rowconfigure(0, weight=1)    

        self.frames = {}

        for F in (HomeScreen, HydrationScreen, MeditationScreen, TimerScreen, SettingsScreen):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0,column=0,sticky="nsew");

        self.root.bind_class("Button", "<ButtonRelease-1>", self._on_button_release, add="+")
        self.show_frame("HomeScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        sound_manager.on_screen_change(page_name)

    def _on_button_release(self, _event):
        sound_manager.play_button_beep()