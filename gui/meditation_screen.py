import tkinter as tk

class MeditationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Meditation Screen", font=("Arial", 14, "bold")).pack()

        tk.Button(self, text="Home", width=20, height=2,
                  command=lambda: controller.show_frame("HomeScreen")).pack()
        