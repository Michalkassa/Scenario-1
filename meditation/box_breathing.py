import threading
import time


PHASES = [
    ("Inhale",  4),
    ("Hold",    4),
    ("Exhale",  4),
    ("Rest",    4),
]


class BoxBreathingSession:

    def __init__(self, duration_minutes: int, on_phase, on_tick, on_finish):
        self.duration_seconds = duration_minutes * 60
        self.on_phase  = on_phase
        self.on_tick   = on_tick
        self.on_finish = on_finish

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run(self):
        elapsed = 0

        while elapsed < self.duration_seconds and not self._stop_event.is_set():
            for phase_name, phase_seconds in PHASES:
                if self._stop_event.is_set():
                    break
                if elapsed >= self.duration_seconds:
                    break

                self.on_phase(phase_name, phase_seconds)

                for remaining in range(phase_seconds, 0, -1):
                    if self._stop_event.is_set():
                        break
                    self.on_tick(phase_name, remaining)
                    time.sleep(1)
                    elapsed += 1
                    if elapsed >= self.duration_seconds:
                        break

        if not self._stop_event.is_set():
            self.on_finish()