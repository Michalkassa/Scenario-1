import tkinter as tk

from colours import BG, BTN_BG, TITLE_FG
from fonts import FONT_LARGE, FONT_SMALL
from .sound import sound_manager

class TimerScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        self.work_color = "#F2A65A"
        self.break_color = "#4CB5AE"
        self.complete_color = "#59C173"
        self.idle_color = TITLE_FG
        self.button_bg = "#FFFFFF"
        self.button_fg = BTN_BG
        self._active_timer = "pomodoro"
        self._pulse_toggle = False
        self.timers = {
            "pomodoro": {"after_id": None, "running": False, "phase": "Work", "seconds_left": 0, "phase_total": 0, "cycles_left": 0, "total_cycles": 0, "color_work": self.work_color, "color_break": self.break_color},
            "simple": {"after_id": None, "running": False, "seconds_left": 0, "initial_seconds": 0, "color": self.break_color},
        }

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        top_bar = tk.Frame(self, bg=BG)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(14, 8))
        top_bar.columnconfigure(0, weight=1)
        top_bar.columnconfigure(1, weight=2)
        top_bar.columnconfigure(2, weight=1)

        tk.Button(top_bar, text="Home", font=FONT_SMALL, fg='#5CDB95', bg=BG,
                  relief="flat", bd=0, command=self._go_home).grid(row=0, column=2, sticky="e")
        tk.Label(top_bar, text="Timers", font=FONT_LARGE, fg=TITLE_FG, bg=BG).grid(row=0, column=1)

        self._build_ui(0, "pomodoro", [("Work (min)", "work_var", "25"), ("Break (min)", "break_var", "5"), ("Cycles", "cycles_var", "4")])
        self._build_ui(1, "simple", [("Hours", "hours_var", "0"), ("Minutes", "minutes_var", "10"), ("Seconds", "seconds_var", "0")])

        self.bind_all("<space>", self._handle_space)
        self.bind_all("<Escape>", self._handle_escape)
        self.bind_all("<r>", self._handle_reset)

    def _build_ui(self, col, timer_name, inputs):
        panel = tk.Frame(self, bg=BG, highlightthickness=1, highlightbackground=BTN_BG)
        panel.grid(row=1, column=col, sticky="nsew", padx=(20 if col == 0 else 10, 10 if col == 0 else 20), pady=12)
        panel.columnconfigure(1, weight=1)
        heading_text = "Pomodoro - Work" if timer_name == "pomodoro" else "Simple Timer"
        heading_color = self.work_color if timer_name == "pomodoro" else self.idle_color
        heading_var = tk.StringVar(value=heading_text)
        heading_label = tk.Label(panel, textvariable=heading_var, font=("Georgia", 20), fg=heading_color, bg=BG)
        heading_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))
        setattr(self, f"{timer_name}_heading_var", heading_var)
        setattr(self, f"{timer_name}_heading_label", heading_label)
        for i, (label_text, var_name, default) in enumerate(inputs, 1):
            tk.Label(panel, text=label_text, font=FONT_SMALL, fg=TITLE_FG, bg=BG).grid(row=i, column=0, sticky="w", padx=14, pady=4)
            var = tk.StringVar(value=default)
            tk.Entry(panel, textvariable=var, width=10).grid(row=i, column=1, sticky="w", padx=10, pady=4)
            setattr(self, var_name, var)
        status_var = tk.StringVar(value="Status: Idle")
        tk.Label(panel, textvariable=status_var, font=FONT_SMALL, fg=TITLE_FG, bg=BG).grid(row=len(inputs)+1, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 2))
        setattr(self, f"{timer_name}_status_var", status_var)
        controls = tk.Frame(panel, bg=BG)
        controls.grid(row=len(inputs)+2, column=0, columnspan=2, pady=(4, 8))
        for btn_text, method in [("Start", f"start_{timer_name}"), ("Pause", f"pause_{timer_name}"), ("Reset", f"reset_{timer_name}")]:
            self._make_button(controls, btn_text, 8, getattr(self, method)).pack(side="left", padx=4)
        ring = tk.Canvas(panel, width=110, height=110, bg=BG, highlightthickness=0)
        ring.grid(row=len(inputs)+3, column=0, columnspan=2, pady=(4, 0))
        setattr(self, f"{timer_name}_ring", ring)
        time_var = tk.StringVar(value="25:00" if timer_name == "pomodoro" else "00:10:00")
        time_label = tk.Label(panel, textvariable=time_var, font=("Georgia", 24), fg=TITLE_FG, bg=BG)
        time_label.grid(row=len(inputs)+4, column=0, columnspan=2, pady=(4, 10))
        setattr(self, f"{timer_name}_time_var", time_var)
        setattr(self, f"{timer_name}_time_label", time_label)

    def _make_button(self, parent, text, width, command):
        return tk.Button(parent,text=text,width=width,command=command,relief="flat",bd=0,bg=self.button_bg,fg=self.button_fg,activebackground=self.button_fg,activeforeground=self.button_bg,highlightthickness=0)

    def _draw_ring(self, canvas, progress, color):
        canvas.delete("all")
        size = 100
        x0 = y0 = 5
        x1 = y1 = x0 + size
        width = 10

        canvas.create_oval(x0, y0, x1, y1, outline=BTN_BG, width=width)
        if progress > 0:
            extent = progress * 360
            canvas.create_arc(x0,y0,x1,y1,start=90,extent=-extent,style="arc",outline=color,width=width)

    def _apply_preset(self, work, rest, cycles):
        self.work_var.set(str(work))
        self.break_var.set(str(rest))
        self.cycles_var.set(str(cycles))
        self.reset_pomodoro()

    def _go_home(self):
        self.controller.show_frame("HomeScreen")

    def _handle_space(self, event=None):
        t = self.timers[self._active_timer]
        getattr(self, f"{'pause' if t['running'] else 'start'}_{self._active_timer}")()

    def _handle_reset(self, event=None):
        getattr(self, f"reset_{self._active_timer}")()

    def _handle_escape(self, event=None):
        self._go_home()

    def _parse_positive_int(self, value, fallback):
        try:
            parsed = int(value)
            if parsed < 0:
                return fallback
            return parsed
        except (TypeError, ValueError):
            return fallback

    def _format_mm_ss(self, total_seconds):
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _format_hh_mm_ss(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def start_pomodoro(self):
        self._active_timer = "pomodoro"
        t = self.timers["pomodoro"]
        work_minutes = self._parse_positive_int(self.work_var.get(), 25)
        cycles = self._parse_positive_int(self.cycles_var.get(), 4)
        if cycles == 0:
            self.pomodoro_status_var.set("Status: Enter at least 1 cycle")
            return
        if t["seconds_left"] <= 0:
            t["phase"] = "Work"
            t["total_cycles"] = cycles
            t["cycles_left"] = cycles
            t["seconds_left"] = max(1, work_minutes * 60)
            t["phase_total"] = t["seconds_left"]
        if not t["running"]:
            t["running"] = True
            self.pomodoro_status_var.set(f"Status: {t['phase']} • Cycle {t['total_cycles'] - t['cycles_left'] + 1}/{t['total_cycles']}")
            self._tick_pomodoro()

    def _tick_pomodoro(self):
        t = self.timers["pomodoro"]
        if not t["running"]:
            return

        phase_color = self.work_color if t["phase"] == "Work" else self.break_color
        self.pomodoro_heading_var.set(f"Pomodoro - {t['phase']}")
        self.pomodoro_heading_label.configure(fg=phase_color)

        if t["phase_total"] > 0:
            progress = 1 - (t["seconds_left"] / t["phase_total"])
        else:
            progress = 0
        self._draw_ring(self.pomodoro_ring, max(0, min(1, progress)), phase_color)

        self.pomodoro_time_var.set(self._format_mm_ss(t["seconds_left"]))
        if t["seconds_left"] <= 10:
            self._pulse_toggle = not self._pulse_toggle
            self.pomodoro_time_label.configure(fg=phase_color if self._pulse_toggle else TITLE_FG)
        else:
            self.pomodoro_time_label.configure(fg=TITLE_FG)

        if t["seconds_left"] > 0:
            t["seconds_left"] -= 1
            t["after_id"] = self.after(1000, self._tick_pomodoro)
            return

        break_minutes = self._parse_positive_int(self.break_var.get(), 5)
        work_minutes = self._parse_positive_int(self.work_var.get(), 25)

        if t["phase"] == "Work":
            t["phase"] = "Break"
            t["seconds_left"] = max(1, break_minutes * 60)
            t["phase_total"] = t["seconds_left"]
        else:
            t["cycles_left"] -= 1
            if t["cycles_left"] <= 0:
                t["running"] = False
                t["after_id"] = None
                self.pomodoro_status_var.set("Status: Completed")
                self.pomodoro_time_var.set("00:00")
                self.pomodoro_heading_var.set("Pomodoro - Complete")
                self.pomodoro_heading_label.configure(fg=self.complete_color)
                self.pomodoro_time_label.configure(fg=self.complete_color)
                self._draw_ring(self.pomodoro_ring, 1, self.complete_color)
                sound_manager.play_friendly_chime()
                return
            t["phase"] = "Work"
            t["seconds_left"] = max(1, work_minutes * 60)
            t["phase_total"] = t["seconds_left"]

        self.pomodoro_status_var.set(
            f"Status: {t['phase']} • Cycle {t['total_cycles'] - t['cycles_left'] + 1}/{t['total_cycles']}"
        )
        t["after_id"] = self.after(1000, self._tick_pomodoro)

    def pause_pomodoro(self):
        t = self.timers["pomodoro"]
        t["running"] = False
        if t["after_id"] is not None:
            self.after_cancel(t["after_id"])
            t["after_id"] = None
        self.pomodoro_status_var.set("Status: Paused")

    def reset_pomodoro(self):
        self.pause_pomodoro()
        t = self.timers["pomodoro"]
        t["phase"] = "Work"
        t["total_cycles"] = self._parse_positive_int(self.cycles_var.get(), 4)
        t["cycles_left"] = 0
        t["seconds_left"] = self._parse_positive_int(self.work_var.get(), 25) * 60
        t["phase_total"] = t["seconds_left"]
        self.pomodoro_time_var.set(self._format_mm_ss(t["seconds_left"]))
        self.pomodoro_status_var.set("Status: Idle")
        self.pomodoro_heading_var.set("Pomodoro - Work")
        self.pomodoro_heading_label.configure(fg=self.work_color)
        self.pomodoro_time_label.configure(fg=TITLE_FG)
        self._draw_ring(self.pomodoro_ring, 0, self.work_color)

    def start_simple(self):
        self._active_timer = "simple"
        t = self.timers["simple"]
        if t["seconds_left"] <= 0:
            hours = self._parse_positive_int(self.hours_var.get(), 0)
            minutes = self._parse_positive_int(self.minutes_var.get(), 10)
            seconds = self._parse_positive_int(self.seconds_var.get(), 0)
            t["seconds_left"] = (hours * 3600) + (minutes * 60) + seconds
            t["initial_seconds"] = t["seconds_left"]

        if t["seconds_left"] <= 0:
            self.simple_status_var.set("Status: Enter a duration")
            return

        if not t["running"]:
            t["running"] = True
            self.simple_status_var.set("Status: Running")
            self.simple_heading_var.set("Simple Timer - Running")
            self.simple_heading_label.configure(fg=self.break_color)
            self._tick_simple()

    def _tick_simple(self):
        t = self.timers["simple"]
        if not t["running"]:
            return

        self.simple_time_var.set(self._format_hh_mm_ss(t["seconds_left"]))

        if t["initial_seconds"] > 0:
            progress = 1 - (t["seconds_left"] / t["initial_seconds"])
        else:
            progress = 0
        self._draw_ring(self.simple_ring, max(0, min(1, progress)), self.break_color)

        if t["seconds_left"] <= 10:
            self._pulse_toggle = not self._pulse_toggle
            self.simple_time_label.configure(fg=self.break_color if self._pulse_toggle else TITLE_FG)
        else:
            self.simple_time_label.configure(fg=TITLE_FG)

        if t["seconds_left"] > 0:
            t["seconds_left"] -= 1
            t["after_id"] = self.after(1000, self._tick_simple)
            return

        t["running"] = False
        t["after_id"] = None
        self.simple_status_var.set("Status: Completed")
        self.simple_heading_var.set("Simple Timer - Complete")
        self.simple_heading_label.configure(fg=self.complete_color)
        self.simple_time_label.configure(fg=self.complete_color)
        self._draw_ring(self.simple_ring, 1, self.complete_color)
        sound_manager.play_friendly_chime()

    def pause_simple(self):
        t = self.timers["simple"]
        t["running"] = False
        if t["after_id"] is not None:
            self.after_cancel(t["after_id"])
            t["after_id"] = None
        self.simple_status_var.set("Status: Paused")
        self.simple_heading_var.set("Simple Timer - Paused")
        self.simple_heading_label.configure(fg=self.idle_color)

    def reset_simple(self):
        self.pause_simple()
        t = self.timers["simple"]
        hours = self._parse_positive_int(self.hours_var.get(), 0)
        minutes = self._parse_positive_int(self.minutes_var.get(), 10)
        seconds = self._parse_positive_int(self.seconds_var.get(), 0)
        t["seconds_left"] = (hours * 3600) + (minutes * 60) + seconds
        t["initial_seconds"] = t["seconds_left"]
        self.simple_time_var.set(self._format_hh_mm_ss(t["seconds_left"]))
        self.simple_status_var.set("Status: Idle")
        self.simple_heading_var.set("Simple Timer")
        self.simple_heading_label.configure(fg=self.idle_color)
        self.simple_time_label.configure(fg=TITLE_FG)
        self._draw_ring(self.simple_ring, 0, self.break_color)