from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.routes import workflow_templates, workflows, permissions
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workflows Module API",
    description="A FastAPI application for managing workflows with registry and permissions. "
                "Add new workflows without writing code - just define templates via API.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflow_templates.router)
app.include_router(workflows.router)
app.include_router(permissions.router)


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {
        "message": "Welcome to the Workflows Module API",
        "description": "A workflow management system with registry and permissions",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "workflow_templates": "/api/workflow-templates",
            "workflows": "/api/workflows",
            "permissions": "/api/permissions"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "workflows-module"
    }

