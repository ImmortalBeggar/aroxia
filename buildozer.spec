[app]
title = Aroxia
package.name = aroxia
package.domain = org.aroxia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,md,txt
version = 0.1
requirements = python3,kivy,python-telegram-bot,google-generativeai,llama-cpp-python,pillow,pydub,google-auth-oauthlib,google-auth-httplib2,google-api-python-client
orientation = portrait
permissions = INTERNET,RECORD_AUDIO,FOREGROUND_SERVICE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.permissions = INTERNET,RECORD_AUDIO,FOREGROUND_SERVICE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = arm64-v8a
android.entrypoint = gui/main_app.py
services = aroxia_service:main.py
