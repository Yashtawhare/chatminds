#!/bin/bash

# Initialize database tables
python -c "from app import create_tables; create_tables()"

# Check if we're in development mode
if [ "$FLASK_ENV" = "development" ] || [ "$FLASK_DEBUG" = "true" ]; then
    echo "Starting in development mode..."
    python app.py
else
    echo "Starting in production mode with Gunicorn..."
    gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
fi