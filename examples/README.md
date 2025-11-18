# Workflow Examples

This directory contains example workflow templates demonstrating workflow dependencies and data collection patterns.

## Workflow Examples

### Basic Workflows
- `sequential_account_opening.json` - Bank account opening
- `sequential_loan_application.json` - Loan application
- `sequential_kyc_verification.json` - KYC verification process
- `non_sequential_loan_application.json` - Loan application form
- `non_sequential_account_opening.json` - Account opening form
- `non_sequential_credit_card_application.json` - Credit card application form

### Workflow Dependencies
- `loan_after_kyc.json` - Loan application that waits for KYC workflow
- `account_opening_with_step_dependencies.json` - Account opening with dependencies

## How to Use

1. **Create a workflow template:**
   ```bash
   curl -X POST "http://localhost:8001/api/workflow-templates" \
     -H "Content-Type: application/json" \
     -d @examples/sequential_account_opening.json
   ```

2. **Or use Swagger UI:**
   - Visit http://localhost:8001/docs
   - Use POST `/api/workflow-templates` endpoint
   - Copy and paste the JSON content

3. **Assign permissions:**
   ```bash
   curl -X POST "http://localhost:8001/api/permissions" \
     -H "Content-Type: application/json" \
     -d '{
       "user_type_id": "your-user-type-id",
       "workflow_template_id": "template-id-from-step-1"
     }'
   ```

4. **Create a workflow instance:**
   ```bash
   curl -X POST "http://localhost:8001/api/workflows" \
     -H "Content-Type: application/json" \
     -d '{
       "template_id": "template-id",
       "conversation_id": "conversation-id",
       "user_id": "user-id"
     }'
   ```

## Example Structure

Each workflow template includes:
- `name`: Unique identifier
- `description`: Human-readable description
- `category`: Workflow category
- `workflow_dependencies`: List of workflow names/IDs this workflow depends on (optional)
- `guidelines`: Instructions for LLM guidance
- `state_schema`: Simplified schema - flat structure with field definitions (no `type: "object"` or `properties` wrapper)
- `end_action_type`: What happens when workflow completes
- `end_action_target`: Target for the end action

## State Schema Format

The `state_schema` uses a simplified format - a flat dictionary of field definitions. Required fields are marked inline with `"required": true`:

```json
{
  "state_schema": {
    "amount": {"type": "number", "minimum": 1000, "maximum": 1000000, "required": true},
    "purpose": {"type": "string", "required": true},
    "full_name": {"type": "string", "required": true},
    "date_of_birth": {"type": "string", "format": "date", "required": true},
    "optional_field": {"type": "string"}
  }
}
```

**Key points:**
- No `type: "object"` or `properties` wrapper needed
- No top-level `required` array
- Required fields are marked with `"required": true` inline in each field definition
- Optional fields simply omit the `required` property


