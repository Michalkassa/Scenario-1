import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    print("App running")
    root.mainloop()         

if __name__ == "__main__":
    main()