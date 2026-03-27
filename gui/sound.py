import json
import threading
from pathlib import Path

try:
    import winsound
except ImportError:  # pragma: no cover - non-Windows fallback
    winsound = None

try:
    import pygame
except ImportError:  # pragma: no cover - runtime fallback if pygame missing
    pygame = None


SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"
MUSIC_DIR = Path(__file__).parent.parent / "static" / "music"
SUPPORTED_MUSIC_EXTENSIONS = (".mp3", ".wav", ".ogg")
GLOBAL_TRACK_KEY = "music_track_global"


class SoundManager:
    """App-wide sound service: button beeps + single continuous background music."""

    def __init__(self):
        self._screen_name = None
        self._active_track = None
        self._settings_lock = threading.Lock()
        self._pygame_ready = False

    def _load_settings(self):
        if not SETTINGS_PATH.exists():
            return {}
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_settings(self, updates):
        with self._settings_lock:
            current = self._load_settings()
            current.update(updates)
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
                json.dump(current, file, indent=2)

    def _init_pygame(self):
        if self._pygame_ready:
            return True
        pg = pygame
        if pg is None:
            return False
        try:
            pg.mixer.init()
            self._pygame_ready = True
            pg.mixer.music.set_volume(self.get_volume() / 100.0)
            return True
        except Exception:
            return False

    def _stop_music(self):
        if self._pygame_ready and pygame is not None:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self._active_track = None

    def is_enabled(self):
        return bool(self._load_settings().get("sound_enabled", True))

    def set_enabled(self, enabled):
        self._save_settings({"sound_enabled": bool(enabled)})
        if not enabled:
            self._stop_music()
            return
        self.ensure_background_music()

    def get_volume(self):
        value = self._load_settings().get("sound_volume", 55)
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 55
        return max(0, min(100, value))

    def set_volume(self, value):
        value = max(0, min(100, int(value)))
        self._save_settings({"sound_volume": value})
        if self._pygame_ready and pygame is not None:
            try:
                pygame.mixer.music.set_volume(value / 100.0)
            except Exception:
                pass

    def list_music_tracks(self):
        MUSIC_DIR.mkdir(parents=True, exist_ok=True)
        track_files = []
        for file_path in MUSIC_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_MUSIC_EXTENSIONS:
                track_files.append(file_path.name)
        return sorted(track_files, key=str.lower)

    def get_background_track(self):
        tracks = self.list_music_tracks()
        if not tracks:
            return ""
        data = self._load_settings()
        # If the global track key exists, respect it (even if empty)
        if GLOBAL_TRACK_KEY in data:
            selected = data[GLOBAL_TRACK_KEY]
            if selected in tracks:
                return selected
            return selected  # Return empty string if user explicitly set "None"
        # Legacy key support: try old per-context settings
        for legacy_key in ("music_track_menu", "music_track_timer", "music_track_meditation"):
            legacy_value = data.get(legacy_key, "")
            if legacy_value in tracks:
                return legacy_value
        # Only default to first track if no setting exists at all
        return tracks[0] if tracks else ""

    def set_background_track(self, track_name):
        tracks = self.list_music_tracks()
        if track_name and track_name not in tracks:
            return
        self._save_settings({GLOBAL_TRACK_KEY: track_name})

    def refresh_active_music(self):
        self.ensure_background_music(force_reload=True)

    def ensure_background_music(self, force_reload=False):
        if not self.is_enabled():
            self._stop_music()
            return
        if not self._init_pygame():
            return
        pg = pygame
        if pg is None:
            return

        selected_track = self.get_background_track()
        if not selected_track:
            self._stop_music()
            return

        if (
            not force_reload
            and self._active_track == selected_track
            and pg.mixer.music.get_busy()
        ):
            return

        # Stop current music before loading a new track
        self._stop_music()

        candidates = [selected_track]
        candidates.extend(track for track in self.list_music_tracks() if track != selected_track)

        for track_name in candidates:
            track_path = MUSIC_DIR / track_name
            if not track_path.exists():
                continue
            try:
                pg.mixer.music.load(str(track_path))
                pg.mixer.music.set_volume(self.get_volume() / 100.0)
                pg.mixer.music.play(-1)
                self._active_track = track_name
                return
            except Exception as exc:
                print(f"Music load failed for {track_name}: {exc}")

        self._stop_music()

    # Backward-compatibility shims kept for existing callers.
    def get_track_for_context(self, _context):
        return self.get_background_track()

    def set_track_for_context(self, _context, track_name):
        self.set_background_track(track_name)

    def play_button_beep(self):
        ws = winsound
        if not self.is_enabled() or ws is None:
            return

        def _worker():
            try:
                ws.Beep(880, 35)
            except RuntimeError:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def play_friendly_chime(self):
        ws = winsound
        if not self.is_enabled() or ws is None:
            return

        def _worker():
            for note, duration_ms in ((523, 120), (659, 120), (784, 160)):
                try:
                    ws.Beep(note, duration_ms)
                except RuntimeError:
                    return

        threading.Thread(target=_worker, daemon=True).start()

    def on_screen_change(self, screen_name):
        self._screen_name = screen_name
        self.ensure_background_music()


sound_manager = SoundManager()
