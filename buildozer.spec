[app]

# Ilova nomi
title = Salomatli Hayot

# Paket nomi
package.name = salomatlihayot

# Paket domeni
package.domain = uz.salomatli

# Manba kodi joylashuvi
source.dir = .

# Manba fayllar
source.include_exts = py,png,jpg,kv,atlas,json

# Versiya
version = 1.0.0

# Kirish nuqtasi
source.main = main.py

# Talablar (dependencies)
requirements = python3,kivy==2.2.1,plyer,android

# Ruxsatlar (permissions)
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,ACCESS_FINE_LOCATION,BODY_SENSORS

# Android API
android.api = 31
android.minapi = 21

# Android NDK
android.ndk = 25b

# Android SDK
android.sdk = 31

# Orientatsiya
orientation = portrait

# Fullscreen
fullscreen = 0

# Icon
#icon.filename = %(source.dir)s/data/icon.png

# Presplash
#presplash.filename = %(source.dir)s/data/presplash.png

# Android arch
android.archs = arm64-v8a, armeabi-v7a

# Logotiр
android.logcat_filters = *:S python:D

# Android gradle dependencies
android.gradle_dependencies = 

# Android manifest
#android.manifest.intent_filters = 

# p4a bootstrap
p4a.bootstrap = sdl2

[buildozer]

# Log level
log_level = 2

# Warning on error
warn_on_root = 1