[app]
title = Swift Grab
package.name = swiftgrab
package.domain = org.swiftgrab

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# Minimal, build-safe set for the first APK (all pure-Python).
# (Optional C-extension extras like pycryptodomex/brotli are added later.)
requirements = python3,kivy==2.3.1,yt-dlp,certifi,setuptools

orientation = portrait
fullscreen = 0

# Permissions: internet to download, storage to save into Download/.
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

# Accept the Android SDK license automatically (needed for unattended CI builds).
android.accept_sdk_license = True

# Needed so the app can write to the shared Download/ folder on older APIs.
android.legacy_storage = True

# App icon (your Swift Grab icon — saved as icon.png in this android/ folder).
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 0
