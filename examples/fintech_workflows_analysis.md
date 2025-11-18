# Fintech Workflows with Varying Dependency Types

## Issues Found in Current `loan_after_kyc.json`

1. **Missing `steps` field** - Required by schema validation
2. **`workflow_dependencies` format mismatch** - Schema expects `List[str]` but file has `List[Dict]`
3. **`state_schema` structure** - Should be proper JSON Schema with `type: "object"` and nested properties
4. **Missing dependency metadata** - No way to specify API endpoints, conditions, or timeout for dependencies

## Suggested Schema Enhancements

### Current Limitation
```json
"workflow_dependencies": ["kyc_verification"]  // Just strings
```

### Enhanced Format (Recommended)
```json
"workflow_dependencies": [
  {
    "workflow_name": "kyc_verification",
    "workflow_id": "optional-uuid",
    "api_endpoint": "https://api.bank.com/kyc/check",
    "condition": "status == 'approved'",
    "timeout_seconds": 3600,
    "required": true
  }
]
```

## Fintech Workflow Scenarios

### 1. Simple Workflow Dependency
**Scenario**: Loan application requires KYC completion
- **Type**: Workflow dependency
- **Dependency**: `kyc_verification` workflow must be completed
- **Condition**: Status must be `approved`

### 2. Multiple Workflow Dependencies
**Scenario**: Mortgage application requires both KYC and credit check
- **Type**: Multiple workflow dependencies
- **Dependencies**: 
  - `kyc_verification` (status: approved)
  - `credit_check` (status: completed, score >= 650)

### 3. Conditional Workflow Dependency
**Scenario**: Premium credit card requires account opening OR high credit score
- **Type**: Conditional workflow dependency (OR logic)
- **Dependencies**: 
  - Either `account_opening` completed OR
  - External credit score >= 750

### 4. Step Dependency on External Service
**Scenario**: Wire transfer requires AML screening service
- **Type**: Step dependency on external service
- **Dependency**: External AML service must be available and return "clear"

### 5. Sequential Step Dependencies
**Scenario**: Account opening - KYC must complete before account features selection
- **Type**: Step dependencies within workflow
- **Dependency**: Step 5 depends on Step 4 (KYC) being approved

### 6. Time-Based Dependency
**Scenario**: Investment account requires account to be open for 30 days
- **Type**: Time-based workflow dependency
- **Dependency**: `account_opening` completed AND `completed_at` > 30 days ago

### 7. Data-Based Dependency
**Scenario**: Loan approval step depends on credit score from previous step
- **Type**: Data condition dependency
- **Dependency**: `financial_information.credit_score >= 650`

### 8. Parallel Dependencies (AND)
**Scenario**: Business account requires both business registration AND tax ID verification
- **Type**: Multiple parallel dependencies (all must be satisfied)
- **Dependencies**: 
  - `business_registration` workflow
  - `tax_id_verification` workflow

### 9. External API Dependency
**Scenario**: Payment processing requires payment gateway to be available
- **Type**: External service dependency
- **Dependency**: External API health check returns "healthy"

### 10. Conditional Step Based on Previous Data
**Scenario**: Collateral step only required if loan amount > $100,000
- **Type**: Conditional step dependency
- **Dependency**: `loan_details.amount > 100000`

### 11. Workflow Chain Dependency
**Scenario**: Investment account → requires account opening → requires KYC
- **Type**: Chained workflow dependencies
- **Dependencies**: 
  - `investment_account` depends on `account_opening`
  - `account_opening` depends on `kyc_verification`

### 12. Retry/Timeout Dependency
**Scenario**: Credit check with retry logic if service unavailable
- **Type**: External dependency with retry
- **Dependency**: External credit check service with max 3 retries, 5min timeout

### 13. User Action Dependency
**Scenario**: Loan disbursement requires user to sign documents
- **Type**: User action dependency
- **Dependency**: User must complete `document_signing` workflow

### 14. Approval Workflow Dependency
**Scenario**: Large loan requires manager approval workflow
- **Type**: Approval workflow dependency
- **Dependency**: `manager_approval` workflow completed with `approved: true`

### 15. Compliance Check Dependency
**Scenario**: International wire requires sanctions screening
- **Type**: External compliance dependency
- **Dependency**: External sanctions API returns "clear"

## Recommended Schema Changes

### Enhanced Workflow Dependencies
```json
{
  "workflow_dependencies": [
    {
      "type": "workflow",
      "workflow_name": "kyc_verification",
      "workflow_id": "optional-uuid",
      "condition": {
        "status": "completed",
        "state_data.verification_status": "approved"
      },
      "api_endpoint": "https://api.bank.com/kyc/check",
      "timeout_seconds": 3600,
      "required": true
    }
  ]
}
```

### Enhanced Step Dependencies
```json
{
  "depends_on": [
    {
      "type": "step",
      "step_id": "step_4",
      "condition": "state_data.kyc_documents.verification_status == 'approved'"
    },
    {
      "type": "workflow",
      "workflow_name": "credit_check",
      "condition": {
        "status": "completed",
        "state_data.credit_score": {">=": 650}
      }
    },
    {
      "type": "external",
      "service": "aml_screening",
      "api_endpoint": "https://api.bank.com/aml/check",
      "condition": "response.status == 'clear'",
      "timeout_seconds": 300,
      "retry": {
        "max_attempts": 3,
        "delay_seconds": 60
      }
    },
    {
      "type": "data",
      "field": "loan_details.amount",
      "condition": {">": 100000}
    },
    {
      "type": "time",
      "workflow_name": "account_opening",
      "condition": "completed_at < (now - 30 days)"
    }
  ]
}
```

## Implementation Recommendations

1. **Update Schema** to support rich dependency objects
2. **Enhance Dependency Service** to handle:
   - Condition evaluation
   - API endpoint checking
   - Timeout handling
   - Retry logic
   - Data-based conditions
   - Time-based conditions
3. **Add Dependency Types**:
   - `workflow` - Other workflow completion
   - `step` - Step within same workflow
   - `external` - External service/API
   - `data` - Data condition in state
   - `time` - Time-based condition
   - `user_action` - User interaction required
   - `approval` - Approval workflow


