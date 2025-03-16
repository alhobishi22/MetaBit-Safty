#!/bin/bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies needed for production
pip install gunicorn gevent

# Make start script executable
chmod +x start.sh

# Initialize the database
python init_db.py

# Run database migrations
flask db upgrade

# Create admin user
python create_admin.py

# Initialize telegram bot database if needed
python -c "from telegram_bot import setup_db; setup_db()"
