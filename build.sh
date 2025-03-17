#!/bin/bash
# Exit on error
set -o errexit

# Print Python version for debugging
python --version
echo "Installing dependencies..."

# تثبيت numpy أولاً بالإصدار المحدد
pip install numpy==1.24.3

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies needed for production
pip install gunicorn gevent psycopg2-binary

# List installed packages for debugging
pip list | grep -E 'numpy|pandas|psycopg2|flask-migrate'

# تهيئة ترحيلات قاعدة البيانات إذا لم تكن موجودة
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

# إنشاء جداول قاعدة البيانات مباشرة
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run database migrations
flask db migrate -m "تحديث هيكل قاعدة البيانات لدعم PostgreSQL"
flask db upgrade

# إعداد قاعدة البيانات PostgreSQL
python init_postgres.py

# Create admin user
python create_admin.py
