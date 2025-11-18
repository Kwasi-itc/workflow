# Workflows Module - FastAPI Project

A modern FastAPI application for managing workflows with registry and permissions. 
This system allows you to **add new workflows without writing code** - just define workflow templates via the API.

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows (PowerShell):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```bash
     venv\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   
   **Option A: Using Docker (Recommended)**
   ```bash
   docker run --name workflows-postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=workflows_db \
     -p 5432:5432 \
     -d postgres:15
   ```
   
   **Option B: Local PostgreSQL Installation**
   - Install PostgreSQL from https://www.postgresql.org/download/
   - Create a database:
     ```sql
     CREATE DATABASE workflows_db;
     ```
   
   **Configure Database Connection**
   - Create a `.env` file in the project root:
     ```bash
     DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflows_db
     ```
   - Replace `postgres:postgres` with your actual username and password
   - Replace `localhost:5432` if your PostgreSQL is on a different host/port
   
   **Initialize Database Schema**
   - Run the migration script to create tables:
     ```bash
     python migrate_database.py
     ```
   
   **Note:** For development/testing, you can use SQLite by setting:
   ```bash
   DATABASE_URL=sqlite:///./workflows.db
   ```

## Running the Application

Start the development server with auto-reload on port 8001:

```bash
uvicorn main:app --reload --port 8001
```

The API will be available at `http://127.0.0.1:8001`

**To use a different port**, simply change the `--port` value:
```bash
uvicorn main:app --reload --port 3000
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## API Endpoints

### Core Endpoints
- `GET /` - Welcome message with API information
- `GET /health` - Health check endpoint with timestamp

### Workflow Templates
- `GET /api/workflow-templates` - List all workflow templates (with filtering)
- `GET /api/workflow-templates/{template_id}` - Get a template by ID
- `GET /api/workflow-templates/name/{name}` - Get a template by name
- `POST /api/workflow-templates` - Create a new workflow template (add workflows without code!)
- `PUT /api/workflow-templates/{template_id}` - Update a template
- `DELETE /api/workflow-templates/{template_id}` - Delete a template
- `GET /api/workflow-templates/user-type/{user_type_id}` - Get templates for a user type

### Workflow Instances
- `GET /api/workflows` - List workflow instances (with filtering)
- `GET /api/workflows/{workflow_id}` - Get a workflow instance by ID
- `POST /api/workflows` - Create a new workflow instance
- `PUT /api/workflows/{workflow_id}` - Update a workflow instance
- `DELETE /api/workflows/{workflow_id}` - Delete a workflow instance

### Permissions
- `POST /api/permissions` - Assign workflow template to user type
- `DELETE /api/permissions` - Remove workflow template from user type
- `GET /api/permissions/user-type/{user_type_id}` - Get permissions for a user type
- `GET /api/permissions/workflow-template/{workflow_template_id}` - Get user types with access to a template

## Features

### Workflow Registry System
- **Code-free workflow creation**: Add new workflows by defining templates via API
- **Template validation**: Automatic validation of workflow structure, steps, and state schemas
- **Workflow discovery**: Easy querying and filtering of available workflows

### Permission Management
- **User type associations**: Control which workflows are available to which user types
- **Granular access control**: Assign/revoke permissions via API
- **Permission queries**: Easily find which workflows a user type can access

### Database Models
- **WorkflowTemplate**: Reusable workflow definitions with steps and state schema
- **Workflow**: Workflow instances tied to conversations
- **UserTypeWorkflowTemplate**: Permission associations

### Technical Features
- **Pydantic Models**: Type-safe request/response validation
- **SQLAlchemy ORM**: Database abstraction with PostgreSQL support
- **Automatic API Documentation**: Swagger UI and ReDoc
- **Type Hints**: Full Python type annotations
- **Data Validation**: Automatic request validation with helpful error messages
- **JSONB Support**: Flexible JSON storage for workflow definitions and state

## Example: Creating a Workflow Template

See `examples/workflow_template_example.json` for a complete example of a workflow template.

Key components:
- **name**: Unique identifier for the workflow
- **steps**: Array of step definitions (each with id, name, fields)
- **state_schema**: JSON Schema defining the expected output structure
- **guidelines**: Instructions for LLM on how to guide users
- **end_action_type**: What happens when workflow completes (api_call, workflow, tool_call, none)

## Development

The server runs with `--reload` flag, which automatically reloads when you make changes to the code.

