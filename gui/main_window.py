import tkinter as tk

from .home_screen import HomeScreen
from .hydration_screen import HydrationScreen
from .meditation_screen import MeditationScreen
from .timer_screen import TimerScreen

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MindfulDesk")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (HomeScreen, HydrationScreen, MeditationScreen, TimerScreen ):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()