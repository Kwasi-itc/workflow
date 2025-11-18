# Workflows Module Architecture

## Overview

This workflows module is designed for a genetic system where workflows can be added **without writing code**. The system uses a template-based registry pattern that allows dynamic workflow creation via API.

## Design Principles

### 1. Code-Free Workflow Addition
- Workflows are defined as **templates** stored in the database
- Templates contain all necessary information: steps, state schema, guidelines, end actions
- No code changes required to add new workflows - just POST a template via API

### 2. Registry Pattern
- **WorkflowRegistry** service manages all workflow templates
- Provides validation, discovery, and management capabilities
- Centralized place for workflow operations

### 3. Permission System
- User types are associated with workflow templates via `UserTypeWorkflowTemplate`
- Permissions are managed at the template level
- Easy to query which workflows are available to which user types

## Architecture Layers

### 1. Models Layer (`app/models/`)
SQLAlchemy ORM models:
- **WorkflowTemplate**: Template definition (name, steps, state_schema, guidelines)
- **Workflow**: Workflow instance (tied to conversation, has state, tracks progress)
- **UserTypeWorkflowTemplate**: Permission association (many-to-many)

### 2. Schemas Layer (`app/schemas/`)
Pydantic models for API validation:
- Request schemas (Create, Update)
- Response schemas (with relationships)
- Field validation and constraints

### 3. Services Layer (`app/services/`)
Business logic:
- **WorkflowRegistry**: Template management, validation, discovery
- Handles all workflow template operations
- Validates template structure (steps, state_schema, end_actions)

### 4. Routes Layer (`app/routes/`)
FastAPI endpoints:
- **workflow_templates.py**: Template CRUD operations
- **workflows.py**: Workflow instance management
- **permissions.py**: Permission management

## Key Features

### Workflow Template Structure

```json
{
  "name": "unique_template_name",
  "description": "Human-readable description",
  "category": "medical|financial|etc",
  "guidelines": "Instructions for LLM on how to guide users",
  "state_schema": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  },
  "steps": [
    {
      "id": "step_1",
      "name": "Step Name",
      "description": "What this step does",
      "fields": ["field1", "field2"],
      "required": true
    }
  ],
  "end_action_type": "api_call|workflow|tool_call|none",
  "end_action_target": "URL or identifier"
}
```

### Validation Rules

1. **Steps Validation**:
   - Must have at least one step
   - Each step must have `id` and `name`
   - Step IDs must be unique

2. **State Schema Validation**:
   - Must be a valid JSON Schema object
   - Used to validate final workflow state

3. **End Action Validation**:
   - Must be one of: `api_call`, `workflow`, `tool_call`, `none`
   - If not `none`, `end_action_target` is required

### Workflow Instance Lifecycle

1. **Created**: Workflow instance created from template
2. **Active**: Workflow in progress, collecting data
3. **Completed**: All steps done, end action executed
4. **Cancelled**: User/System cancelled the workflow
5. **Failed**: Error occurred during execution

### Constraints

- **One active workflow per conversation**: Unique index ensures only one active workflow exists per conversation
- **Template uniqueness**: Template names must be unique
- **Permission uniqueness**: Each user_type + template combination is unique

## Database Schema

### WorkflowTemplate
- Stores reusable workflow definitions
- JSONB fields for flexible schema (steps, state_schema, metadata)
- Indexed on name, category, is_active

### Workflow
- Represents active/completed workflow executions
- Linked to conversation and template
- Tracks current step, state data, status
- Indexed on template_id, conversation_id, user_id, status

### UserTypeWorkflowTemplate
- Many-to-many association table
- Defines which workflows are available to which user types
- Unique constraint on (user_type_id, workflow_template_id)

## API Design

### RESTful Conventions
- `/api/workflow-templates` - Template resources
- `/api/workflows` - Workflow instance resources
- `/api/permissions` - Permission management

### Query Parameters
- Pagination: `skip`, `limit`
- Filtering: `category`, `is_active`, `status`, `conversation_id`, `user_id`

### Response Codes
- `201` - Created
- `200` - Success
- `204` - No Content (delete)
- `400` - Bad Request (validation errors)
- `404` - Not Found

## Extension Points

### Adding New Workflow Types
1. POST to `/api/workflow-templates` with template definition
2. System validates and stores template
3. Assign to user types via `/api/permissions`
4. Ready to use immediately!

### Custom End Actions
Currently supports:
- `api_call`: Call external API with workflow state
- `workflow`: Trigger another workflow
- `tool_call`: Execute a tool/function
- `none`: No action

To add new types, update the CheckConstraint in `WorkflowTemplate` model.

### Integration with LLM System
The `guidelines` field provides instructions for how the LLM should guide users through the workflow. The `state_schema` defines what data structure should be collected.

## Future Enhancements

1. **Step Validation**: Add per-step validation rules
2. **Conditional Steps**: Steps that depend on previous step data
3. **Workflow Versioning**: Version templates and track changes
4. **Workflow Analytics**: Track completion rates, time to complete
5. **Webhooks**: Notify external systems on workflow events
6. **Step Templates**: Reusable step definitions


