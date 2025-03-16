import os

# تكوين منفذ التطبيق - أخذ قيمة PORT من متغيرات البيئة أو استخدام 10000 كقيمة افتراضية
port = int(os.environ.get("PORT", 10000))

# إعدادات Gunicorn
bind = f"0.0.0.0:{port}"
workers = 1
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
