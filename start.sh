#!/bin/bash

# تشغيل تطبيق الويب في الخلفية
gunicorn app:app --daemon --bind 0.0.0.0:$PORT --workers=1

# تشغيل بوت تيليجرام في المقدمة
python run_telegram_bot.py
