# Android app — build your own APK

This folder is a complete Kivy + yt-dlp Android app (`main.py`) and its build
config (`buildozer.spec`). Android apps must be **compiled on Linux**, so pick
one of the two paths below.

---

## ✅ Path A — Cloud build (recommended, no Linux needed)

You get a real, installable `.apk` from a free GitHub build server.

1. Create a free account at github.com and make a **new repository**.
2. Upload this whole project to it (the `android/` folder **and** the
   `.github/` folder are both required). Easiest:
   - On the repo page → **Add file → Upload files** → drag the project in → Commit.
3. Go to the repo's **Actions** tab. The **"Build Android APK"** workflow runs
   automatically (or click it → **Run workflow**).
4. Wait ~15–25 min for the first build (it downloads the Android toolchain).
5. When it finishes (green check), open the run → **Artifacts** →
   download **`UniversalVideoDownloader-apk`**. Inside is your `.apk`.

Install it on your phone:
- Copy the `.apk` to your phone, tap it.
- Allow **"Install unknown apps"** when Android asks (Settings prompt).
- Open the app, paste a link, Download. Files save to your **Download** folder.

> First launch asks for storage permission — allow it.

---

## Path B — Build locally on Linux / WSL

On Ubuntu (or Windows + WSL2 Ubuntu):

```bash
sudo apt update
sudo apt install -y python3-pip openjdk-17-jdk git zip unzip \
    autoconf libtool pkg-config zlib1g-dev libncurses-dev \
    libffi-dev libssl-dev
pip install --user buildozer cython
cd android
buildozer android debug
# APK appears in android/bin/*.apk
```

(First run downloads the Android SDK/NDK — a few GB, ~30 min.)

---

## What works / what doesn't

- **Works:** any site that serves a normal single-file MP4 (huge number of
  them), plus audio extraction to M4A. Paste link → pick quality → download.
- **Limited:** YouTube max-resolution and HLS/DASH streams that need merging
  require **ffmpeg on the device**, which isn't bundled by default (adding it is
  an advanced step — an ffmpeg recipe in `buildozer.spec`). The app picks
  single-file formats to avoid this.
- **Impossible:** DRM (Netflix/Prime/Disney+) — encrypted, same as every tool.

## Want a ready-made app instead?

If you just want it working on your phone today without building:
- **Seal** (F-Droid / github.com/JunkFood02/Seal) — open-source yt-dlp app.
- **1DM** — has a built-in stream-sniffing browser for movie sites.
