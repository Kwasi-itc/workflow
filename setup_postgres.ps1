# PostgreSQL Setup Script for Workflows Module (PowerShell)

Write-Host "Setting up PostgreSQL for Workflows Module..." -ForegroundColor Green

# Check if Docker is installed
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker detected. Starting PostgreSQL container..." -ForegroundColor Yellow
    
    # Check if container already exists
    $containerExists = docker ps -a | Select-String "workflows-postgres"
    
    if ($containerExists) {
        Write-Host "Container already exists. Starting it..." -ForegroundColor Yellow
        docker start workflows-postgres
    } else {
        Write-Host "Creating new PostgreSQL container..." -ForegroundColor Yellow
        docker run --name workflows-postgres `
            -e POSTGRES_PASSWORD=postgres `
            -e POSTGRES_DB=workflows_db `
            -e POSTGRES_USER=postgres `
            -p 5432:5432 `
            -d postgres:15
    }
    
    Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host ""
    Write-Host "PostgreSQL container is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Connection details:" -ForegroundColor Cyan
    Write-Host "  Host: localhost"
    Write-Host "  Port: 5432"
    Write-Host "  Database: workflows_db"
    Write-Host "  Username: postgres"
    Write-Host "  Password: postgres"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Create a .env file with:"
    Write-Host "   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflows_db"
    Write-Host "2. Run: python migrate_database.py"
    Write-Host "3. Start the server: uvicorn app.main:app --reload"
} else {
    Write-Host "Docker not found. Please install Docker or set up PostgreSQL manually." -ForegroundColor Red
    Write-Host "See POSTGRESQL_SETUP.md for manual setup instructions." -ForegroundColor Yellow
}

