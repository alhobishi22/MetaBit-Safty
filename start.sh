#!/bin/bash
# تشغيل كلا العمليتين: تطبيق الويب وبوت تلجرام
echo "Starting services..."
echo "PORT=$PORT"
echo "PYTHONPATH=$PYTHONPATH"

# تأكد من تثبيت numpy أولاً بالإصدار المحدد
pip uninstall -y numpy pandas
pip install numpy==1.24.3
pip install pandas==2.0.3

# تأكد من تثبيت بقية المتطلبات
pip install -r requirements.txt

# عرض المكتبات المثبتة للتشخيص
pip list | grep -E 'numpy|pandas'

# تشغيل بوت تلجرام في الخلفية
echo "Starting Telegram bot in background..."
python run_telegram_bot.py &

# تشغيل تطبيق الويب
echo "Starting web application..."
gunicorn --bind 0.0.0.0:$PORT --workers=2 --threads=2 --worker-class=gevent wsgi:app
