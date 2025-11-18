# Workflow Dependencies API Design

## Overview
Workflow dependencies should be API-callable with full configuration for HTTP requests and failure handling. A dependency is considered satisfied if the API call succeeds (HTTP 200-299 status codes).

## Proposed Structure

### Basic Format
```json
{
  "workflow_dependencies": [
    {
      "name": "kyc_verification",
      "api": {
        "endpoint": "https://api.bank.com/kyc/check",
        "method": "GET",
        "headers": ["Authorization", "Content-Type"],
        "query_params": ["user_id", "conversation_id"],
        "body": null,  // Can also be array of keys (e.g., ["user_id", "loan_amount"])
        "timeout_seconds": 30
      },
       "on_failure": {
         "action_type": "workflow",
         "action_target": {
           "workflow_id": "uuid-of-workflow-instance",
           "workflow_name": "kyc_verification"
         }
       }
    }
  ]
}
```

## Field Definitions

### `api` object
- **endpoint** (required): Full URL to check dependency status
- **method** (required): HTTP method - **Only `GET` is allowed for workflow dependencies**
  - Dependencies are status checks, so they should be read-only operations
- **headers** (optional): Array of header names as strings (e.g., `["Authorization", "X-API-KEY"]`)
  - Values are resolved by the API executor from configuration/environment
- **query_params** (optional): Array of query parameter names as strings (e.g., `["user_id", "conversation_id"]`)
  - Values are resolved by the API executor from configuration/environment/template variables
- **body** (optional): Must be `null` or empty array for GET requests
  - GET requests do not have request bodies
- **timeout_seconds** (optional): Request timeout, default 30

### Template Variables
Variables resolved by the API executor for headers, query_params, and body:
- `{workflow.user_id}` - Current workflow's user_id
- `{workflow.conversation_id}` - Current workflow's conversation_id
- `{workflow.id}` - Current workflow's ID
- `{workflow.state_data.*}` - Access state data fields

Note: For `headers`, `query_params`, and `body`, values are resolved by the API executor based on the names/keys provided. The executor can look up values from configuration, environment variables, or template variables.

### `on_failure` object
What to do when dependency check fails:

**action_type** (required): One of:
- `workflow` - Wait for workflow completion or trigger another workflow
- `api_call` - Make an API call to handle the failure

**action_target** (required): Contains the configuration based on `action_type`:

**For action_type: "workflow":**
- **workflow_id** (required): ID of specific workflow instance to wait for
- **workflow_name** (optional): Name of workflow to trigger/wait for (for reference)

**For action_type: "api_call":**
- Same structure as dependency `api` object:
  - `endpoint` (required)
  - `method` (required)
  - `headers` (optional): Array of header names as strings (e.g., `["Authorization", "X-API-KEY"]`)
  - `query_params` (optional): Array of query parameter names as strings (e.g., `["user_id", "conversation_id"]`)
  - `body` (optional): Array of body keys as strings (e.g., `["user_id", "loan_amount"]`)
  - `timeout_seconds` (optional)

## Failure Scenarios

1. **API Call Fails** (network error, timeout, 4xx, 5xx responses)
   - Execute `on_failure` handler based on `action_type`:
     - If `action_type == "workflow"`: Set workflow to 'waiting' status, wait for dependent workflow
     - If `action_type == "api_call"`: Make the failure API call

2. **Dependency Not Found** (404 response)
   - Same handling as API call fails

3. **Invalid Response** (malformed JSON, unexpected structure)
   - Log error, treat as API call failure, execute `on_failure` handler

## Implementation Flow

1. **Workflow Creation/Update**
   - Parse `workflow_dependencies` array
   - For each dependency, make API call
   - If API call succeeds (HTTP 200-299): dependency satisfied, continue
   - If API call fails: execute `on_failure` handler

2. **Resume Workflow**
   - When workflow is in 'waiting' status
   - Re-check all dependencies
   - If all satisfied: resume to 'active'
   - If still pending: remain in 'waiting'

## Example Use Cases

### Example 1: KYC Verification (Workflow Failure Handler)
```json
{
  "name": "kyc_verification",
  "api": {
    "endpoint": "https://api.bank.com/kyc/status",
    "method": "GET",
    "query_params": ["user_id"]
  },
   "on_failure": {
     "action_type": "workflow",
     "action_target": {
       "workflow_id": "uuid-of-kyc-workflow-instance",
       "workflow_name": "kyc_verification"
     }
   }
}
```

### Example 2: Credit Check (API Call Failure Handler)
```json
{
  "name": "credit_check",
  "api": {
    "endpoint": "https://api.credit.com/check",
    "method": "POST",
    "headers": ["Authorization", "Content-Type"],
    "body": ["user_id", "loan_amount"]
  },
   "on_failure": {
     "action_type": "api_call",
     "action_target": {
       "endpoint": "https://api.bank.com/notifications/credit-failed",
       "method": "POST",
       "headers": ["Authorization", "Content-Type"],
       "query_params": ["user_id"],
       "body": ["user_id", "message"]
     }
   }
}
```

### Example 3: Optional Dependency (Skip if not available)
```json
{
  "name": "premium_features",
  "api": {
    "endpoint": "https://api.bank.com/premium/check",
    "method": "GET",
    "query_params": ["user_id"]
  },
   "on_failure": {
     "action_type": "workflow",
     "action_target": {
       "workflow_id": "uuid-of-premium-workflow-instance",
       "workflow_name": "premium_upgrade"
     }
   }
}
```

### Example 4: Workflow Dependency with Workflow Failure Handler
```json
{
  "name": "loan_after_kyc",
  "api": {
    "endpoint": "https://api.bank.com/workflows/kyc/status",
    "method": "GET",
    "query_params": ["user_id", "conversation_id"]
  },
   "on_failure": {
     "action_type": "workflow",
     "action_target": {
       "workflow_id": "uuid-of-kyc-workflow-instance",
       "workflow_name": "kyc_verification"
     }
   }
}
```


