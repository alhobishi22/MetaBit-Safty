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
pip list | grep -E 'numpy|pandas|psycopg2'

# إعداد قاعدة البيانات PostgreSQL
python init_postgres.py

# Run database migrations
flask db upgrade

# Create admin user
python create_admin.py
