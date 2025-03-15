#!/bin/bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies needed for production
pip install gunicorn gevent

# Initialize the database
python init_db.py

# Run database migrations
flask db upgrade
