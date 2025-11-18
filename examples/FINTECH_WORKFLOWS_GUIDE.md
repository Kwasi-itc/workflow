# Fintech Workflows - Comprehensive Dependency Guide

## Current Schema Limitations & Recommendations

### Issues Found in `loan_after_kyc.json`

1. ✅ **FIXED**: Missing `steps` field - Now included
2. ✅ **FIXED**: `workflow_dependencies` format - Changed to `List[str]` to match current schema
3. ✅ **FIXED**: `state_schema` structure - Now proper JSON Schema with nested objects
4. ⚠️ **LIMITATION**: Current schema only supports simple string workflow dependencies

### Current Schema Support

**Currently Supported:**
- ✅ Simple workflow dependencies: `["workflow_name"]`
- ✅ Step dependencies: `["step_id"]` or `[{"type": "step", "step_id": "..."}]`
- ✅ External dependencies: `[{"type": "external", "condition": "..."}]`
- ✅ Workflow dependencies in steps: `[{"type": "workflow", "workflow_name": "..."}]`

**Not Yet Supported (Recommended Enhancements):**
- ❌ Rich workflow dependency objects with conditions
- ❌ API endpoint specification for dependencies
- ❌ Timeout/retry logic for external dependencies
- ❌ Data-based conditions in dependencies
- ❌ Time-based conditions
- ❌ OR/AND logic for multiple dependencies

---

## 15 Fintech Workflow Scenarios with Dependency Types

### 1. Simple Workflow Dependency ✅ (Currently Supported)
**Workflow**: `loan_application_after_kyc`
- **Dependency Type**: Workflow dependency
- **Requires**: `kyc_verification` workflow completed
- **Current Support**: ✅ Yes (using `workflow_dependencies: ["kyc_verification"]`)

### 2. Multiple Workflow Dependencies ⚠️ (Partially Supported)
**Workflow**: `mortgage_application`
- **Dependency Type**: Multiple workflow dependencies (AND)
- **Requires**: 
  - `kyc_verification` completed
  - `credit_check` completed
- **Current Support**: ⚠️ Partial (can list multiple, but no conditions)
- **Recommended**: `workflow_dependencies: ["kyc_verification", "credit_check"]`

### 3. Conditional Workflow Dependency ❌ (Not Supported)
**Workflow**: `premium_credit_card`
- **Dependency Type**: Conditional (OR logic)
- **Requires**: Either `account_opening` OR `credit_score >= 750`
- **Current Support**: ❌ No
- **Recommended Enhancement**: 
```json
"workflow_dependencies": [
  {
    "type": "or",
    "options": [
      {"type": "workflow", "name": "account_opening"},
      {"type": "data", "field": "credit_score", "condition": ">= 750"}
    ]
  }
]
```

### 4. External Service Dependency ✅ (Currently Supported)
**Workflow**: `wire_transfer`
- **Dependency Type**: External service dependency
- **Requires**: AML screening service available
- **Current Support**: ✅ Yes (using step dependency with `{"type": "external"}`)
- **Example**:
```json
"depends_on": [
  {
    "type": "external",
    "condition": "aml_service_available",
    "description": "AML screening service must be available"
  }
]
```

### 5. Step Dependency on Previous Step ✅ (Currently Supported)
**Workflow**: `account_opening_with_kyc_step`
- **Dependency Type**: Step dependency
- **Requires**: KYC step must be approved before account features
- **Current Support**: ✅ Yes
- **Example**:
```json
"depends_on": [
  {
    "type": "step",
    "step_id": "step_4",
    "condition": "kyc_documents.verification_status == 'approved'"
  }
]
```

### 6. Time-Based Dependency ❌ (Not Supported)
**Workflow**: `investment_account`
- **Dependency Type**: Time-based workflow dependency
- **Requires**: Account opened 30+ days ago
- **Current Support**: ❌ No
- **Recommended Enhancement**:
```json
"workflow_dependencies": [
  {
    "type": "workflow",
    "name": "account_opening",
    "time_condition": "completed_at < (now - 30 days)"
  }
]
```

### 7. Data-Based Dependency ⚠️ (Partially Supported)
**Workflow**: `loan_approval`
- **Dependency Type**: Data condition dependency
- **Requires**: Credit score from previous step >= 650
- **Current Support**: ⚠️ Partial (can specify in step condition, but not validated)
- **Example**:
```json
"depends_on": [
  {
    "type": "step",
    "step_id": "step_3",
    "condition": "financial_information.credit_score >= 650"
  }
]
```

### 8. Parallel Dependencies (AND) ⚠️ (Partially Supported)
**Workflow**: `business_account`
- **Dependency Type**: Multiple parallel dependencies
- **Requires**: Both `business_registration` AND `tax_id_verification`
- **Current Support**: ⚠️ Partial (can list multiple, all must be satisfied)
- **Example**: `workflow_dependencies: ["business_registration", "tax_id_verification"]`

### 9. External API Health Check ❌ (Not Supported)
**Workflow**: `payment_processing`
- **Dependency Type**: External API dependency with health check
- **Requires**: Payment gateway API returns "healthy"
- **Current Support**: ❌ No
- **Recommended Enhancement**:
```json
"depends_on": [
  {
    "type": "external",
    "service": "payment_gateway",
    "api_endpoint": "https://api.payment.com/health",
    "condition": "response.status == 'healthy'",
    "timeout_seconds": 30
  }
]
```

### 10. Conditional Step Based on Data ⚠️ (Partially Supported)
**Workflow**: `collateral_loan`
- **Dependency Type**: Conditional step dependency
- **Requires**: Collateral step only if loan amount > $100k
- **Current Support**: ⚠️ Partial (can specify condition, but step still exists)
- **Example**:
```json
{
  "id": "step_collateral",
  "depends_on": [
    {
      "type": "data",
      "field": "loan_details.amount",
      "condition": "> 100000"
    }
  ]
}
```

### 11. Chained Workflow Dependencies ✅ (Currently Supported)
**Workflow**: `investment_account_chain`
- **Dependency Type**: Chained workflow dependencies
- **Requires**: `account_opening` (which itself requires `kyc_verification`)
- **Current Support**: ✅ Yes (dependency chain is automatically resolved)
- **Example**: `workflow_dependencies: ["account_opening"]` (account_opening has its own dependencies)

### 12. External Dependency with Retry ❌ (Not Supported)
**Workflow**: `credit_check_with_retry`
- **Dependency Type**: External dependency with retry logic
- **Requires**: Credit check service with retry on failure
- **Current Support**: ❌ No
- **Recommended Enhancement**:
```json
"depends_on": [
  {
    "type": "external",
    "service": "credit_check",
    "api_endpoint": "https://api.bank.com/credit/check",
    "retry": {
      "max_attempts": 3,
      "delay_seconds": 60
    },
    "timeout_seconds": 300
  }
]
```

### 13. User Action Dependency ⚠️ (Partially Supported)
**Workflow**: `loan_disbursement`
- **Dependency Type**: User action dependency
- **Requires**: User completes `document_signing` workflow
- **Current Support**: ⚠️ Partial (can use workflow dependency, but no user action flag)
- **Example**: `workflow_dependencies: ["document_signing"]`

### 14. Approval Workflow Dependency ⚠️ (Partially Supported)
**Workflow**: `large_loan_approval`
- **Dependency Type**: Approval workflow with condition
- **Requires**: `manager_approval` workflow with `approved: true`
- **Current Support**: ⚠️ Partial (can check workflow completion, but condition checking not implemented)
- **Recommended Enhancement**:
```json
"workflow_dependencies": [
  {
    "type": "workflow",
    "name": "manager_approval",
    "condition": {
      "status": "completed",
      "state_data.approved": true
    }
  }
]
```

### 15. Compliance Check Dependency ✅ (Currently Supported)
**Workflow**: `international_wire`
- **Dependency Type**: External compliance dependency
- **Requires**: Sanctions screening API returns "clear"
- **Current Support**: ✅ Yes (using external dependency type)
- **Example**:
```json
"depends_on": [
  {
    "type": "external",
    "condition": "sanctions_screening_passed",
    "description": "Sanctions screening must return 'clear'"
  }
]
```

---

## Summary: Current vs Recommended

### ✅ Currently Supported (7/15)
1. Simple workflow dependency
2. External service dependency
3. Step dependency on previous step
4. Chained workflow dependencies
5. Compliance check dependency
6. Multiple workflow dependencies (basic)
7. Data-based dependency (basic, in step conditions)

### ⚠️ Partially Supported (5/15)
1. Multiple workflow dependencies (no conditions)
2. Data-based dependency (not validated)
3. Parallel dependencies (no explicit AND logic)
4. Conditional step (step still exists)
5. User action dependency (no user action flag)

### ❌ Not Supported (3/15)
1. Conditional workflow dependency (OR logic)
2. Time-based dependency
3. External dependency with retry/timeout

---

## Recommended Schema Enhancements

### 1. Enhanced Workflow Dependencies
```json
"workflow_dependencies": [
  "simple_string_name",  // Current format (backward compatible)
  {
    "type": "workflow",
    "workflow_name": "kyc_verification",
    "workflow_id": "optional-uuid",
    "condition": {
      "status": "completed",
      "state_data.verification_status": "approved"
    },
    "api_endpoint": "https://api.bank.com/kyc/check",
    "timeout_seconds": 3600
  }
]
```

### 2. Enhanced Step Dependencies
```json
"depends_on": [
  "step_1",  // Simple string (current)
  {
    "type": "step",
    "step_id": "step_4",
    "condition": "state_data.kyc_documents.verification_status == 'approved'"
  },
  {
    "type": "workflow",
    "workflow_name": "credit_check",
    "condition": {"state_data.credit_score": {">=": 650}}
  },
  {
    "type": "external",
    "service": "aml_screening",
    "api_endpoint": "https://api.bank.com/aml/check",
    "condition": "response.status == 'clear'",
    "timeout_seconds": 300,
    "retry": {"max_attempts": 3, "delay_seconds": 60}
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
```

---

## Implementation Priority

### Phase 1: High Priority (Most Common)
1. ✅ Workflow dependencies with conditions
2. ✅ External dependencies with API endpoints
3. ✅ Data-based conditions in dependencies

### Phase 2: Medium Priority
4. Time-based dependencies
5. Retry logic for external dependencies
6. Timeout handling

### Phase 3: Nice to Have
7. OR logic for conditional dependencies
8. User action flags
9. Advanced condition evaluation

---

## Example Workflows to Create

Based on current schema capabilities, here are workflows you can create now:

1. ✅ `loan_application_after_kyc.json` - Simple workflow dependency
2. ✅ `mortgage_application.json` - Multiple workflow dependencies
3. ✅ `wire_transfer_with_aml.json` - External service dependency
4. ✅ `account_opening_with_dependencies.json` - Step dependencies
5. ✅ `business_account.json` - Parallel workflow dependencies

Would you like me to create these example workflow files?


