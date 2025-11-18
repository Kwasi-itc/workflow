# Workflows Module API Endpoints

## Workflow Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/workflow-templates` | Create a new workflow template |
| `GET` | `/api/workflow-templates` | List all templates (filter: `category`, `is_active`, `skip`, `limit`) |
| `GET` | `/api/workflow-templates/{template_id}` | Get template by ID |
| `GET` | `/api/workflow-templates/name/{name}` | Get template by name |
| `PUT` | `/api/workflow-templates/{template_id}` | Update a template |
| `DELETE` | `/api/workflow-templates/{template_id}` | Delete a template |
| `GET` | `/api/workflow-templates/user-type/{user_type_id}` | Get templates for a user type |

## Workflow Instances

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/workflows` | Create a new workflow instance |
| `GET` | `/api/workflows` | List all workflows (filter: `conversation_id`, `user_id`, `status`, `skip`, `limit`) |
| `GET` | `/api/workflows/{workflow_id}` | Get workflow by ID |
| `PUT` | `/api/workflows/{workflow_id}` | Update a workflow instance |
| `DELETE` | `/api/workflows/{workflow_id}` | Delete a workflow instance |
| `GET` | `/api/workflows/{workflow_id}/dependencies` | Check workflow dependencies status |

## Permissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/permissions` | Assign workflow template to user type |
| `DELETE` | `/api/permissions` | Remove workflow from user type (query: `user_type_id`, `workflow_template_id`) |
| `GET` | `/api/permissions/user-type/{user_type_id}` | Get permissions for a user type |
| `GET` | `/api/permissions/workflow-template/{workflow_template_id}` | Get user types for a workflow template |

## Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint (API info) |
| `GET` | `/health` | Health check |

