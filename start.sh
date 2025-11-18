#!/bin/bash
# Start script for Render deployment
# Runs database migrations and starts the FastAPI server

set -e  # Exit on error

echo "============================================================"
echo "Starting Workflows Module API"
echo "============================================================"

# Run database migrations
echo ""
echo "Running database migrations..."
python migrate_database.py

if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully!"
else
    echo "✗ Migration failed"
    exit 1
fi

# Get port from environment variable (Render sets this)
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
WORKERS=${WORKERS:-4}

echo ""
echo "============================================================"
echo "Starting FastAPI server..."
echo "Server will start on $HOST:$PORT"
echo "API docs available at: http://$HOST:$PORT/docs"
echo "============================================================"
echo ""

# Start uvicorn
exec uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS

