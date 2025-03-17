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
pip install gunicorn gevent

# List installed packages for debugging
pip list | grep -E 'numpy|pandas'

# Initialize the database
python init_db.py

# Run database migrations
flask db upgrade

# Create admin user
python create_admin.py
