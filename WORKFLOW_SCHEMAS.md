# Complete Workflow Schemas

This document provides a complete overview of all workflow schemas in the system.

## Table of Contents
1. [Workflow Dependencies Schemas](#workflow-dependencies-schemas)
2. [Workflow Template Schemas](#workflow-template-schemas)
3. [Workflow Instance Schemas](#workflow-instance-schemas)
4. [User Type Association Schemas](#user-type-association-schemas)
5. [Complete JSON Examples](#complete-json-examples)

---

## Workflow Dependencies Schemas

### `ApiConfig`
API configuration used in dependencies and end actions.

```python
{
  "endpoint": str (required)              # Full URL
  "method": str (required)                # GET, POST, PUT, PATCH
  "headers": Optional[List[str]]          # Array of header names: ["Authorization", "Content-Type"]
  "query_params": Optional[List[str]]     # Array of param names: ["user_id", "conversation_id"]
  "body": Optional[List[str] | None]      # Array of body keys: ["user_id", "loan_amount"] or null
  "timeout_seconds": Optional[int]        # Default: 30, range: 1-300
}
```

### `OnFailureWorkflowTarget`
Target configuration for workflow failure handler.

```python
{
  "workflow_id": str (required)          # ID of workflow instance to wait for
  "workflow_name": Optional[str]           # Name of workflow (for reference)
}
```

### `OnFailureApiCallTarget`
Target configuration for API call failure handler (extends `ApiConfig`).

```python
# Same structure as ApiConfig
{
  "endpoint": str (required)
  "method": str (required)
  "headers": Optional[List[str]]
  "query_params": Optional[List[str]]
  "body": Optional[List[str] | None]
  "timeout_seconds": Optional[int]
}
```

### `OnFailure`
Failure handler configuration for workflow dependencies.

```python
{
  "action_type": Literal["workflow", "api_call"] (required)
  "action_target": Union[OnFailureWorkflowTarget, OnFailureApiCallTarget] (required)
}
```

**Validation:**
- If `action_type == "workflow"`: `action_target` must be `OnFailureWorkflowTarget`
- If `action_type == "api_call"`: `action_target` must be `OnFailureApiCallTarget`

### `WorkflowDependency`
Complete workflow dependency definition.

```python
{
  "name": str (required)                  # Name of the dependency
  "api": ApiConfig (required)             # API configuration to check dependency
  "on_failure": OnFailure (required)      # Failure handler configuration
}
```

### `EndActionWorkflowTarget`
Target configuration for workflow end action.

```python
{
  "workflow_id": Optional[str]            # ID of specific workflow instance to trigger
  "workflow_name": str (required)        # Name of workflow template to trigger
}
```

---

## Workflow Template Schemas

### `WorkflowTemplateBase`
Base schema for workflow templates.

```python
{
  "name": str (required)                  # Unique name, 1-255 chars
  "description": Optional[str]            # Description of the template
  "category": Optional[str]               # Category, max 100 chars
  "guidelines": Optional[str]             # Instructions for LLM guidance
  "state_schema": Dict[str, Any] (required)  # Simplified flat schema (no type/properties wrapper)
  "workflow_dependencies": Optional[List[WorkflowDependency]]  # Array of dependencies
  "end_action_type": Literal["api_call", "workflow", "none"] (required)
  "end_action_target": Optional[Union[ApiConfig, EndActionWorkflowTarget]]
  "workflow_metadata": Optional[Dict[str, Any]]  # Additional metadata
  "is_active": bool                      # Default: True
}
```

**Validation Rules:**
- `state_schema`: Must be a dictionary
- `workflow_dependencies`: Each item must be a valid `WorkflowDependency` object
- `end_action_type` and `end_action_target`:
  - If `end_action_type == "none"`: `end_action_target` must be `None`
  - If `end_action_type == "api_call"`: `end_action_target` must be `ApiConfig` (required)
  - If `end_action_type == "workflow"`: `end_action_target` must be `EndActionWorkflowTarget` (required)

### `WorkflowTemplateCreate`
Schema for creating a workflow template (extends `WorkflowTemplateBase`).

```python
# Same fields as WorkflowTemplateBase
```

### `WorkflowTemplateUpdate`
Schema for updating a workflow template (all fields optional).

```python
{
  "name": Optional[str]                   # 1-255 chars
  "description": Optional[str]
  "category": Optional[str]               # Max 100 chars
  "guidelines": Optional[str]
  "state_schema": Optional[Dict[str, Any]]
  "workflow_dependencies": Optional[List[WorkflowDependency]]
  "end_action_type": Optional[Literal["api_call", "workflow", "none"]]
  "end_action_target": Optional[Union[ApiConfig, EndActionWorkflowTarget]]
  "workflow_metadata": Optional[Dict[str, Any]]
  "is_active": Optional[bool]
}
```

### `WorkflowTemplateResponse`
Schema for workflow template response (extends `WorkflowTemplateBase`).

```python
# All fields from WorkflowTemplateBase, plus:
{
  "id": UUID (required)
  "created_at": datetime (required)
  "updated_at": datetime (required)
}
```

---

## Workflow Instance Schemas

### `WorkflowBase`
Base schema for workflow instances.

```python
{
  "template_id": UUID (required)         # ID of the workflow template
  "conversation_id": UUID (required)      # ID of the conversation
  "user_id": str (required)              # ID of the user
  "state_data": Dict[str, Any]          # Current state data (default: {})
  "workflow_metadata": Optional[Dict[str, Any]]  # Additional metadata
}
```

### `WorkflowCreate`
Schema for creating a workflow instance (extends `WorkflowBase`).

```python
# Same fields as WorkflowBase
```

### `WorkflowUpdate`
Schema for updating a workflow instance (all fields optional).

```python
{
  "status": Optional[str]                 # active|completed|cancelled|failed|waiting
  "state_data": Optional[Dict[str, Any]]
  "pending_dependencies": Optional[Dict[str, Any]]
  "waiting_for": Optional[Dict[str, Any]]
  "end_action_result": Optional[Dict[str, Any]]
  "workflow_metadata": Optional[Dict[str, Any]]
}
```

### `WorkflowResponse`
Schema for workflow instance response (extends `WorkflowBase`).

```python
# All fields from WorkflowBase, plus:
{
  "id": UUID (required)
  "status": str (required)               # active|completed|cancelled|failed|waiting
  "pending_dependencies": Optional[Dict[str, Any]]
  "waiting_for": Optional[Dict[str, Any]]
  "started_at": datetime (required)
  "completed_at": Optional[datetime]
  "last_interaction_at": datetime (required)
  "end_action_result": Optional[Dict[str, Any]]
  "created_at": datetime (required)
  "updated_at": datetime (required)
  "template": Optional[WorkflowTemplateResponse]  # Related template
}
```

---

## User Type Association Schemas

### `UserTypeWorkflowTemplateCreate`
Schema for creating a user type workflow template association.

```python
{
  "user_type_id": UUID (required)        # ID of the user type
  "workflow_template_id": UUID (required) # ID of the workflow template
}
```

### `UserTypeWorkflowTemplateResponse`
Schema for user type workflow template association response.

```python
{
  "id": UUID (required)
  "user_type_id": UUID (required)
  "workflow_template_id": UUID (required)
  "created_at": datetime (required)
}
```

---

## Complete JSON Examples

### Example 1: Workflow Template with API Call End Action

```json
{
  "name": "loan_application",
  "description": "Personal loan application workflow",
  "category": "fintech",
  "guidelines": "Guide the applicant through the loan application process. Be clear about what information is needed.",
  "state_schema": {
    "amount": {"type": "number", "minimum": 1000, "maximum": 1000000, "required": true},
    "purpose": {"type": "string", "required": true},
    "full_name": {"type": "string", "required": true},
    "date_of_birth": {"type": "string", "format": "date", "required": true},
    "national_id": {"type": "string", "required": true},
    "monthly_income": {"type": "number", "minimum": 0, "required": true}
  },
  "workflow_dependencies": [
    {
      "name": "kyc_verification",
      "api": {
        "endpoint": "https://api.bank.com/kyc/check",
        "method": "GET",
        "headers": ["Authorization", "Content-Type"],
        "query_params": ["user_id", "conversation_id"],
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "workflow",
        "action_target": {
          "workflow_id": "uuid-of-kyc-workflow-instance",
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
    "body": ["user_id", "loan_amount", "purpose"],
    "timeout_seconds": 60
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 15
  }
}
```

### Example 2: Workflow Template with Workflow End Action

```json
{
  "name": "kyc_verification",
  "description": "KYC verification process",
  "category": "compliance",
  "guidelines": "Guide the customer through KYC verification. This is a compliance requirement.",
  "state_schema": {
    "full_name": {"type": "string", "required": true},
    "date_of_birth": {"type": "string", "format": "date", "required": true},
    "national_id": {"type": "string", "required": true},
    "id_verified": {"type": "boolean", "required": true},
    "address_verified": {"type": "boolean", "required": true}
  },
  "workflow_dependencies": null,
  "end_action_type": "workflow",
  "end_action_target": {
    "workflow_name": "account_opening",
    "workflow_id": null
  },
  "is_active": true
}
```

### Example 3: Workflow Template with No End Action

```json
{
  "name": "data_collection",
  "description": "Simple data collection workflow",
  "category": "general",
  "guidelines": "Collect user information",
  "state_schema": {
    "email": {"type": "string", "format": "email", "required": true},
    "phone": {"type": "string", "required": true}
  },
  "workflow_dependencies": null,
  "end_action_type": "none",
  "end_action_target": null,
  "is_active": true
}
```

### Example 4: Workflow Dependency with API Call Failure Handler

```json
{
  "name": "credit_check",
  "api": {
    "endpoint": "https://api.credit.com/check",
    "method": "POST",
    "headers": ["Authorization", "Content-Type"],
    "body": ["user_id", "loan_amount"],
    "timeout_seconds": 30
  },
  "on_failure": {
    "action_type": "api_call",
    "action_target": {
      "endpoint": "https://api.bank.com/notifications/credit-failed",
      "method": "POST",
      "headers": ["Authorization", "Content-Type"],
      "body": ["user_id", "message"],
      "timeout_seconds": 30
    }
  }
}
```

### Example 5: Workflow Instance

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "state_data": {
    "amount": 50000,
    "purpose": "Home improvement",
    "full_name": "John Doe",
    "date_of_birth": "1990-01-01",
    "national_id": "ID123456",
    "monthly_income": 5000
  },
  "workflow_metadata": {
    "source": "web_app"
  }
}
```

---

## Schema Relationships

```
WorkflowTemplateBase
├── workflow_dependencies: List[WorkflowDependency]
│   ├── api: ApiConfig
│   └── on_failure: OnFailure
│       ├── action_type: "workflow" → action_target: OnFailureWorkflowTarget
│       └── action_type: "api_call" → action_target: OnFailureApiCallTarget (extends ApiConfig)
├── end_action_type: "api_call" → end_action_target: ApiConfig
├── end_action_type: "workflow" → end_action_target: EndActionWorkflowTarget
└── end_action_type: "none" → end_action_target: None

WorkflowBase
└── template_id → WorkflowTemplateResponse
```

---

## Key Features

1. **Simplified State Schema**: Flat structure without `type: "object"` or `properties` wrapper
2. **API Configuration**: Headers, query_params, and body are arrays of strings (names/keys)
3. **Structured Dependencies**: Full dependency objects with API config and failure handlers
4. **Type-Safe End Actions**: `end_action_target` structure matches `end_action_type`
5. **Failure Handling**: Configurable failure handlers with workflow or API call targets
6. **Validation**: Comprehensive validation at schema level and service level

