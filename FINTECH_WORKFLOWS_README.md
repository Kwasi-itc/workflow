# Fintech Workflow Templates

This document describes the workflow templates created based on the Fintech Agent API documentation (`DUMMY_API_DOCUMENTATION.md`).

## Overview

The `fintech_workflow_templates.json` file contains 13 workflow templates that integrate with the Fintech Agent API at `https://mydummyapi.onrender.com/`. These workflows cover the main use cases described in the API documentation.

## Workflow Templates

### 1. Payment Processing Workflow
**Name:** `payment_processing_workflow`  
**Category:** fintech  
**Description:** Complete payment processing with account validation, KYC check, limit verification, and payment initiation.

**Dependencies:**
- Account status check
- KYC status check  
- Limit status check

**End Action:** Initiates payment via `POST /payments/initiate`

**State Schema Fields:**
- `accountId`, `customerId`, `beneficiary`, `beneficiaryAccount`
- `amount`, `currency`, `method`, `reference`
- `paymentId` (output)

---

### 2. Loan Application Workflow
**Name:** `loan_application_workflow`  
**Category:** fintech  
**Description:** Complete loan application with eligibility check, KYC verification, and loan submission.

**Dependencies:**
- KYC status check

**End Action:** Submits loan application via `POST /loans/apply`

**State Schema Fields:**
- `customerId`, `accountId`, `amount`, `purpose`, `tenure`
- `collateral` (optional)
- `loanId`, `creditScore`, `eligible`, `status` (output)

---

### 3. Loan Approval Workflow
**Name:** `loan_approval_workflow`  
**Category:** fintech  
**Description:** Loan approval workflow that checks eligibility and approval status before approving.

**Dependencies:**
- Loan status check
- Loan details check

**End Action:** Approves loan via `POST /loans/{loanId}/approve`

**State Schema Fields:**
- `loanId`, `customerId`
- `approved`, `status`, `approvedAt`, `disbursedAt` (output)

---

### 4. Airtime Purchase Workflow
**Name:** `airtime_purchase_workflow`  
**Category:** fintech  
**Description:** Airtime purchase workflow that validates account and purchases airtime.

**Dependencies:**
- Account status check

**End Action:** Purchases airtime via `POST /airtime/purchase`

**State Schema Fields:**
- `phoneNumber`, `amount`, `provider`, `currency`, `accountId`
- `purchaseId`, `status`, `deliveryStatus` (output)

---

### 5. Airtime Completion Check Workflow
**Name:** `airtime_completion_check_workflow`  
**Category:** fintech  
**Description:** Workflow to check if airtime purchase has been completed and delivered.

**Dependencies:**
- Airtime status check

**End Action:** Gets airtime purchase details via `GET /airtime/purchases/{purchaseId}`

**State Schema Fields:**
- `purchaseId`
- `phoneNumber`, `status`, `deliveryStatus`, `completed`, `completedAt` (output)

---

### 6. Account Creation with KYC Workflow
**Name:** `account_creation_with_kyc_workflow`  
**Category:** fintech  
**Description:** Account creation workflow that creates an account and can verify KYC status.

**Dependencies:** None

**End Action:** Creates account via `POST /accounts`

**State Schema Fields:**
- `customerId`, `type`, `currency`
- `initialDeposit`, `kycLevel` (optional)
- `accountId`, `accountNumber`, `kycStatus`, `kycApproved` (output)

---

### 7. KYC Refresh Workflow
**Name:** `kyc_refresh_workflow`  
**Category:** fintech  
**Description:** KYC refresh workflow that updates KYC documents and verifies approval.

**Dependencies:** None

**End Action:** Refreshes KYC via `POST /kyc/customers/{customerId}/refresh`

**State Schema Fields:**
- `customerId`, `documents`, `level`
- `status`, `approved`, `riskRating` (output)

---

### 8. Transaction Transfer Workflow
**Name:** `transaction_transfer_workflow`  
**Category:** fintech  
**Description:** Transaction/transfer workflow that creates a transfer between accounts.

**Dependencies:**
- From account status check
- To account status check

**End Action:** Creates transaction via `POST /transactions`

**State Schema Fields:**
- `fromAccount`, `toAccount`, `amount`, `currency`
- `purpose` (optional)
- `debitTransactionId`, `creditTransactionId`, `status` (output)

---

### 9. Transaction Cleared Check Workflow
**Name:** `transaction_cleared_check_workflow`  
**Category:** fintech  
**Description:** Workflow to verify that a transaction has been cleared.

**Dependencies:**
- Transaction status check

**End Action:** Gets transaction details via `GET /transactions/{txnId}`

**State Schema Fields:**
- `txnId`
- `accountId`, `amount`, `status`, `cleared`, `processedAt` (output)

---

### 10. Payment Ready Check Workflow
**Name:** `payment_ready_check_workflow`  
**Category:** fintech  
**Description:** Workflow to verify that a payment is ready to process.

**Dependencies:**
- Payment status check

**End Action:** Gets payment details via `GET /payments/{paymentId}`

**State Schema Fields:**
- `paymentId`
- `accountId`, `amount`, `status`, `ready`, `kycComplete`, `sufficientBalance` (output)

---

### 11. Account Limit Update Workflow
**Name:** `account_limit_update_workflow`  
**Category:** fintech  
**Description:** Workflow to update account transaction limits.

**Dependencies:**
- Account existence check

**End Action:** Updates limits via `POST /limits/{accountId}/update`

**State Schema Fields:**
- `accountId`
- `dailyLimit`, `monthlyLimit` (optional)
- `currency` (output)

---

### 12. Account Status Update Workflow
**Name:** `account_status_update_workflow`  
**Category:** fintech  
**Description:** Workflow to update account status (active, suspended, closed).

**Dependencies:**
- Account existence check

**End Action:** Updates account status via `PATCH /accounts/{accountId}/status`

**State Schema Fields:**
- `accountId`, `status`
- `accountNumber`, `updatedAt` (output)

---

### 13. Payment Cancellation Workflow
**Name:** `payment_cancellation_workflow`  
**Category:** fintech  
**Description:** Workflow to cancel a pending payment.

**Dependencies:**
- Payment status check

**End Action:** Cancels payment via `POST /payments/{paymentId}/cancel`

**State Schema Fields:**
- `paymentId`
- `accountId`, `status`, `cancelled` (output)

---

### 14. Loan Rejection Workflow
**Name:** `loan_rejection_workflow`  
**Category:** fintech  
**Description:** Workflow to reject a loan application with a reason.

**Dependencies:**
- Loan status check

**End Action:** Rejects loan via `POST /loans/{loanId}/reject`

**State Schema Fields:**
- `loanId`, `reason`
- `status`, `rejectionReason` (output)

---

## Important Notes

### Checker Endpoints
The API documentation includes several "checker" endpoints (e.g., `/accounts/{accountId}/check-active`, `/loans/{loanId}/check-eligible`) that use **POST** method and return `{ result: true/false, reason: string, metadata: object }`.

However, workflow dependencies in this system only support **GET** methods. Therefore:
- **Dependencies** use regular GET endpoints to check status (e.g., `GET /accounts/{accountId}` to check account status)
- **Checker endpoints** (POST) can be used in the workflow execution logic or as separate workflows, but not as dependencies

### Path Parameters
Path parameters in endpoints (e.g., `{accountId}`, `{customerId}`) should be replaced with actual values from the workflow state data when making API calls.

### API Base URL
All workflows use the base URL: `https://mydummyapi.onrender.com/`

### Workflow Chaining
Some workflows are designed to chain together:
- `payment_processing_workflow` → `payment_ready_check_workflow`
- `loan_application_workflow` → `loan_approval_workflow` or `loan_rejection_workflow`
- `airtime_purchase_workflow` → `airtime_completion_check_workflow`
- `transaction_transfer_workflow` → `transaction_cleared_check_workflow`
- `account_creation_with_kyc_workflow` → `kyc_refresh_workflow` (if KYC not approved)

### Failure Handlers
Each workflow dependency includes an `on_failure` handler that:
- Can trigger another workflow (e.g., `kyc_refresh_workflow` when KYC check fails)
- Can make an API call to log errors or get additional information
- Helps maintain workflow resilience and error handling

## Usage Example

To use these workflows, import the JSON file and create workflow instances:

```json
{
  "template_id": "<workflow_template_id>",
  "conversation_id": "<conversation_id>",
  "user_id": "user-123",
  "state_data": {
    "accountId": "acc-001",
    "customerId": "cust-001",
    "beneficiary": "John Doe",
    "beneficiaryAccount": "9876543210",
    "amount": 200.00,
    "currency": "GHS",
    "method": "bank_transfer"
  }
}
```

## API Response Format

All workflows expect the API to return responses in this format:

**Success:**
```json
{
  "status": "success",
  "data": { /* Response data */ },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Checker Response:**
```json
{
  "result": true,
  "reason": "Human-readable explanation",
  "metadata": { /* Additional context */ },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

## Validation

The JSON file has been validated and is syntactically correct. All workflows follow the schema defined in `app/schemas/workflow.py`.


