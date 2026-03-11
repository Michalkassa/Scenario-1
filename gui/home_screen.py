import tkinter as tk

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="MindfulDesk", font=("Arial", 14, "bold")).pack()
        tk.Label(self, text="Tools for focus, mindfulness, and healthy work habits", font=("Arial", 12)).pack()

        tk.Button(self, text="Meditation", width=20, height=2,
                  command=lambda: controller.show_frame("MeditationScreen")).pack()
        tk.Button(self, text="Timers", width=20, height=2,
                  command=lambda: controller.show_frame("TimerScreen")).pack()
        tk.Button(self, text="Hydration", width=20, height=2,
                  command=lambda: controller.show_frame("HydrationScreen")).pack()