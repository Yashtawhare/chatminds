#!/bin/bash
set -e

# Function to check database connection
check_database() {
    echo "Checking database connection..."
    python -c "
import sqlite3
import os
db_path = os.environ.get('DATABASE_URL', 'sqlite:///app/askai.db').replace('sqlite:///', '')
try:
    conn = sqlite3.connect(db_path)
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"
}

# Wait for database to be ready
check_database

# Initialize database tables
echo "Initializing database tables..."
python -c "
try:
    from app import create_tables
    create_tables()
    print('Database tables initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    exit(1)
"

# Create required directories
mkdir -p /app/data/uploads /app/logs

# Check if we're in development mode
if [ "$FLASK_ENV" = "development" ] || [ "$FLASK_DEBUG" = "true" ]; then
    echo "Starting in development mode..."
    exec python app.py
else
    echo "Starting in production mode with Gunicorn..."
    # Calculate workers based on CPU cores (2 * cores + 1)
    WORKERS=${GUNICORN_WORKERS:-$((2 * $(nproc) + 1))}
    echo "Starting with $WORKERS workers"
    
    exec gunicorn \
        --bind 0.0.0.0:5000 \
        --workers $WORKERS \
        --worker-class sync \
        --worker-connections 1000 \
        --timeout 300 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --capture-output \
        app:app
fi