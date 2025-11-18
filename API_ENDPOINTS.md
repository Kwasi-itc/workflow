# API Endpoints Documentation

Complete list of all available endpoints in the Workflows Module API.

## Base URL
- Development: `http://127.0.0.1:8001`
- API Documentation: `http://127.0.0.1:8001/docs` (Swagger UI)
- Alternative Docs: `http://127.0.0.1:8001/redoc` (ReDoc)

---

## Core Endpoints

### `GET /`
**Description:** Welcome message with API information

**Response:**
```json
{
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
```

### `GET /health`
**Description:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Workflow Templates Endpoints

Base path: `/api/workflow-templates`

### `POST /api/workflow-templates`
**Description:** Create a new workflow template

**Request Body:** `WorkflowTemplateCreate`
```json
{
  "name": "loan_application",
  "description": "Personal loan application workflow",
  "category": "fintech",
  "guidelines": "Guide the applicant through the loan application process...",
  "state_schema": {
    "amount": {"type": "number", "required": true},
    "purpose": {"type": "string", "required": true}
  },
  "workflow_dependencies": [
    {
      "name": "kyc_verification",
      "api": {
        "endpoint": "https://api.bank.com/kyc/check",
        "method": "GET",
        "headers": ["Authorization"],
        "query_params": ["user_id"]
      },
      "on_failure": {
        "action_type": "workflow",
        "action_target": {
          "workflow_id": "uuid-here",
          "workflow_name": "kyc_verification"
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://api.bank.com/loans/apply",
    "method": "POST",
    "headers": ["Authorization", "Content-Type"],
    "body": ["user_id", "loan_amount"]
  },
  "is_active": true
}
```

**Response:** `WorkflowTemplateResponse` (201 Created)

---

### `GET /api/workflow-templates`
**Description:** List all workflow templates with optional filtering

**Query Parameters:**
- `category` (optional): Filter by category
- `is_active` (optional): Filter by active status (true/false)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Pagination limit (default: 100, max: 1000)

**Example:**
```
GET /api/workflow-templates?category=fintech&is_active=true&skip=0&limit=50
```

**Response:** `List[WorkflowTemplateResponse]` (200 OK)

---

### `GET /api/workflow-templates/{template_id}`
**Description:** Get a workflow template by ID

**Path Parameters:**
- `template_id` (UUID): Template ID

**Response:** `WorkflowTemplateResponse` (200 OK)

**Errors:**
- `404`: Workflow template not found

---

### `GET /api/workflow-templates/name/{name}`
**Description:** Get a workflow template by name

**Path Parameters:**
- `name` (string): Template name

**Response:** `WorkflowTemplateResponse` (200 OK)

**Errors:**
- `404`: Workflow template not found

---

### `PUT /api/workflow-templates/{template_id}`
**Description:** Update a workflow template

**Path Parameters:**
- `template_id` (UUID): Template ID

**Request Body:** `WorkflowTemplateUpdate` (all fields optional)

**Response:** `WorkflowTemplateResponse` (200 OK)

**Errors:**
- `404`: Workflow template not found
- `400`: Validation error or name conflict

---

### `DELETE /api/workflow-templates/{template_id}`
**Description:** Delete a workflow template

**Path Parameters:**
- `template_id` (UUID): Template ID

**Response:** `204 No Content`

**Errors:**
- `404`: Workflow template not found

---

### `GET /api/workflow-templates/user-type/{user_type_id}`
**Description:** Get all workflow templates available to a specific user type

**Path Parameters:**
- `user_type_id` (UUID): User type ID

**Response:** `List[WorkflowTemplateResponse]` (200 OK)

---

## Workflow Instances Endpoints

Base path: `/api/workflows`

### `POST /api/workflows`
**Description:** Create a new workflow instance

**Request Body:** `WorkflowCreate`
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "state_data": {
    "amount": 50000,
    "purpose": "Home improvement"
  },
  "workflow_metadata": {
    "source": "web_app"
  }
}
```

**Response:** `WorkflowResponse` (201 Created)

**Behavior:**
- Automatically checks workflow dependencies
- Sets workflow to 'waiting' status if dependencies not satisfied
- Prevents creating multiple active workflows for same conversation

**Errors:**
- `404`: Workflow template not found
- `400`: Template is inactive or active workflow already exists for conversation

---

### `GET /api/workflows`
**Description:** List workflow instances with optional filtering

**Query Parameters:**
- `conversation_id` (optional, UUID): Filter by conversation ID
- `user_id` (optional, string): Filter by user ID
- `status` (optional, string): Filter by status (active|completed|cancelled|failed|waiting)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Pagination limit (default: 100, max: 1000)

**Example:**
```
GET /api/workflows?conversation_id=660e8400-e29b-41d4-a716-446655440000&status=active
```

**Response:** `List[WorkflowResponse]` (200 OK)

---

### `GET /api/workflows/{workflow_id}`
**Description:** Get a workflow instance by ID

**Path Parameters:**
- `workflow_id` (UUID): Workflow instance ID

**Response:** `WorkflowResponse` (200 OK)

**Errors:**
- `404`: Workflow not found

---

### `PUT /api/workflows/{workflow_id}`
**Description:** Update a workflow instance

**Path Parameters:**
- `workflow_id` (UUID): Workflow instance ID

**Request Body:** `WorkflowUpdate` (all fields optional)
```json
{
  "status": "completed",
  "state_data": {
    "amount": 50000,
    "purpose": "Home improvement",
    "full_name": "John Doe"
  },
  "pending_dependencies": {},
  "waiting_for": null
}
```

**Response:** `WorkflowResponse` (200 OK)

**Behavior:**
- Automatically checks dependencies before allowing workflow to proceed
- Sets workflow to 'waiting' if dependencies not satisfied
- Automatically resumes workflow if it was waiting and dependencies are now satisfied
- Sets `completed_at` timestamp when status changes to 'completed'

**Errors:**
- `404`: Workflow not found
- `400`: Cannot proceed - workflow dependencies not satisfied

---

### `POST /api/workflows/{workflow_id}/resume`
**Description:** Resume a waiting workflow if dependencies are satisfied

**Path Parameters:**
- `workflow_id` (UUID): Workflow instance ID

**Response:** `WorkflowResponse` (200 OK)

**Behavior:**
- Checks all dependencies
- Resumes workflow to 'active' status if all dependencies satisfied
- Returns error if dependencies still not satisfied

**Errors:**
- `404`: Workflow not found
- `400`: Cannot resume - dependencies not satisfied

---

### `GET /api/workflows/{workflow_id}/dependencies`
**Description:** Check workflow dependencies status

**Path Parameters:**
- `workflow_id` (UUID): Workflow instance ID

**Response:**
```json
{
  "workflow_id": "uuid-here",
  "status": "waiting",
  "workflow_dependencies": {
    "satisfied": false,
    "pending": [
      {
        "type": "workflow",
        "workflow_name": "kyc_verification",
        "satisfied": false
      }
    ]
  },
  "waiting_for": {
    "type": "workflow",
    "dependencies": [...]
  },
  "pending_dependencies": {
    "workflows": [...]
  }
}
```

**Errors:**
- `404`: Workflow not found

---

### `DELETE /api/workflows/{workflow_id}`
**Description:** Delete a workflow instance

**Path Parameters:**
- `workflow_id` (UUID): Workflow instance ID

**Response:** `204 No Content`

**Errors:**
- `404`: Workflow not found

---

## Permissions Endpoints

Base path: `/api/permissions`

### `POST /api/permissions`
**Description:** Assign a workflow template to a user type (grant permission)

**Request Body:** `UserTypeWorkflowTemplateCreate`
```json
{
  "user_type_id": "770e8400-e29b-41d4-a716-446655440000",
  "workflow_template_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** `UserTypeWorkflowTemplateResponse` (201 Created)

**Errors:**
- `404`: Workflow template not found
- `400`: Permission already exists or validation error

---

### `DELETE /api/permissions`
**Description:** Remove a workflow template from a user type (revoke permission)

**Query Parameters:**
- `user_type_id` (UUID, required): User type ID
- `workflow_template_id` (UUID, required): Workflow template ID

**Example:**
```
DELETE /api/permissions?user_type_id=770e8400-e29b-41d4-a716-446655440000&workflow_template_id=550e8400-e29b-41d4-a716-446655440000
```

**Response:** `204 No Content`

**Errors:**
- `404`: Permission association not found

---

### `GET /api/permissions/user-type/{user_type_id}`
**Description:** Get all workflow permissions for a specific user type

**Path Parameters:**
- `user_type_id` (UUID): User type ID

**Response:** `List[UserTypeWorkflowTemplateResponse]` (200 OK)

---

### `GET /api/permissions/workflow-template/{workflow_template_id}`
**Description:** Get all user types that have access to a specific workflow template

**Path Parameters:**
- `workflow_template_id` (UUID): Workflow template ID

**Response:** `List[UserTypeWorkflowTemplateResponse]` (200 OK)

---

## HTTP Status Codes

- `200 OK`: Successful GET, PUT request
- `201 Created`: Successful POST request (resource created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error, business logic error
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation error (Pydantic)

---

## Common Query Parameters

### Pagination
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

### Filtering
- `category`: Filter by category (workflow templates)
- `is_active`: Filter by active status (workflow templates)
- `conversation_id`: Filter by conversation ID (workflows)
- `user_id`: Filter by user ID (workflows)
- `status`: Filter by status (workflows: active|completed|cancelled|failed|waiting)

---

## Example API Calls

### Create a Workflow Template
```bash
curl -X POST "http://127.0.0.1:8001/api/workflow-templates" \
  -H "Content-Type: application/json" \
  -d @examples/loan_after_kyc.json
```

### Create a Workflow Instance
```bash
curl -X POST "http://127.0.0.1:8001/api/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
    "user_id": "user123"
  }'
```

### Check Workflow Dependencies
```bash
curl "http://127.0.0.1:8001/api/workflows/{workflow_id}/dependencies"
```

### Resume a Waiting Workflow
```bash
curl -X POST "http://127.0.0.1:8001/api/workflows/{workflow_id}/resume"
```

### Assign Permission
```bash
curl -X POST "http://127.0.0.1:8001/api/permissions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_type_id": "770e8400-e29b-41d4-a716-446655440000",
    "workflow_template_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8001/docs
  - Try out endpoints directly in the browser
  - See request/response schemas
  - View example requests

- **ReDoc**: http://127.0.0.1:8001/redoc
  - Clean, readable documentation
  - Better for printing/sharing

