# Fintech Agent API - Complete Documentation

This document provides comprehensive API documentation for creating tools and workflows for intelligent agent chatbots.

## Base URL

```
http://localhost:3000
```

## Response Format

All endpoints return a consistent JSON structure:

**Success Response:**
```json
{
  "status": "success",
  "data": { /* Response data */ },
  "count": 0, // For list endpoints
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Checker Response:**
```json
{
  "result": true, // or false
  "reason": "Human-readable explanation",
  "metadata": { /* Additional context */ },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

---

## System Endpoints

### Health Check

**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

---

## Account Management

### List Accounts

**GET** `/accounts`

List all accounts with optional filters.

**Query Parameters:**
- `customerId` (string, optional) - Filter by customer ID
- `status` (string, optional) - Filter by status: `active`, `suspended`, `closed`
- `type` (string, optional) - Filter by type: `savings`, `current`
- `currency` (string, optional) - Filter by currency (e.g., `GHS`)

**Example Request:**
```
GET /accounts?customerId=cust-001&status=active
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "acc-001",
      "customerId": "cust-001",
      "type": "savings",
      "currency": "GHS",
      "balance": 5000.00,
      "status": "active",
      "accountNumber": "1234567890",
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T10:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Get Account Details

**GET** `/accounts/:accountId`

Get detailed information about a specific account.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Example Request:**
```
GET /accounts/acc-001
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "acc-001",
    "customerId": "cust-001",
    "type": "savings",
    "currency": "GHS",
    "balance": 5000.00,
    "status": "active",
    "accountNumber": "1234567890",
    "createdAt": "2024-01-15T10:00:00Z",
    "updatedAt": "2024-01-15T10:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Create Account

**POST** `/accounts`

Create a new account.

**Request Body:**
```json
{
  "customerId": "cust-001",
  "type": "savings",
  "currency": "GHS",
  "initialDeposit": 1000.00,
  "kycLevel": "tier2"
}
```

**Required Fields:**
- `customerId` (string)
- `type` (string) - `savings` or `current`
- `currency` (string)

**Optional Fields:**
- `initialDeposit` (number) - Default: 0
- `kycLevel` (string)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "acc-004",
    "customerId": "cust-001",
    "type": "savings",
    "currency": "GHS",
    "balance": 1000.00,
    "status": "active",
    "accountNumber": "1234567893",
    "createdAt": "2024-01-20T10:00:00Z",
    "updatedAt": "2024-01-20T10:00:00Z"
  },
  "message": "Account created successfully",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Update Account Status

**PATCH** `/accounts/:accountId/status`

Update the status of an account.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Request Body:**
```json
{
  "status": "suspended"
}
```

**Valid Status Values:**
- `active`
- `suspended`
- `closed`

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "acc-001",
    "status": "suspended",
    "updatedAt": "2024-01-20T10:00:00Z"
  },
  "message": "Account status updated",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Check Account Active (Checker)

**GET** `/accounts/:accountId/check-active`

**Checker endpoint** - Returns true/false indicating if account is active.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Response:**
```json
{
  "result": true,
  "reason": "Account is active",
  "metadata": {
    "accountId": "acc-001",
    "status": "active",
    "accountNumber": "1234567890"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Check if account is active before processing transactions or payments.

---

## Transactions & Transfers

### List Transactions

**GET** `/transactions`

List transactions with optional filters.

**Query Parameters:**
- `accountId` (string, optional) - Filter by account ID
- `status` (string, optional) - Filter by status: `pending`, `cleared`
- `type` (string, optional) - Filter by type: `debit`, `credit`
- `dateFrom` (string, optional) - Filter from date (ISO format)
- `dateTo` (string, optional) - Filter to date (ISO format)

**Example Request:**
```
GET /transactions?accountId=acc-001&status=cleared
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "txn-001",
      "accountId": "acc-001",
      "type": "debit",
      "amount": 100.00,
      "currency": "GHS",
      "description": "Payment to merchant",
      "status": "cleared",
      "counterparty": "merchant-123",
      "initiatedAt": "2024-01-18T09:00:00Z",
      "processedAt": "2024-01-18T09:05:00Z",
      "reference": "REF-001"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Get Transaction Details

**GET** `/transactions/:txnId`

Get details of a specific transaction.

**Path Parameters:**
- `txnId` (string, required) - Transaction ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "txn-001",
    "accountId": "acc-001",
    "type": "debit",
    "amount": 100.00,
    "currency": "GHS",
    "description": "Payment to merchant",
    "status": "cleared",
    "counterparty": "merchant-123",
    "initiatedAt": "2024-01-18T09:00:00Z",
    "processedAt": "2024-01-18T09:05:00Z",
    "reference": "REF-001"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Create Transaction/Transfer

**POST** `/transactions`

Create a new transaction/transfer between accounts.

**Request Body:**
```json
{
  "fromAccount": "acc-001",
  "toAccount": "acc-002",
  "amount": 100.00,
  "currency": "GHS",
  "purpose": "Payment for services"
}
```

**Required Fields:**
- `fromAccount` (string) - Source account ID
- `toAccount` (string) - Destination account ID
- `amount` (number) - Must be > 0
- `currency` (string)

**Optional Fields:**
- `purpose` (string) - Transaction description

**Response:**
```json
{
  "status": "success",
  "data": {
    "debitTransaction": {
      "id": "txn-004",
      "accountId": "acc-001",
      "type": "debit",
      "amount": 100.00,
      "currency": "GHS",
      "status": "pending",
      "reference": "REF-004"
    },
    "creditTransaction": {
      "id": "txn-005",
      "accountId": "acc-002",
      "type": "credit",
      "amount": 100.00,
      "currency": "GHS",
      "status": "pending",
      "reference": "REF-005"
    }
  },
  "message": "Transaction initiated",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Check Transaction Cleared (Checker)

**GET** `/transactions/:txnId/check-cleared`

**Checker endpoint** - Returns true/false indicating if transaction has been cleared.

**Path Parameters:**
- `txnId` (string, required) - Transaction ID

**Response:**
```json
{
  "result": true,
  "reason": "Transaction has been cleared",
  "metadata": {
    "transactionId": "txn-001",
    "status": "cleared",
    "amount": 100.00,
    "currency": "GHS",
    "processedAt": "2024-01-18T09:05:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify transaction completion before proceeding with dependent operations.

---

## Payments & Payouts

### Initiate Payment

**POST** `/payments/initiate`

Initiate a payment/payout to a beneficiary.

**Request Body:**
```json
{
  "accountId": "acc-001",
  "beneficiary": "John Doe",
  "beneficiaryAccount": "9876543210",
  "amount": 200.00,
  "currency": "GHS",
  "method": "bank_transfer",
  "reference": "PAY-REF-001"
}
```

**Required Fields:**
- `accountId` (string)
- `beneficiary` (string)
- `beneficiaryAccount` (string)
- `amount` (number) - Must be > 0
- `currency` (string)

**Optional Fields:**
- `method` (string) - Default: `bank_transfer`
- `reference` (string)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "pay-003",
    "accountId": "acc-001",
    "beneficiary": "John Doe",
    "beneficiaryAccount": "9876543210",
    "amount": 200.00,
    "currency": "GHS",
    "method": "bank_transfer",
    "status": "pending",
    "reference": "PAY-REF-001",
    "initiatedAt": "2024-01-20T10:00:00Z",
    "kycComplete": true,
    "sufficientBalance": true
  },
  "message": "Payment initiated",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Get Payment Details

**GET** `/payments/:paymentId`

Get details of a specific payment.

**Path Parameters:**
- `paymentId` (string, required) - Payment ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "pay-001",
    "accountId": "acc-001",
    "beneficiary": "John Doe",
    "beneficiaryAccount": "9876543210",
    "amount": 200.00,
    "currency": "GHS",
    "method": "bank_transfer",
    "status": "completed",
    "reference": "PAY-REF-001",
    "initiatedAt": "2024-01-18T08:00:00Z",
    "completedAt": "2024-01-18T08:15:00Z",
    "kycComplete": true,
    "sufficientBalance": true
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Cancel Payment

**POST** `/payments/:paymentId/cancel`

Cancel a pending payment.

**Path Parameters:**
- `paymentId` (string, required) - Payment ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "pay-002",
    "status": "cancelled"
  },
  "message": "Payment cancelled",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Note:** Cannot cancel completed payments.

### Check Payment Ready (Checker)

**GET** `/payments/:paymentId/check-ready`

**Checker endpoint** - Returns true/false indicating if payment is ready to process (KYC complete, sufficient balance, pending status).

**Path Parameters:**
- `paymentId` (string, required) - Payment ID

**Response:**
```json
{
  "result": true,
  "reason": "Payment is ready to process",
  "metadata": {
    "paymentId": "pay-001",
    "status": "pending",
    "kycComplete": true,
    "sufficientBalance": true,
    "amount": 200.00,
    "currency": "GHS"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify all prerequisites are met before processing payment.

---

## Loan Application Workflow

### Apply for Loan

**POST** `/loans/apply`

Submit a loan application.

**Request Body:**
```json
{
  "customerId": "cust-001",
  "accountId": "acc-001",
  "amount": 5000.00,
  "purpose": "Business expansion",
  "tenure": 12,
  "collateral": "Property documents"
}
```

**Required Fields:**
- `customerId` (string)
- `accountId` (string)
- `amount` (number) - Must be > 0
- `purpose` (string)
- `tenure` (integer) - Loan tenure in months

**Optional Fields:**
- `collateral` (string)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "loan-004",
    "customerId": "cust-001",
    "accountId": "acc-001",
    "amount": 5000.00,
    "currency": "GHS",
    "purpose": "Business expansion",
    "tenure": 12,
    "interestRate": 8.5,
    "status": "pending",
    "creditScore": 750,
    "eligible": true,
    "appliedAt": "2024-01-20T10:00:00Z",
    "monthlyPayment": 437.50
  },
  "message": "Loan application submitted",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Get Loan Details

**GET** `/loans/:loanId`

Get details of a specific loan application.

**Path Parameters:**
- `loanId` (string, required) - Loan ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "loan-001",
    "customerId": "cust-001",
    "accountId": "acc-001",
    "amount": 5000.00,
    "currency": "GHS",
    "purpose": "Business expansion",
    "tenure": 12,
    "interestRate": 8.5,
    "status": "approved",
    "creditScore": 750,
    "eligible": true,
    "appliedAt": "2024-01-10T09:00:00Z",
    "approvedAt": "2024-01-12T14:00:00Z",
    "disbursedAt": "2024-01-13T10:00:00Z",
    "monthlyPayment": 437.50,
    "remainingBalance": 5000.00
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### List Loans

**GET** `/loans`

List loans with optional filters.

**Query Parameters:**
- `customerId` (string, optional) - Filter by customer ID
- `status` (string, optional) - Filter by status: `pending`, `approved`, `rejected`
- `dateFrom` (string, optional) - Filter from date (ISO format)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "loan-001",
      "customerId": "cust-001",
      "amount": 5000.00,
      "status": "approved",
      "appliedAt": "2024-01-10T09:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Check Loan Eligible (Checker)

**GET** `/loans/:loanId/check-eligible`

**Checker endpoint** - Returns true/false indicating if loan is eligible (credit score >= 650).

**Path Parameters:**
- `loanId` (string, required) - Loan ID

**Response:**
```json
{
  "result": true,
  "reason": "Loan is eligible",
  "metadata": {
    "loanId": "loan-001",
    "creditScore": 750,
    "eligible": true,
    "amount": 5000.00,
    "status": "pending"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify eligibility before proceeding with loan approval workflow.

### Check Loan Approved (Checker)

**GET** `/loans/:loanId/check-approved`

**Checker endpoint** - Returns true/false indicating if loan has been approved.

**Path Parameters:**
- `loanId` (string, required) - Loan ID

**Response:**
```json
{
  "result": true,
  "reason": "Loan has been approved",
  "metadata": {
    "loanId": "loan-001",
    "status": "approved",
    "pendingChecks": [],
    "approvedAt": "2024-01-12T14:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify approval status before disbursement.

### Approve Loan

**POST** `/loans/:loanId/approve`

Approve a loan application (admin action).

**Path Parameters:**
- `loanId` (string, required) - Loan ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "loan-002",
    "status": "approved",
    "approvedAt": "2024-01-20T10:00:00Z",
    "disbursedAt": "2024-01-20T10:00:00Z",
    "remainingBalance": 3000.00
  },
  "message": "Loan approved and disbursed",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Note:** Can only approve loans with `pending` status.

### Reject Loan

**POST** `/loans/:loanId/reject`

Reject a loan application.

**Path Parameters:**
- `loanId` (string, required) - Loan ID

**Request Body:**
```json
{
  "reason": "Insufficient credit score"
}
```

**Optional Fields:**
- `reason` (string) - Rejection reason

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "loan-003",
    "status": "rejected",
    "rejectionReason": "Insufficient credit score"
  },
  "message": "Loan application rejected",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

---

## Airtime Purchase

### List Providers

**GET** `/airtime/providers`

Get list of available airtime providers/networks.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "MTN",
      "name": "MTN",
      "countries": ["GH", "NG", "ZA"]
    },
    {
      "id": "Vodafone",
      "name": "Vodafone",
      "countries": ["GH", "NG"]
    },
    {
      "id": "Airtel",
      "name": "Airtel",
      "countries": ["GH", "NG", "KE"]
    },
    {
      "id": "Tigo",
      "name": "Tigo",
      "countries": ["GH"]
    },
    {
      "id": "Orange",
      "name": "Orange",
      "countries": ["GH", "CI"]
    }
  ],
  "count": 5,
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Purchase Airtime

**POST** `/airtime/purchase`

Purchase airtime for a phone number.

**Request Body:**
```json
{
  "phoneNumber": "+233241234567",
  "amount": 10.00,
  "provider": "MTN",
  "currency": "GHS",
  "accountId": "acc-001"
}
```

**Required Fields:**
- `phoneNumber` (string) - Phone number with country code
- `amount` (number) - Must be > 0
- `provider` (string) - Provider ID (MTN, Vodafone, Airtel, Tigo, Orange)
- `accountId` (string)

**Optional Fields:**
- `currency` (string) - Default: `GHS`

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "air-003",
    "accountId": "acc-001",
    "phoneNumber": "+233241234567",
    "amount": 10.00,
    "currency": "GHS",
    "provider": "MTN",
    "status": "pending",
    "transactionReference": "AIR-REF-003",
    "purchasedAt": "2024-01-20T10:00:00Z",
    "deliveryStatus": "processing"
  },
  "message": "Airtime purchase initiated",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Note:** Purchase status changes to `completed` after ~2 seconds (simulated).

### Get Airtime Purchase Details

**GET** `/airtime/purchases/:purchaseId`

Get details of a specific airtime purchase.

**Path Parameters:**
- `purchaseId` (string, required) - Airtime purchase ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "air-001",
    "accountId": "acc-001",
    "phoneNumber": "+233241234567",
    "amount": 10.00,
    "currency": "GHS",
    "provider": "MTN",
    "status": "completed",
    "transactionReference": "AIR-REF-001",
    "purchasedAt": "2024-01-18T12:00:00Z",
    "completedAt": "2024-01-18T12:02:00Z",
    "deliveryStatus": "delivered"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### List Airtime Purchases

**GET** `/airtime/purchases`

List airtime purchases with optional filters.

**Query Parameters:**
- `accountId` (string, optional) - Filter by account ID
- `phoneNumber` (string, optional) - Filter by phone number
- `status` (string, optional) - Filter by status: `pending`, `completed`
- `dateFrom` (string, optional) - Filter from date (ISO format)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "air-001",
      "accountId": "acc-001",
      "phoneNumber": "+233241234567",
      "amount": 10.00,
      "provider": "MTN",
      "status": "completed"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Check Airtime Purchase Completed (Checker)

**GET** `/airtime/purchases/:purchaseId/check-completed`

**Checker endpoint** - Returns true/false indicating if airtime purchase has been completed.

**Path Parameters:**
- `purchaseId` (string, required) - Airtime purchase ID

**Response:**
```json
{
  "result": true,
  "reason": "Airtime purchase has been completed",
  "metadata": {
    "purchaseId": "air-001",
    "status": "completed",
    "deliveryStatus": "delivered",
    "phoneNumber": "+233241234567",
    "amount": 10.00,
    "provider": "MTN",
    "completedAt": "2024-01-18T12:02:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify airtime delivery before confirming to user.

---

## KYC (Know Your Customer)

### Get KYC Status

**GET** `/kyc/customers/:customerId`

Get KYC status for a customer.

**Path Parameters:**
- `customerId` (string, required) - Customer ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "customerId": "cust-001",
    "status": "approved",
    "level": "tier2",
    "documents": ["id", "proof_of_address"],
    "riskRating": "low",
    "verifiedAt": "2024-01-05T10:00:00Z",
    "expiresAt": "2025-01-05T10:00:00Z",
    "pendingItems": []
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Refresh KYC Check

**POST** `/kyc/customers/:customerId/refresh`

Refresh KYC check with updated documents.

**Path Parameters:**
- `customerId` (string, required) - Customer ID

**Request Body:**
```json
{
  "documents": ["id", "proof_of_address", "income_statement"],
  "level": "tier2"
}
```

**Optional Fields:**
- `documents` (array of strings) - List of submitted documents
- `level` (string) - KYC tier level

**Response:**
```json
{
  "status": "success",
  "data": {
    "customerId": "cust-001",
    "status": "approved",
    "level": "tier2",
    "documents": ["id", "proof_of_address", "income_statement"],
    "riskRating": "low",
    "pendingItems": []
  },
  "message": "KYC check refreshed",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Note:** Status becomes `approved` if 2+ documents are provided.

### Check KYC Approved (Checker)

**GET** `/kyc/customers/:customerId/check-approved`

**Checker endpoint** - Returns true/false indicating if KYC is approved.

**Path Parameters:**
- `customerId` (string, required) - Customer ID

**Response:**
```json
{
  "result": true,
  "reason": "KYC is approved",
  "metadata": {
    "customerId": "cust-001",
    "status": "approved",
    "level": "tier2",
    "riskRating": "low",
    "pendingItems": [],
    "verifiedAt": "2024-01-05T10:00:00Z",
    "expiresAt": "2025-01-05T10:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify KYC approval before allowing transactions or loan applications.

---

## Account Limits

### Get Account Limits

**GET** `/limits/:accountId`

Get account transaction limits.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "accountId": "acc-001",
    "dailyLimit": 1000.00,
    "monthlyLimit": 10000.00,
    "dailyUsed": 250.00,
    "monthlyUsed": 1200.00,
    "currency": "GHS",
    "dailyRemaining": 750.00,
    "monthlyRemaining": 8800.00,
    "dailyAvailable": true,
    "monthlyAvailable": true,
    "updatedAt": "2024-01-20T10:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Update Account Limits

**POST** `/limits/:accountId/update`

Update account transaction limits.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Request Body:**
```json
{
  "dailyLimit": 2000.00,
  "monthlyLimit": 20000.00
}
```

**Optional Fields:**
- `dailyLimit` (number) - Must be >= 0
- `monthlyLimit` (number) - Must be >= 0

**Note:** At least one limit must be provided.

**Response:**
```json
{
  "status": "success",
  "data": {
    "accountId": "acc-001",
    "dailyLimit": 2000.00,
    "monthlyLimit": 20000.00,
    "updatedAt": "2024-01-20T10:00:00Z"
  },
  "message": "Account limits updated",
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

### Check Limit Available (Checker)

**GET** `/limits/:accountId/check-available`

**Checker endpoint** - Returns true/false indicating if requested amount is within available limit.

**Path Parameters:**
- `accountId` (string, required) - Account ID

**Query Parameters:**
- `amount` (number, required) - Amount to check (must be > 0)
- `period` (string, optional) - `daily` or `monthly` (default: `daily`)

**Example Request:**
```
GET /limits/acc-001/check-available?amount=500.00&period=daily
```

**Response:**
```json
{
  "result": true,
  "reason": "Daily limit available: 750 GHS",
  "metadata": {
    "accountId": "acc-001",
    "period": "daily",
    "requestedAmount": 500.00,
    "remaining": 750.00,
    "limit": 1000.00,
    "used": 250.00,
    "currency": "GHS"
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "requestId": "req-1234567890-abc123"
}
```

**Use Case:** Verify sufficient limit before processing transactions or payments.

---

## Workflow Examples

### Example 1: Payment Processing Workflow

**Goal:** Process a payment with all prerequisite checks.

**Steps:**
1. Check account is active
   ```
   GET /accounts/acc-001/check-active
   ```
   - If `result: false`, stop workflow

2. Check KYC is approved
   ```
   GET /kyc/customers/cust-001/check-approved
   ```
   - If `result: false`, request KYC refresh

3. Check limit is available
   ```
   GET /limits/acc-001/check-available?amount=200.00&period=daily
   ```
   - If `result: false`, stop workflow

4. Initiate payment
   ```
   POST /payments/initiate
   Body: { "accountId": "acc-001", "beneficiary": "John Doe", ... }
   ```

5. Check payment is ready
   ```
   GET /payments/pay-003/check-ready
   ```
   - If `result: true`, proceed with processing

### Example 2: Loan Application Workflow

**Goal:** Process loan application with eligibility and approval checks.

**Steps:**
1. Submit loan application
   ```
   POST /loans/apply
   Body: { "customerId": "cust-001", "amount": 5000.00, ... }
   ```

2. Check loan eligibility
   ```
   GET /loans/loan-004/check-eligible
   ```
   - If `result: false`, reject loan

3. Check KYC is approved
   ```
   GET /kyc/customers/cust-001/check-approved
   ```
   - If `result: false`, request KYC refresh

4. Approve loan (if eligible and KYC approved)
   ```
   POST /loans/loan-004/approve
   ```

5. Verify approval
   ```
   GET /loans/loan-004/check-approved
   ```
   - Confirm `result: true` before disbursement

### Example 3: Airtime Purchase Workflow

**Goal:** Purchase airtime and verify delivery.

**Steps:**
1. Get available providers
   ```
   GET /airtime/providers
   ```

2. Purchase airtime
   ```
   POST /airtime/purchase
   Body: { "phoneNumber": "+233241234567", "amount": 10.00, ... }
   ```

3. Check completion (poll until complete)
   ```
   GET /airtime/purchases/air-003/check-completed
   ```
   - If `result: false`, wait and retry
   - If `result: true`, confirm delivery to user

### Example 4: Account Creation with KYC Workflow

**Goal:** Create account and verify KYC status.

**Steps:**
1. Create account
   ```
   POST /accounts
   Body: { "customerId": "cust-004", "type": "savings", ... }
   ```

2. Check KYC status
   ```
   GET /kyc/customers/cust-004
   ```

3. If KYC not approved, refresh KYC
   ```
   POST /kyc/customers/cust-004/refresh
   Body: { "documents": ["id", "proof_of_address"], ... }
   ```

4. Verify KYC approval
   ```
   GET /kyc/customers/cust-004/check-approved
   ```
   - If `result: true`, account is fully activated

---

## Checker Endpoints Summary

All checker endpoints follow this pattern:
- **Method:** GET
- **Response:** `{ result: true|false, reason: string, metadata: object }`
- **Purpose:** Enable conditional workflow logic

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `GET /accounts/:accountId/check-active` | Verify account is active | Pre-transaction validation |
| `GET /transactions/:txnId/check-cleared` | Verify transaction cleared | Post-transaction confirmation |
| `GET /payments/:paymentId/check-ready` | Verify payment ready to process | Pre-payment validation |
| `GET /loans/:loanId/check-eligible` | Verify loan eligibility | Pre-approval validation |
| `GET /loans/:loanId/check-approved` | Verify loan approved | Pre-disbursement validation |
| `GET /airtime/purchases/:purchaseId/check-completed` | Verify airtime delivered | Post-purchase confirmation |
| `GET /kyc/customers/:customerId/check-approved` | Verify KYC approved | Pre-transaction validation |
| `GET /limits/:accountId/check-available?amount=X&period=Y` | Verify limit available | Pre-transaction validation |

---

## Tool Creation Guidelines

### For Intelligent Agent Chatbots

1. **Use Checker Endpoints First**
   - Always verify prerequisites before executing actions
   - Use checker endpoints to build conditional logic
   - Handle `result: false` cases appropriately

2. **Error Handling**
   - Check `status: "error"` in responses
   - Read `message` field for error details
   - Use appropriate error messages to users

3. **Workflow Chaining**
   - Use IDs from previous responses in subsequent calls
   - Store `requestId` for debugging
   - Poll checker endpoints until conditions are met

4. **Data Validation**
   - Validate required fields before API calls
   - Check amount > 0 for financial operations
   - Verify account/entity exists before operations

5. **User Feedback**
   - Use `message` field from responses for user updates
   - Show `metadata` from checker responses for context
   - Display timestamps for audit trail

---

## Quick Reference

### Endpoint Categories

- **System:** `/health`
- **Accounts:** `/accounts/*`
- **Transactions:** `/transactions/*`
- **Payments:** `/payments/*`
- **Loans:** `/loans/*`
- **Airtime:** `/airtime/*`
- **KYC:** `/kyc/*`
- **Limits:** `/limits/*`

### Common HTTP Methods

- **GET** - Retrieve data (list or single item)
- **POST** - Create new resources or execute actions
- **PATCH** - Update specific fields

### Common Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation error)
- **404** - Not Found
- **500** - Internal Server Error

---

## Notes

- All data is in-memory (lost on server restart)
- Currency defaults to `GHS` (Ghanaian Cedis)
- All timestamps are in ISO 8601 format
- Request IDs are unique per request for tracking
- Checker endpoints are designed for workflow conditional logic

