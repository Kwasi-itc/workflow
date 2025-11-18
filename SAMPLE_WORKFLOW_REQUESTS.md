# Sample Workflow Template Request Bodies

These are 5 ready-to-use workflow template request bodies using **real, publicly available mock APIs** that you can actually test. All APIs are free and don't require authentication.

## Mock APIs Used

- **JSONPlaceholder** (https://jsonplaceholder.typicode.com/) - Fake REST API for testing
- **ReqRes** (https://reqres.in/) - Fake user API
- **HTTPBin** (https://httpbin.org/) - HTTP testing service

## 1. User Onboarding (User Existence Check)

```json
{
  "name": "user_onboarding",
  "description": "User onboarding workflow that checks if user exists in system, then creates new user profile",
  "category": "user_management",
  "guidelines": "Guide new users through the onboarding process. Check if user email already exists in the system, then collect basic information and create their profile.",
  "state_schema": {
    "username": {"type": "string", "minLength": 3, "maxLength": 30, "required": true},
    "email": {"type": "string", "format": "email", "required": true},
    "full_name": {"type": "string", "required": true},
    "phone_number": {"type": "string", "required": true},
    "preferred_language": {"type": "string", "enum": ["en", "es", "fr", "de"], "required": true},
    "newsletter_subscription": {"type": "boolean", "required": true},
    "terms_accepted": {"type": "boolean", "required": true}
  },
  "workflow_dependencies": [
    {
      "name": "email_availability_check",
      "api": {
        "endpoint": "https://jsonplaceholder.typicode.com/users",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["email"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "api_call",
        "action_target": {
          "endpoint": "https://httpbin.org/post",
          "method": "POST",
          "headers": ["Content-Type"],
          "query_params": [],
          "body": ["email", "error_message"],
          "timeout_seconds": 20
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://jsonplaceholder.typicode.com/users",
    "method": "POST",
    "headers": ["Content-Type"],
    "query_params": [],
    "body": ["username", "email", "full_name", "phone_number", "preferred_language"],
    "timeout_seconds": 30
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 5
  }
}
```

**Test the dependency API:**
```bash
# Returns array of user objects: [{id, name, username, email, phone, website, address, company}]
curl "https://jsonplaceholder.typicode.com/users"
```

## 2. Product Order Processing (Product Availability Check)

```json
{
  "name": "product_order_processing",
  "description": "Order processing workflow that checks product/post availability, then creates order/post",
  "category": "ecommerce",
  "guidelines": "Process a product order. Check if the product/post exists and is available, then collect shipping information and create the order.",
  "state_schema": {
    "product_id": {"type": "integer", "required": true},
    "quantity": {"type": "integer", "minimum": 1, "required": true},
    "shipping_address": {"type": "string", "required": true},
    "shipping_city": {"type": "string", "required": true},
    "shipping_postal_code": {"type": "string", "required": true},
    "payment_method": {"type": "string", "enum": ["credit_card", "debit_card", "paypal"], "required": true},
    "card_last_four": {"type": "string", "minLength": 4, "maxLength": 4}
  },
  "workflow_dependencies": [
    {
      "name": "inventory_check",
      "api": {
        "endpoint": "https://jsonplaceholder.typicode.com/posts",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["product_id"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "workflow",
        "action_target": {
          "workflow_id": "restock_notification_workflow_id",
          "workflow_name": "restock_notification"
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://jsonplaceholder.typicode.com/posts",
    "method": "POST",
    "headers": ["Content-Type"],
    "query_params": [],
    "body": ["product_id", "quantity", "shipping_address", "shipping_city", "shipping_postal_code", "payment_method"],
    "timeout_seconds": 30
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 8
  }
}
```

**Test the dependency API:**
```bash
# Returns post object: {userId, id, title, body}
curl "https://jsonplaceholder.typicode.com/posts/1"
```

## 3. Content Approval (Author Verification)

```json
{
  "name": "content_approval",
  "description": "Content submission workflow that verifies author/user exists, then creates content/post",
  "category": "content_management",
  "guidelines": "Collect content submission details. Verify that the author/user exists in the system before allowing submission.",
  "state_schema": {
    "content_type": {"type": "string", "enum": ["article", "video", "image", "document"], "required": true},
    "title": {"type": "string", "minLength": 5, "maxLength": 200, "required": true},
    "description": {"type": "string", "maxLength": 1000, "required": true},
    "tags": {"type": "string"},
    "author_id": {"type": "integer", "required": true},
    "publish_date": {"type": "string", "format": "date"}
  },
  "workflow_dependencies": [
    {
      "name": "author_permission_check",
      "api": {
        "endpoint": "https://reqres.in/api/users",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["id"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "api_call",
        "action_target": {
          "endpoint": "https://httpbin.org/post",
          "method": "POST",
          "headers": ["Content-Type"],
          "query_params": [],
          "body": ["author_id", "error_message"],
          "timeout_seconds": 20
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://jsonplaceholder.typicode.com/posts",
    "method": "POST",
    "headers": ["Content-Type"],
    "query_params": [],
    "body": ["content_type", "title", "description", "tags", "author_id", "publish_date"],
    "timeout_seconds": 30
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 10
  }
}
```

**Test the dependency API:**
```bash
# Returns: {data: {id, email, first_name, last_name, avatar}, support: {...}}
curl "https://reqres.in/api/users/1"
```

## 4. Event Registration (Event Existence Check)

```json
{
  "name": "event_registration",
  "description": "Event registration workflow that checks event/post exists, then creates registration/post",
  "category": "events",
  "guidelines": "Register user for an event. Verify that the event/post exists in the system before confirming registration.",
  "state_schema": {
    "event_id": {"type": "integer", "required": true},
    "attendee_name": {"type": "string", "required": true},
    "attendee_email": {"type": "string", "format": "email", "required": true},
    "dietary_requirements": {"type": "string"},
    "special_accommodations": {"type": "string"},
    "emergency_contact": {"type": "string", "required": true},
    "emergency_phone": {"type": "string", "required": true}
  },
  "workflow_dependencies": [
    {
      "name": "event_availability_check",
      "api": {
        "endpoint": "https://jsonplaceholder.typicode.com/posts",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["event_id"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "workflow",
        "action_target": {
          "workflow_id": "waitlist_workflow_id",
          "workflow_name": "event_waitlist"
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://jsonplaceholder.typicode.com/posts",
    "method": "POST",
    "headers": ["Content-Type"],
    "query_params": [],
    "body": ["event_id", "attendee_name", "attendee_email", "dietary_requirements", "emergency_contact"],
    "timeout_seconds": 30
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 6
  }
}
```

**Test the dependency API:**
```bash
# Returns post object: {userId, id, title, body}
curl "https://jsonplaceholder.typicode.com/posts/1"
```

## 5. Support Ticket Creation (User Verification + Existing Ticket Check)

```json
{
  "name": "support_ticket_creation",
  "description": "Create support ticket workflow that verifies user exists and checks existing tickets, then creates ticket/post",
  "category": "support",
  "guidelines": "Help user create a support ticket. Verify user account exists, check for existing tickets, then collect issue details and create the ticket.",
  "state_schema": {
    "user_id": {"type": "integer", "required": true},
    "issue_category": {"type": "string", "enum": ["technical", "billing", "account", "feature_request", "other"], "required": true},
    "subject": {"type": "string", "minLength": 5, "maxLength": 200, "required": true},
    "description": {"type": "string", "minLength": 10, "required": true},
    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "required": true},
    "attachments_count": {"type": "integer", "minimum": 0}
  },
  "workflow_dependencies": [
    {
      "name": "user_verification",
      "api": {
        "endpoint": "https://reqres.in/api/users",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["id"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "api_call",
        "action_target": {
          "endpoint": "https://httpbin.org/post",
          "method": "POST",
          "headers": ["Content-Type"],
          "query_params": [],
          "body": ["user_id", "error_message"],
          "timeout_seconds": 20
        }
      }
    },
    {
      "name": "existing_ticket_check",
      "api": {
        "endpoint": "https://jsonplaceholder.typicode.com/posts",
        "method": "GET",
        "headers": ["Content-Type"],
        "query_params": ["userId"],
        "body": null,
        "timeout_seconds": 30
      },
      "on_failure": {
        "action_type": "workflow",
        "action_target": {
          "workflow_id": "ticket_escalation_workflow_id",
          "workflow_name": "ticket_escalation"
        }
      }
    }
  ],
  "end_action_type": "api_call",
  "end_action_target": {
    "endpoint": "https://jsonplaceholder.typicode.com/posts",
    "method": "POST",
    "headers": ["Content-Type"],
    "query_params": [],
    "body": ["user_id", "issue_category", "subject", "description", "priority"],
    "timeout_seconds": 30
  },
  "is_active": true,
  "workflow_metadata": {
    "version": "1.0",
    "estimated_duration_minutes": 7
  }
}
```

**Test the dependency APIs:**
```bash
# User verification - Returns: {data: {id, email, first_name, last_name, avatar}, support: {...}}
curl "https://reqres.in/api/users/1"

# Existing ticket check - Returns array of posts: [{userId, id, title, body}]
curl "https://jsonplaceholder.typicode.com/posts?userId=1"
```

## How to Use

### Using cURL

```bash
# Example: Create User Onboarding workflow
curl -X POST "http://localhost:8000/api/workflow-templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "user_onboarding",
    "description": "User onboarding workflow with profile verification",
    ...
  }'
```

### Using Postman/Insomnia

1. Method: `POST`
2. URL: `http://localhost:8000/api/workflow-templates`
3. Headers: `Content-Type: application/json`
4. Body: Copy any of the examples above

### Testing the Mock APIs

All the APIs used are publicly available and can be tested:

**JSONPlaceholder:**
- GET `/users` - Returns array of user objects: `[{id, name, username, email, phone, website, address, company}]`
- GET `/users/{id}` - Returns single user object
- GET `/posts` - Returns array of post objects: `[{userId, id, title, body}]`
- GET `/posts/{id}` - Returns single post object
- POST `/users` - Creates user, returns created user with id
- POST `/posts` - Creates post, returns created post with id

**ReqRes:**
- GET `/api/users/{id}` - Returns: `{data: {id, email, first_name, last_name, avatar}, support: {...}}`
- GET `/api/users` - Returns paginated list: `{page, per_page, total, total_pages, data: [...]}`

**HTTPBin:**
- POST `/post` - Echoes back request data: `{json: {...}, data: "...", form: {...}, ...}`

## Notes

- ✅ All APIs are **publicly available** and **free**
- ✅ No authentication required
- ✅ All dependencies use **GET requests only**
- ✅ All examples are **validated** against the current schema
- ✅ Ready to test immediately
- ⚠️ These are mock APIs - they return fake data but demonstrate the workflow structure

## API Documentation

- **JSONPlaceholder**: https://jsonplaceholder.typicode.com/
- **ReqRes**: https://reqres.in/
- **HTTPBin**: https://httpbin.org/
