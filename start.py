#!/usr/bin/env python3
"""
Start script for Render deployment.
Runs database migrations and starts the FastAPI server.
"""
import sys
import subprocess
import os

def run_migrations():
    """Run database migrations."""
    print("=" * 60)
    print("Running database migrations...")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "migrate_database.py"],
            check=True,
            capture_output=False
        )
        print("\n✓ Migrations completed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Migration failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error running migrations: {e}")
        sys.exit(1)

def start_server():
    """Start the FastAPI server with uvicorn."""
    print("=" * 60)
    print("Starting FastAPI server...")
    print("=" * 60)
    
    # Get port from environment variable (Render sets this)
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    workers = os.getenv("WORKERS", "4")
    
    print(f"Server will start on {host}:{port}")
    print(f"Workers: {workers}")
    print(f"API docs available at: http://{host}:{port}/docs\n")
    
    # Build uvicorn command
    uvicorn_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    # Add workers if specified (only for production)
    if workers and workers != "1":
        uvicorn_cmd.extend(["--workers", str(workers)])
    
    # Start uvicorn
    try:
        subprocess.run(uvicorn_cmd, check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run migrations first
    run_migrations()
    
    # Then start the server
    start_server()

