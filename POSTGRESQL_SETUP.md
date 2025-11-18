# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL for the Workflows Module.

## Prerequisites

- Python 3.8+ installed
- PostgreSQL 12+ installed OR Docker installed

## Option 1: Using Docker (Recommended for Development)

### Step 1: Start PostgreSQL Container

```bash
docker run --name workflows-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=workflows_db \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  -d postgres:15
```

This will:
- Create a PostgreSQL 15 container named `workflows-postgres`
- Set the password to `postgres`
- Create a database named `workflows_db`
- Expose PostgreSQL on port 5432

### Step 2: Verify Container is Running

```bash
docker ps
```

You should see the `workflows-postgres` container running.

### Step 3: Stop/Start Container (when needed)

```bash
# Stop the container
docker stop workflows-postgres

# Start the container
docker start workflows-postgres

# Remove the container (if you want to start fresh)
docker rm -f workflows-postgres
```

## Option 2: Local PostgreSQL Installation

### Step 1: Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Run the installer and follow the setup wizard
- Remember the password you set for the `postgres` user

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE workflows_db;

# Exit psql
\q
```

## Configuration

### Step 1: Create `.env` File

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflows_db
```

**Replace the values:**
- `postgres:postgres` → `username:password` (your PostgreSQL credentials)
- `localhost:5432` → `host:port` (if different)
- `workflows_db` → your database name

### Step 2: Install Dependencies

Make sure `psycopg2-binary` is installed:

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database Schema

Run the migration script to create all tables:

```bash
python migrate_database.py
```

This will:
- Create all necessary tables
- Add any missing columns
- Set up indexes and constraints

## Verify Connection

### Test Database Connection

You can test the connection by starting the application:

```bash
uvicorn app.main:app --reload
```

If the connection is successful, you should see the server start without errors.

### Check Tables

Connect to PostgreSQL and verify tables were created:

```bash
psql -U postgres -d workflows_db

# List all tables
\dt

# Check workflow_templates table structure
\d workflow_templates

# Exit
\q
```

## Troubleshooting

### Connection Refused

**Error:** `could not connect to server: Connection refused`

**Solutions:**
- Verify PostgreSQL is running: `docker ps` (Docker) or `sudo systemctl status postgresql` (Linux)
- Check if port 5432 is correct
- Verify firewall settings

### Authentication Failed

**Error:** `password authentication failed`

**Solutions:**
- Verify username and password in `.env` file
- For Docker: Default is `postgres:postgres`
- For local install: Use the password you set during installation

### Database Does Not Exist

**Error:** `database "workflows_db" does not exist`

**Solutions:**
- Create the database: `CREATE DATABASE workflows_db;`
- Or update `.env` to use an existing database

### Permission Denied

**Error:** `permission denied for table`

**Solutions:**
- Grant permissions to your user:
  ```sql
  GRANT ALL PRIVILEGES ON DATABASE workflows_db TO postgres;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
  ```

## Migration from SQLite

If you were previously using SQLite and want to migrate data:

1. **Export data from SQLite:**
   ```bash
   sqlite3 workflows.db .dump > sqlite_dump.sql
   ```

2. **Import to PostgreSQL:**
   - You'll need to manually convert the SQLite dump to PostgreSQL format
   - Or use a migration tool like `pgloader`

3. **Update `.env` file** to point to PostgreSQL

4. **Run migration script:**
   ```bash
   python migrate_database.py
   ```

## Production Considerations

For production environments:

1. **Use strong passwords** - Don't use default `postgres:postgres`
2. **Enable SSL connections** - Add `?sslmode=require` to DATABASE_URL
3. **Use connection pooling** - Already configured in `database.py`
4. **Set up backups** - Regular PostgreSQL backups
5. **Monitor performance** - Use PostgreSQL monitoring tools
6. **Use environment variables** - Never commit `.env` files

Example production DATABASE_URL:
```
DATABASE_URL=postgresql://user:strong_password@db.example.com:5432/workflows_db?sslmode=require
```

## Switching Back to SQLite

If you want to use SQLite for development:

1. Update `.env`:
   ```bash
   DATABASE_URL=sqlite:///./workflows.db
   ```

2. The application will automatically use SQLite
3. No additional setup required

