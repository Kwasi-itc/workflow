# Render Deployment Guide

This guide explains how to deploy the Workflows Module API to Render.

## Prerequisites

- A GitHub repository with your code
- A Render account (sign up at https://render.com)

## Quick Start

### Option 1: Using render.yaml (Recommended)

1. **Connect your GitHub repository** to Render
2. Render will automatically detect the `render.yaml` file
3. Configure the `DATABASE_URL` environment variable in Render dashboard
4. Deploy!

### Option 2: Manual Setup

1. **Create a new Web Service** in Render
2. Connect your GitHub repository
3. Configure the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py` (or `bash start.sh`)
   - **Environment**: Python 3
4. **Add Environment Variables**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `PORT`: 8000 (usually set automatically by Render)
   - `HOST`: 0.0.0.0 (usually set automatically by Render)
   - `WORKERS`: 4 (optional, defaults to 4)

## Database Setup

### Using Render PostgreSQL (Recommended)

1. In Render dashboard, create a **PostgreSQL** database
2. Copy the **Internal Database URL** or **External Database URL**
3. Set it as the `DATABASE_URL` environment variable in your web service

### Using External PostgreSQL

1. Set `DATABASE_URL` to your external PostgreSQL connection string:
   ```
   postgresql://user:password@host:port/database
   ```

## Start Scripts

The repository includes two start scripts:

### `start.py` (Python - Cross-platform)
- Runs migrations automatically
- Starts the server with uvicorn
- Handles errors gracefully

### `start.sh` (Bash - Linux/Unix)
- Same functionality as `start.py`
- More efficient for Linux-based deployments
- Make sure it's executable: `chmod +x start.sh`

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `PORT` | Server port | 8000 | No (auto-set by Render) |
| `HOST` | Server host | 0.0.0.0 | No |
| `WORKERS` | Number of uvicorn workers | 4 | No |

## Deployment Process

When you deploy, the start script will:

1. **Run Database Migrations**
   - Checks for missing columns
   - Creates tables if they don't exist
   - Updates schema to match current models

2. **Start FastAPI Server**
   - Runs on the configured host and port
   - Multiple workers for better performance
   - Accessible via Render's provided URL

## Health Check

After deployment, verify the service is running:

```bash
# Health check endpoint
curl https://your-app.onrender.com/health

# API documentation
https://your-app.onrender.com/docs
```

## Troubleshooting

### Migration Errors

If migrations fail:
1. Check your `DATABASE_URL` is correct
2. Ensure the database is accessible from Render
3. Check the logs in Render dashboard

### Server Won't Start

1. Check the build logs for dependency issues
2. Verify Python version (should be 3.8+)
3. Ensure all environment variables are set

### Database Connection Issues

1. For Render PostgreSQL: Use the **Internal Database URL** for better performance
2. For external databases: Ensure firewall allows Render's IP addresses
3. Verify credentials are correct

## Monitoring

- **Logs**: Available in Render dashboard under "Logs"
- **Metrics**: Monitor CPU, memory, and request metrics
- **Health Endpoint**: `/health` returns service status

## Notes

- The start script runs migrations on every deployment
- Migrations are idempotent (safe to run multiple times)
- The server uses multiple workers for better performance
- CORS is configured to allow all origins (adjust for production)

