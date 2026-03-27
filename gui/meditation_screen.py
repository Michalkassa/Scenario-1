import tkinter as tk
import time
from pathlib import Path
from PIL import Image, ImageTk, ImageOps
from colours import BG, BTN_BG, TITLE_FG, BTN_FG
from fonts import FONT_SMALL, FONT_MEDIUM, FONT_LARGE
from meditation.box_breathing import BoxBreathingSession
from .sound import sound_manager

BG_IMAGE_PATH = Path(__file__).parent.parent / "static" / "meditation_bg.jpg"


# ── Constants ──
CANVAS_SIZE   = 220
BOX_RADIUS    = 80
MAX_BEND      = 30
BEZIER_STEPS  = 80
PHASE_SECS    = 4

# Bend animation 
BEND_FRAME_MS = 16
BEND_TOTAL    = 150

# Dot smooth interpolation 
DOT_FRAME_MS  = 16
DOT_RADIUS    = 8

PHASE_COLOUR = {
    "Inhale": "#6AAFE6",
    "Hold":   "#A8D5BA",
    "Exhale": "#A8D5BA",
    "Rest":   "#6AAFE6",
}

PHASE_SIDE = {"Inhale": 0, "Hold": 1, "Exhale": 2, "Rest": 3}


def _ease(t):
    return t * t * (3 - 2 * t)


def _bezier_pt(p0, p1, p2, t):
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return (x, y)


def _bezier(p0, p1, p2, steps=BEZIER_STEPS):
    return [_bezier_pt(p0, p1, p2, i / steps) for i in range(steps + 1)]


def _get_sides(bend):
    cx = cy = CANVAS_SIZE // 2
    r  = BOX_RADIUS
    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r
    d = bend * MAX_BEND
    return [
        ((x0, y0), (cx,     y0 - d), (x1, y0)),  # 0: top    Inhale
        ((x1, y0), (x1 + d, cy    ), (x1, y1)),  # 1: right  Hold
        ((x1, y1), (cx,     y1 + d), (x0, y1)),  # 2: bottom Exhale
        ((x0, y1), (x0 - d, cy    ), (x0, y0)),  # 3: left   Rest
    ]


class MeditationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        self._session      = None
        self._bg_photo     = None   # keep reference to prevent GC

        # Bend state
        self._bend_job     = None
        self._bend_frame   = 0
        self._bend         = 0.0
        self._start_bend   = 0.0
        self._target_bend  = 0.0
        self._phase_colour = PHASE_COLOUR["Inhale"]

        
        self._dot_side        = 0
        self._dot_t           = 0.0
        self._dot_phase_start = 0.0
        self._dot_job         = None
        self._dot_running     = False

        cx = cy = CANVAS_SIZE // 2
        self._dot_pos = (cx - BOX_RADIUS, cy - BOX_RADIUS)

        self._build_ui()

    # ── UI ──

    def _build_ui(self):
        # ── Background image ──
        self._bg_label = tk.Label(self, bg=BG)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.after(1, self._load_bg)

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=40, pady=(10, 0))
        tk.Label(header, text="Meditation", font=FONT_MEDIUM,
                 fg='#5CDB95', bg=BG).pack(side="left")
        tk.Button(header, text="Home", font=FONT_SMALL,
                  fg='#5CDB95', bg=BG, relief="flat", bd=0,
                  command=self._go_back).pack(side="right")

        tk.Label(self, text="Box Breathing", font=FONT_LARGE,
                 fg='#5CDB95', bg=BG).pack(pady=(12, 2))
        tk.Label(self, text="Inhale · Hold · Exhale · Rest  —  4 seconds each",
                 font=FONT_SMALL, fg='#5CDB95', bg=BG).pack()

        dur_row = tk.Frame(self, bg=BG, highlightthickness=0)
        dur_row.pack(pady=(4, 0))
        tk.Label(dur_row, text="Duration (minutes):", font=FONT_SMALL,
                 fg='#5CDB95', bg=BG).pack(side="left", padx=(0, 10))
        self._duration_var = tk.StringVar(value="5")
        tk.Entry(dur_row, textvariable=self._duration_var,
                 font=FONT_SMALL, fg='#5CDB95', bg='#2B2D3A',
                 insertbackground=TITLE_FG, relief="flat", bd=0,
                 width=4, justify="center").pack(side="left", ipady=6, ipadx=6)

        self._canvas = tk.Canvas(self, width=CANVAS_SIZE, height=CANVAS_SIZE,
                                 bg=BG, highlightthickness=0)
        self._canvas.pack(pady=(4, 0))
        self._redraw()

        self._phase_label = tk.Label(self, text="", font=("Georgia", 22),
                                     fg='#5CDB95', bg=BG, relief="flat", bd=0, highlightthickness=0)

        ctrl = tk.Frame(self, bg=BG, highlightthickness=0)
        ctrl.pack(pady=(24, 0))
        self._start_btn = tk.Button(ctrl, text="Start", font=FONT_SMALL,
                                    fg="#5CDB95", bg=BG, relief="raised", bd=1,
                                    padx=30, pady=12, command=self._start_session,
                                    activebackground=BG, activeforeground="#5CDB95")
        self._start_btn.pack(side="left", padx=12)
        self._stop_btn = tk.Button(ctrl, text="Stop", font=FONT_SMALL,
                                   fg="#5CDB95", bg=BG, relief="raised", bd=1,
                                   padx=30, pady=12, state="disabled",
                                   command=self._stop_session,
                                   activebackground=BG, activeforeground="#5CDB95")
        self._stop_btn.pack(side="left", padx=12)

        self._feedback = tk.Label(self, text="", font=FONT_SMALL,
                                  fg='#5CDB95', bg=BG, relief="flat", bd=0, highlightthickness=0)

    def _load_bg(self):
        if not BG_IMAGE_PATH.exists():
            return
        img = Image.open(BG_IMAGE_PATH)
        img = ImageOps.fit(img, (800, 600))
        self._bg_photo = ImageTk.PhotoImage(img)
        self._bg_label.configure(image=self._bg_photo)

    # ── Drawing ──

    def _redraw(self):
        self._canvas.delete("all")
        cx = cy = CANVAS_SIZE // 2
        r  = BOX_RADIUS
        x0, y0 = cx - r, cy - r
        x1, y1 = cx + r, cy + r
        colour = self._phase_colour

        sides = _get_sides(self._bend)
        all_pts = []
        for p0, ctrl, p2 in sides:
            all_pts.extend(_bezier(p0, ctrl, p2))

        flat = [c for pt in all_pts for c in pt]
        self._canvas.create_polygon(flat, outline=colour, width=4,
                                    fill='', smooth=True)

        dot = 7
        for px, py in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            self._canvas.create_oval(px-dot, py-dot, px+dot, py+dot,
                                     fill=colour, outline="")

        dx, dy = self._dot_pos
        r2 = DOT_RADIUS
        self._canvas.create_oval(dx-r2*2, dy-r2*2, dx+r2*2, dy+r2*2,
                                 fill="#4a4e70", outline="")
        self._canvas.create_oval(dx-r2, dy-r2, dx+r2, dy+r2,
                                 fill=TITLE_FG, outline="")

    # ── Bend animation ──

    def _start_bend_animation(self, target_bend, colour, animate):
        if self._bend_job:
            self.after_cancel(self._bend_job)
            self._bend_job = None
        self._phase_colour = colour
        if not animate:
            self._bend = target_bend
            self._redraw()
            return
        self._bend_frame  = 0
        self._start_bend  = self._bend
        self._target_bend = target_bend
        self._bend_step()

    def _bend_step(self):
        if self._bend_frame > BEND_TOTAL:
            return
        t = _ease(self._bend_frame / BEND_TOTAL)
        self._bend = self._start_bend + (self._target_bend - self._start_bend) * t
        self._bend_frame += 1
        self._bend_job = self.after(BEND_FRAME_MS, self._bend_step)

    # ── Dot ──

    def _start_dot_phase(self, side):
        """Called when a new phase begins — records the wall-clock start time."""
        self._dot_side        = side
        self._dot_phase_start = time.monotonic()
        if not self._dot_running:
            self._dot_running = True
            self._dot_tick()

    def _dot_tick(self):
        if not self._dot_running:
            return
        # t = elapsed / phase_duration, clamped to [0, 1]
        elapsed = time.monotonic() - self._dot_phase_start
        t = min(elapsed / PHASE_SECS, 1.0)

        sides = _get_sides(self._bend)
        p0, ctrl, p2 = sides[self._dot_side]
        self._dot_pos = _bezier_pt(p0, ctrl, p2, t)
        self._redraw()

        self._dot_job = self.after(DOT_FRAME_MS, self._dot_tick)

    def _stop_dot(self):
        self._dot_running = False
        if self._dot_job:
            self.after_cancel(self._dot_job)
            self._dot_job = None

    # ── Session control ──

    def _start_session(self):
        try:
            minutes = int(self._duration_var.get())
            if minutes <= 0:
                raise ValueError
        except ValueError:
            self._feedback.configure(text="Please enter a valid number of minutes.")
            self._feedback.pack(pady=(4, 0))
            return
        self._feedback.pack_forget()
        self._feedback.configure(text="")
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._session = BoxBreathingSession(
            duration_minutes=minutes,
            on_phase=self._on_phase,
            on_tick=self._on_tick,
            on_finish=self._on_finish,
        )
        self._session.start()

    def _stop_session(self):
        if self._session:
            self._session.stop()
            self._session = None
        self._stop_dot()
        self._reset_ui()

    def _go_back(self):
        self._stop_session()
        self.controller.show_frame("HomeScreen")

    # ── Callbacks from background thread ──

    def _on_phase(self, phase_name, total_seconds):
        colour = PHASE_COLOUR[phase_name]
        side   = PHASE_SIDE[phase_name]

        if phase_name == "Inhale":
            target_bend, animate = +1.0, True
        elif phase_name == "Hold":
            target_bend, animate = +1.0, False
        elif phase_name == "Exhale":
            target_bend, animate = -1.0, True
        else:  # Rest
            target_bend, animate = -1.0, False

        self.after(0, lambda: (self._phase_label.configure(text=phase_name), 
                               self._phase_label.pack(pady=(4, 2))))
        self.after(0, lambda b=target_bend, c=colour, a=animate:
                   self._start_bend_animation(b, c, a))
        
        
        phase_start = time.monotonic()
        self.after(0, lambda s=side, ps=phase_start: self._on_phase_ui(s, ps))

    def _on_phase_ui(self, side, phase_start):
        self._dot_side        = side
        self._dot_phase_start = phase_start
        if not self._dot_running:
            self._dot_running = True
            self._dot_tick()

    def _on_tick(self, phase_name, seconds_left):
        pass

    def _on_finish(self):
        self.after(0, self._session_complete)

    def _session_complete(self):
        self._stop_dot()
        self._phase_label.configure(text="Session complete ✓")
        self._phase_label.pack(pady=(4, 2))
        self._feedback.configure(text="Well done — take a moment to notice how you feel.")
        self._feedback.pack(pady=(4, 0))
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._bend = 0.0
        self._redraw()
        self._session = None
        sound_manager.play_friendly_chime()

    def _reset_ui(self):
        if self._bend_job:
            self.after_cancel(self._bend_job)
            self._bend_job = None
        self._phase_label.pack_forget()
        self._phase_label.configure(text="")
        self._feedback.pack_forget()
        self._feedback.configure(text="")
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._bend    = 0.0
        cx = cy = CANVAS_SIZE // 2
        self._dot_pos = (cx - BOX_RADIUS, cy - BOX_RADIUS)
        self._redraw()