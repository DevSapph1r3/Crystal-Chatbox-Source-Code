[app]
# Application title
title = Crystal Chatbox

# Package name
package.name = crystal_chatbox

# Package domain (needed for android/ios packaging)
package.domain = com.sapph1r3

# Source code directory
source.dir = .

# Source files to include (let empty for all files)
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js

# Source files to exclude
source.exclude_exts = spec

# Application versioning
version = 1.0.0

# Application requirements
# PyWebview supports Android as of v5.0+
requirements = python3,kivy,flask,python-osc,pytz,spotipy,requests,pywebview,cython,gunicorn

# Supported Android API
android.api = 31

# Minimum API required
android.minapi = 21

# Android NDK version to use
android.ndk = 25b

# Android SDK version to use
android.sdk = 31

# Permissions
android.permissions = INTERNET,WAKE_LOCK,VIBRATE

# Android orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Presplash background color
android.presplash_color = #0d0d0d

# Supported architectures
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1
