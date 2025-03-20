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

<<<<<<< HEAD
# طباعة متغيرات البيئة (بدون كشف المعلومات الحساسة)
echo "DATABASE_URL exists: ${DATABASE_URL:+yes}"
if [ -n "$DATABASE_URL" ]; then
    DB_URL_MASKED=$(echo $DATABASE_URL | sed -E 's/(.+:\/\/.+:).+(@.+)/\1*****\2/')
    echo "DATABASE_URL: $DB_URL_MASKED"
fi

# إصلاح قاعدة البيانات بدلاً من إعادة تهيئتها في بيئة الإنتاج
echo "Fixing database..."
python fix_db.py

=======
>>>>>>> 0b2e9edf5d191e0912dd4d125ab7926541c65858
# تهيئة ترحيلات قاعدة البيانات إذا لم تكن موجودة
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

<<<<<<< HEAD
# Run database migrations
echo "Running database migrations..."
flask db migrate -m "تحديث هيكل قاعدة البيانات" || echo "Migration failed but continuing..."
flask db upgrade || echo "Upgrade failed but continuing..."

# إنشاء مستخدم مشرف
echo "Creating admin user..."
=======
# إنشاء جداول قاعدة البيانات مباشرة
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run database migrations
flask db migrate -m "تحديث هيكل قاعدة البيانات لدعم PostgreSQL"
flask db upgrade

# إعداد قاعدة البيانات PostgreSQL
python init_postgres.py

# Create admin user
>>>>>>> 0b2e9edf5d191e0912dd4d125ab7926541c65858
python create_admin.py
