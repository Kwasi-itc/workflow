#!/bin/bash
# PostgreSQL Setup Script for Workflows Module

echo "Setting up PostgreSQL for Workflows Module..."

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "Docker detected. Starting PostgreSQL container..."
    
    # Check if container already exists
    if docker ps -a | grep -q workflows-postgres; then
        echo "Container already exists. Starting it..."
        docker start workflows-postgres
    else
        echo "Creating new PostgreSQL container..."
        docker run --name workflows-postgres \
            -e POSTGRES_PASSWORD=postgres \
            -e POSTGRES_DB=workflows_db \
            -e POSTGRES_USER=postgres \
            -p 5432:5432 \
            -d postgres:15
    fi
    
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    echo "PostgreSQL container is running!"
    echo ""
    echo "Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: workflows_db"
    echo "  Username: postgres"
    echo "  Password: postgres"
    echo ""
    echo "Next steps:"
    echo "1. Create a .env file with:"
    echo "   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflows_db"
    echo "2. Run: python migrate_database.py"
    echo "3. Start the server: uvicorn app.main:app --reload"
else
    echo "Docker not found. Please install Docker or set up PostgreSQL manually."
    echo "See POSTGRESQL_SETUP.md for manual setup instructions."
fi

