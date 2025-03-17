#!/bin/bash
# تشغيل كلا العمليتين باستخدام honcho
echo "Starting services with honcho..."
echo "PORT=$PORT"
echo "PYTHONPATH=$PYTHONPATH"

# تأكد من تثبيت جميع المتطلبات مرة أخرى للتأكد
pip install -r requirements.txt

# تشغيل الخدمات
honcho start
