#!/bin/bash

echo "Starting GreenCloud application..."

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting Gunicorn server..."
gunicorn app:app --config gunicorn_config.py
