# Workflow Template vs Workflow Instance

## Overview

The system uses a **Template-Instance pattern** similar to classes and objects in programming:

- **Workflow Template** = The blueprint/definition (like a class)
- **Workflow** = A specific execution/instance (like an object)

---

## Workflow Template

### What It Is
A **reusable definition** that describes how a workflow should work. It's like a blueprint or recipe.

### Purpose
- **Define the structure** of a workflow once
- **Reuse** the same workflow definition for multiple users/conversations
- **Manage** workflow definitions centrally
- **Control permissions** - decide which user types can access which workflows

### Key Characteristics
- ✅ **Reusable** - One template can create many workflow instances
- ✅ **Static** - Defines the "what" and "how", not the actual data
- ✅ **Shared** - Same template used by all users who have permission
- ✅ **Versioned** - Can be updated, activated/deactivated

### What It Contains
```json
{
  "name": "loan_application",                    // Template identifier
  "description": "Personal loan application",     // What it does
  "category": "fintech",                         // Category
  "guidelines": "Guide the applicant...",        // LLM instructions
  "state_schema": {                              // What data to collect
    "amount": {"type": "number", "required": true},
    "purpose": {"type": "string", "required": true}
  },
  "workflow_dependencies": [...],                // Dependencies configuration
  "end_action_type": "api_call",                 // What happens when done
  "end_action_target": {...},                    // End action configuration
  "is_active": true                              // Can it be used?
}
```

### Use Cases
1. **Define a new workflow type** - Create a template for "loan application"
2. **Update workflow structure** - Modify the template to change how all future instances work
3. **Manage availability** - Activate/deactivate templates
4. **Control access** - Assign templates to user types via permissions

### Example
Think of it like a **form template**:
- The template defines: "This form collects name, email, phone"
- The template doesn't contain actual user data
- Many users can fill out the same form template

---

## Workflow Instance

### What It Is
A **specific execution** of a workflow template for a particular user and conversation. It's the actual running workflow.

### Purpose
- **Track progress** for a specific user's workflow
- **Store actual data** collected during the workflow
- **Manage state** - what's been completed, what's pending
- **Handle dependencies** - track what the workflow is waiting for

### Key Characteristics
- ✅ **Unique** - Each instance is for a specific user/conversation
- ✅ **Dynamic** - Contains actual data and state
- ✅ **Tracked** - Has status, timestamps, progress
- ✅ **Isolated** - One user's workflow doesn't affect another's

### What It Contains
```json
{
  "id": "workflow-instance-uuid",               // Unique instance ID
  "template_id": "loan-application-template",   // Which template it's based on
  "conversation_id": "conversation-123",        // Which conversation
  "user_id": "user456",                         // Which user
  "status": "active",                           // Current status
  "state_data": {                               // ACTUAL data collected
    "amount": 50000,
    "purpose": "Home improvement",
    "full_name": "John Doe"
  },
  "pending_dependencies": {...},                // What it's waiting for
  "waiting_for": {...},                         // Current blocker
  "started_at": "2024-01-01T10:00:00Z",        // When it started
  "completed_at": null                          // When it finished (if done)
}
```

### Use Cases
1. **Start a workflow** - Create an instance when a user begins a loan application
2. **Update progress** - Update state_data as user provides information
3. **Check status** - See if workflow is active, waiting, or completed
4. **Resume workflow** - Continue a waiting workflow when dependencies are met

### Example
Think of it like a **filled-out form**:
- The instance contains: "John Doe, john@example.com, 555-1234"
- Each user gets their own instance
- The instance tracks whether the form is complete or still being filled

---

## Relationship

```
WorkflowTemplate (Blueprint)
    │
    ├─── Workflow Instance 1 (User A, Conversation 1)
    ├─── Workflow Instance 2 (User B, Conversation 2)
    ├─── Workflow Instance 3 (User A, Conversation 3)
    └─── ... (many more instances)
```

### One-to-Many Relationship
- **One template** can have **many instances**
- Each instance references **one template**
- All instances share the same structure from the template
- Each instance has its own unique data and state

---

## Real-World Analogy

### Workflow Template = Recipe
- Defines ingredients needed (state_schema)
- Defines steps to follow (guidelines)
- Defines what to do when done (end_action)
- Can be used by many cooks (users)

### Workflow Instance = Cooking Session
- A specific cook (user) following the recipe
- Has actual ingredients (state_data)
- Tracks progress (status, completed steps)
- Has a start time and (hopefully) a completion time

---

## Lifecycle Example

### 1. Create Template (One Time)
```bash
POST /api/workflow-templates
{
  "name": "loan_application",
  "state_schema": {...},
  "guidelines": "...",
  "end_action_type": "api_call",
  ...
}
```
**Result:** Template stored in database, ready to use

### 2. Assign Permission (One Time)
```bash
POST /api/permissions
{
  "user_type_id": "premium_users",
  "workflow_template_id": "loan_application_template_id"
}
```
**Result:** Premium users can now access this workflow

### 3. Create Instance (Many Times)
```bash
POST /api/workflows
{
  "template_id": "loan_application_template_id",
  "conversation_id": "conv_123",
  "user_id": "user_456"
}
```
**Result:** A new workflow instance created for this specific user/conversation

### 4. Update Instance (As User Progresses)
```bash
PUT /api/workflows/{workflow_id}
{
  "state_data": {
    "amount": 50000,
    "purpose": "Home improvement"
  }
}
```
**Result:** Workflow instance updated with new data

### 5. Complete Instance
```bash
PUT /api/workflows/{workflow_id}
{
  "status": "completed"
}
```
**Result:** Workflow instance marked as completed, end_action executed

---

## Key Differences Summary

| Aspect | Workflow Template | Workflow Instance |
|--------|------------------|-------------------|
| **Type** | Definition/Blueprint | Execution/Runtime |
| **Quantity** | One per workflow type | Many per template |
| **Data** | Structure only (schema) | Actual data (state_data) |
| **User** | Not tied to a user | Tied to specific user |
| **Conversation** | Not tied to conversation | Tied to specific conversation |
| **Status** | Active/Inactive | Active/Completed/Waiting/Failed/Cancelled |
| **Timestamps** | Created/Updated | Started/Completed/Last Interaction |
| **Purpose** | Define "how" | Track "what happened" |
| **Changes** | Affects all future instances | Only affects this instance |

---

## When to Use Each

### Use Workflow Template When:
- ✅ Defining a new type of workflow
- ✅ Updating workflow structure/requirements
- ✅ Managing which workflows are available
- ✅ Setting up permissions
- ✅ Viewing all available workflow types

### Use Workflow Instance When:
- ✅ Starting a workflow for a user
- ✅ Tracking user's progress
- ✅ Storing user's data
- ✅ Checking workflow status
- ✅ Resuming a waiting workflow
- ✅ Completing a workflow

---

## Example Scenario

### Scenario: Loan Application System

**Step 1: Create Template (Admin)**
```json
POST /api/workflow-templates
{
  "name": "loan_application",
  "state_schema": {
    "amount": {"type": "number", "required": true},
    "purpose": {"type": "string", "required": true}
  },
  "workflow_dependencies": [
    {
      "name": "kyc_verification",
      "api": {...},
      "on_failure": {...}
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://api.bank.com/loans/apply",
    "method": "POST"
  }
}
```
**Result:** Template created, ready to use

**Step 2: Assign Permission (Admin)**
```json
POST /api/permissions
{
  "user_type_id": "verified_users",
  "workflow_template_id": "loan_application_template_id"
}
```
**Result:** Verified users can now access loan application

**Step 3: User Starts Workflow**
```json
POST /api/workflows
{
  "template_id": "loan_application_template_id",
  "conversation_id": "conv_123",
  "user_id": "john_doe"
}
```
**Result:** Workflow instance created for John Doe

**Step 4: User Provides Data**
```json
PUT /api/workflows/{workflow_id}
{
  "state_data": {
    "amount": 50000,
    "purpose": "Home improvement"
  }
}
```
**Result:** John's workflow instance updated with his data

**Step 5: Complete Workflow**
```json
PUT /api/workflows/{workflow_id}
{
  "status": "completed"
}
```
**Result:** John's workflow completed, API called to submit loan application

---

## Benefits of This Pattern

1. **Reusability**: Define once, use many times
2. **Consistency**: All instances follow the same structure
3. **Maintainability**: Update template to change all future instances
4. **Scalability**: Can handle thousands of concurrent instances
5. **Isolation**: Each user's workflow is independent
6. **Tracking**: Can see all instances of a template for analytics

---

## Summary

- **Workflow Template** = The definition/blueprint (what the workflow is)
- **Workflow Instance** = The execution/runtime (what's happening for a specific user)

Think of it like:
- Template = A class definition
- Instance = An object created from that class

Or:
- Template = A form template
- Instance = A filled-out form

