"""
Universal Video Downloader — Android (Kivy)
-------------------------------------------
Paste a link, pick quality, Download. Powered by yt-dlp.

Notes:
- Built for Android via buildozer / python-for-android.
- Defaults to single-file (progressive) formats so it works WITHOUT ffmpeg on
  the device. (Bundling ffmpeg on Android is optional/advanced — see
  README_ANDROID.md.) Most sites that serve a normal MP4 work out of the box.
- Also runs on desktop for quick UI testing (storage falls back to ./Downloads).
"""

import os
import threading

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex as H
from kivy.core.window import Window

# yt-dlp is imported lazily/guarded so a problem loading it can never stop the
# app from opening — we surface it in the UI instead.
try:
    import yt_dlp
    _YTDLP_ERR = None
except Exception as _e:  # pragma: no cover
    yt_dlp = None
    _YTDLP_ERR = str(_e)

# ---- Android storage + permissions (no-ops on desktop) ------------------
ON_ANDROID = False
try:
    from android.permissions import request_permissions, Permission  # noqa
    from android.storage import primary_external_storage_path        # noqa
    ON_ANDROID = True
except Exception:
    pass


def default_download_dir():
    if ON_ANDROID:
        try:
            return os.path.join(primary_external_storage_path(), "Download")
        except Exception:
            pass
    d = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(d, exist_ok=True)
    return d


# Single-file presets — no ffmpeg merge needed on device.
QUALITY = {
    "Best (MP4)":        "best[ext=mp4]/best",
    "1080p":             "best[height<=1080][ext=mp4]/best[height<=1080]/best",
    "720p":              "best[height<=720][ext=mp4]/best[height<=720]/best",
    "480p":              "best[height<=480][ext=mp4]/best[height<=480]/best",
    "360p":              "best[height<=360][ext=mp4]/best[height<=360]/best",
    "Audio (M4A)":       "bestaudio[ext=m4a]/bestaudio/best",
}

BG = "#15151c"
CARD = "#21212c"
ACCENT = "#7c5cff"
ACCENT_D = "#6a4be0"
DANGER = "#e0524d"


class Root(BoxLayout):
    def __init__(self, app, **kw):
        super().__init__(orientation="vertical", padding=dp(14), spacing=dp(10), **kw)
        self.app = app
        Window.clearcolor = H(BG)

        # Header
        self.add_widget(Label(text="[b]⚡  Swift Grab[/b]",
                              markup=True, font_size="22sp", size_hint_y=None,
                              height=dp(44), color=H("#4aa3ff")))

        # URL
        self.url = TextInput(hint_text="Paste video / page / stream link…",
                             multiline=False, size_hint_y=None, height=dp(48),
                             background_color=H(CARD), foreground_color=H("#ffffff"),
                             cursor_color=H(ACCENT), padding=[dp(12), dp(14)])
        self.add_widget(self.url)

        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.paste_btn = self._btn("Paste", self.paste, "#3a3a44")
        row.add_widget(self.paste_btn)
        self.quality = Spinner(text="Best (MP4)", values=list(QUALITY.keys()),
                               background_color=H(ACCENT))
        row.add_widget(self.quality)
        self.add_widget(row)

        # Buttons
        brow = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        self.dl_btn = self._btn("⬇  Download", self.start, ACCENT)
        self.cancel_btn = self._btn("✕  Cancel", self.cancel, DANGER)
        self.cancel_btn.disabled = True
        brow.add_widget(self.dl_btn)
        brow.add_widget(self.cancel_btn)
        self.add_widget(brow)

        # Progress + status
        self.pb = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(18))
        self.add_widget(self.pb)
        self.status = Label(text="Ready.", size_hint_y=None, height=dp(26),
                            color=H("#cdb4ff"), font_size="13sp")
        self.add_widget(self.status)

        # Log
        sv = ScrollView()
        self.log_lbl = Label(text="", markup=False, size_hint_y=None,
                             halign="left", valign="top", color=H("#aab"),
                             font_size="12sp")
        self.log_lbl.bind(width=lambda *_: setattr(self.log_lbl, "text_size",
                                                   (self.log_lbl.width, None)))
        self.log_lbl.bind(texture_size=lambda *_: setattr(self.log_lbl, "height",
                                                          self.log_lbl.texture_size[1]))
        sv.add_widget(self.log_lbl)
        self.add_widget(sv)

        self.cancel_flag = threading.Event()

    def _btn(self, text, cb, color):
        b = Button(text=text, on_release=lambda *_: cb(),
                   background_normal="", background_color=H(color),
                   color=H("#ffffff"), font_size="15sp", bold=True)
        return b

    def paste(self):
        try:
            self.url.text = (Clipboard.paste() or "").strip()
        except Exception:
            pass

    @mainthread
    def log(self, msg):
        self.log_lbl.text += msg + "\n"

    @mainthread
    def set_status(self, msg):
        self.status.text = msg

    @mainthread
    def set_progress(self, v):
        self.pb.value = v

    @mainthread
    def set_running(self, running):
        self.dl_btn.disabled = running
        self.cancel_btn.disabled = not running
        self.dl_btn.text = "Downloading…" if running else "⬇  Download"

    def cancel(self):
        self.cancel_flag.set()
        self.set_status("Cancelling…")

    def start(self):
        url = self.url.text.strip()
        if not url:
            self.set_status("Please paste a link first.")
            return
        if yt_dlp is None:
            self.set_status("Download engine failed to load.")
            self.log("ERROR: yt-dlp did not load: " + str(_YTDLP_ERR))
            return
        self.cancel_flag.clear()
        self.set_running(True)
        self.set_progress(0)
        self.log("\n" + "=" * 30)
        self.log("Downloading: " + url)
        threading.Thread(target=self._worker, args=(url, self.quality.text),
                         daemon=True).start()

    def _hook(self, d):
        if self.cancel_flag.is_set():
            raise Exception("Cancelled by user")
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                pct = d.get("downloaded_bytes", 0) / total * 100
                self.set_progress(pct)
                spd = d.get("speed") or 0
                self.set_status(f"Downloading… {pct:.0f}%  "
                                f"{spd/1024/1024:.1f} MB/s" if spd
                                else f"Downloading… {pct:.0f}%")
        elif d.get("status") == "finished":
            self.set_progress(100)
            self.set_status("Finishing…")

    def _worker(self, url, quality_label):
        dest = default_download_dir()
        try:
            opts = {
                "format": QUALITY.get(quality_label, "best"),
                "outtmpl": os.path.join(dest, "%(title).100B.%(ext)s"),
                "progress_hooks": [self._hook],
                "noplaylist": True,
                "retries": 8,
                "fragment_retries": 8,
                "nocheckcertificate": True,
                "http_headers": {"User-Agent": "Mozilla/5.0 (Linux; Android 12)"},
                "logger": _Logger(self.log),
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.set_status("✓ Saved to: " + dest)
            self.log("✓ Done. Saved in " + dest)
        except Exception as e:
            if self.cancel_flag.is_set():
                self.set_status("Cancelled.")
                self.set_progress(0)
            else:
                self.set_status("✗ Failed — see log.")
                self.log("ERROR: " + str(e))
        finally:
            self.set_running(False)


class _Logger:
    def __init__(self, log):
        self._log = log

    def debug(self, m):
        if m and not m.startswith("[debug]"):
            self._log(m)

    def info(self, m):
        if m:
            self._log(m)

    def warning(self, m):
        self._log("WARNING: " + m)

    def error(self, m):
        self._log("ERROR: " + m)


# Clipboard import placed late so desktop testing still works.
try:
    from kivy.core.clipboard import Clipboard
except Exception:
    class Clipboard:  # noqa
        @staticmethod
        def paste():
            return ""


class VideoDownloaderApp(App):
    def build(self):
        self.title = "Swift Grab"
        if ON_ANDROID:
            try:
                request_permissions([Permission.INTERNET,
                                     Permission.WRITE_EXTERNAL_STORAGE,
                                     Permission.READ_EXTERNAL_STORAGE])
            except Exception:
                pass
        return Root(self)


def _write_crash(exc_text):
    """If the app crashes on startup, save the reason so it can be diagnosed."""
    for d in ("/sdcard/Download", os.path.expanduser("~")):
        try:
            with open(os.path.join(d, "swiftgrab_crash.txt"), "w",
                      encoding="utf-8") as f:
                f.write(exc_text)
            break
        except Exception:
            continue


if __name__ == "__main__":
    import traceback
    try:
        VideoDownloaderApp().run()
    except Exception:
        _write_crash(traceback.format_exc())
        raise
