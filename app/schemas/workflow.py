from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List, Union, Literal
from uuid import UUID
from datetime import datetime


# Workflow Dependencies Schemas
class ApiConfig(BaseModel):
    """Schema for API configuration in workflow dependencies."""
    endpoint: str = Field(..., description="Full URL to check dependency status")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(..., description="HTTP method (supports all methods for checker endpoints)")
    headers: Optional[List[str]] = Field(None, description="Array of header names as strings")
    query_params: Optional[List[str]] = Field(None, description="Array of query parameter names as strings")
    body: Optional[Union[List[str], None]] = Field(None, description="Array of body keys as strings (should be null for GET requests)")
    
    @model_validator(mode='after')
    def validate_body_for_method(self):
        """Validate that body is null for GET requests."""
        if self.method == 'GET' and self.body is not None and len(self.body) > 0:
            raise ValueError("Body must be null or empty for GET requests")
        return self


class OnFailureWorkflowTarget(BaseModel):
    """Schema for workflow action_target in on_failure."""
    workflow_id: str = Field(..., description="ID of specific workflow instance to wait for")
    workflow_name: Optional[str] = Field(None, description="Name of workflow (for reference)")


class EndActionApiConfig(BaseModel):
    """Schema for API configuration in end actions (supports all HTTP methods)."""
    endpoint: str = Field(..., description="Full URL for the end action")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(..., description="HTTP method")
    headers: Optional[List[str]] = Field(None, description="Array of header names as strings")


class EndActionWorkflowTarget(BaseModel):
    """Schema for workflow end_action_target."""
    workflow_id: Optional[str] = Field(None, description="ID of specific workflow instance to trigger")
    workflow_name: str = Field(..., description="Name of workflow template to trigger")


class OnFailure(BaseModel):
    """Schema for on_failure handler in workflow dependencies. Only workflows are allowed."""
    action_type: Literal["workflow"] = Field(..., description="Type of failure handler (only 'workflow' is allowed)")
    action_target: OnFailureWorkflowTarget = Field(
        ..., 
        description="Workflow target configuration"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_action_target(cls, data: Any):
        """Parse action_target as workflow target."""
        if isinstance(data, dict):
            action_target_data = data.get('action_target')
            
            if isinstance(action_target_data, dict):
                # Validate and parse as OnFailureWorkflowTarget
                data['action_target'] = OnFailureWorkflowTarget.model_validate(action_target_data)
        
        return data


class WorkflowDependency(BaseModel):
    """Schema for a single workflow dependency."""
    name: str = Field(..., description="Name of the dependency")
    api: ApiConfig = Field(..., description="API configuration to check dependency")
    on_failure: Optional[OnFailure] = Field(None, description="Failure handler configuration (optional for legacy compatibility)")
    
    @model_validator(mode='before')
    @classmethod
    def handle_legacy_on_failure(cls, data: Any):
        """Handle legacy on_failure formats (API calls) by converting to None."""
        if isinstance(data, dict):
            on_failure_data = data.get('on_failure')
            if isinstance(on_failure_data, dict):
                # Check if it's legacy format (has 'endpoint' directly or missing 'action_target' with 'workflow_id')
                action_target = on_failure_data.get('action_target', {})
                if isinstance(action_target, dict):
                    # If action_target has 'endpoint', it's legacy API call format
                    if 'endpoint' in action_target:
                        # Legacy format - set to None
                        data['on_failure'] = None
                    # If action_target doesn't have 'workflow_id', it's invalid
                    elif 'workflow_id' not in action_target and on_failure_data.get('action_type') == 'workflow':
                        # Missing workflow_id - set to None
                        data['on_failure'] = None
                # If on_failure has 'endpoint' directly (old format), it's legacy
                elif 'endpoint' in on_failure_data:
                    data['on_failure'] = None
                # If action_type is not 'workflow', it's legacy
                elif on_failure_data.get('action_type') != 'workflow':
                    data['on_failure'] = None
        return data


# Workflow Template Schemas
class WorkflowTemplateBase(BaseModel):
    """Base schema for workflow template."""
    name: str = Field(..., description="Unique name of the workflow template", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Description of the workflow template")
    category: Optional[str] = Field(None, description="Category of the workflow", max_length=100)
    guidelines: Optional[str] = Field(None, description="Instructions for LLM on how to guide users")
    state_schema: Dict[str, Any] = Field(..., description="Desired output JSON structure (JSON Schema)")
    workflow_dependencies: Optional[List[WorkflowDependency]] = Field(
        None, 
        description="List of workflow dependencies"
    )
    end_action_type: Literal["api_call", "workflow", "none"] = Field(..., description="Type of end action")
    end_action_target: Optional[Union[EndActionApiConfig, EndActionWorkflowTarget]] = Field(
        None, 
        description="Target configuration based on end_action_type (required if end_action_type is not 'none')"
    )
    workflow_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: bool = Field(True, description="Whether the template is active")

    @field_validator('state_schema')
    @classmethod
    def validate_state_schema(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation for JSON schema structure."""
        if not isinstance(v, dict):
            raise ValueError("State schema must be a dictionary")
        return v
    
    @field_validator('workflow_dependencies')
    @classmethod
    def validate_workflow_dependencies(cls, v: Optional[List[WorkflowDependency]]) -> Optional[List[WorkflowDependency]]:
        """Validate workflow dependencies structure."""
        if v is None:
            return v
        
        for dep in v:
            if isinstance(dep, dict):
                # Should be validated as WorkflowDependency
                try:
                    WorkflowDependency.model_validate(dep)
                except Exception as e:
                    raise ValueError(f"Invalid workflow dependency structure: {e}")
            elif not isinstance(dep, WorkflowDependency):
                raise ValueError("Workflow dependencies must be dependency objects")
        
        return v
    
    @model_validator(mode='before')
    @classmethod
    def parse_end_action_target(cls, data: Any):
        """Parse end_action_target based on end_action_type."""
        if isinstance(data, dict):
            end_action_type = data.get('end_action_type')
            end_action_target_data = data.get('end_action_target')
            
            if end_action_type == "api_call" and isinstance(end_action_target_data, dict):
                # Validate and parse as EndActionApiConfig
                data['end_action_target'] = EndActionApiConfig.model_validate(end_action_target_data)
            elif end_action_type == "workflow" and isinstance(end_action_target_data, dict):
                # Validate and parse as EndActionWorkflowTarget
                data['end_action_target'] = EndActionWorkflowTarget.model_validate(end_action_target_data)
        
        return data
    
    @model_validator(mode='after')
    def validate_end_action(self):
        """Validate that end_action_target matches end_action_type."""
        if self.end_action_type == "none":
            if self.end_action_target is not None:
                raise ValueError("end_action_target must be None when end_action_type is 'none'")
        elif self.end_action_type == "api_call":
            if self.end_action_target is None:
                raise ValueError("end_action_target is required when end_action_type is 'api_call'")
            if not isinstance(self.end_action_target, EndActionApiConfig):
                raise ValueError("end_action_target must be EndActionApiConfig when end_action_type is 'api_call'")
        elif self.end_action_type == "workflow":
            if self.end_action_target is None:
                raise ValueError("end_action_target is required when end_action_type is 'workflow'")
            if not isinstance(self.end_action_target, EndActionWorkflowTarget):
                raise ValueError("end_action_target must be EndActionWorkflowTarget when end_action_type is 'workflow'")
        
        return self


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating a workflow template."""
    pass


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a workflow template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    guidelines: Optional[str] = None
    state_schema: Optional[Dict[str, Any]] = None
    workflow_dependencies: Optional[List[WorkflowDependency]] = None
    end_action_type: Optional[Literal["api_call", "workflow", "none"]] = None
    end_action_target: Optional[Union[EndActionApiConfig, EndActionWorkflowTarget]] = None
    workflow_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema for workflow template response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workflow Instance Schemas
class WorkflowBase(BaseModel):
    """Base schema for workflow instance."""
    template_id: UUID = Field(..., description="ID of the workflow template")
    conversation_id: UUID = Field(..., description="ID of the conversation")
    user_id: str = Field(..., description="ID of the user")
    state_data: Dict[str, Any] = Field(default_factory=dict, description="Current state data")
    workflow_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow instance."""
    pass


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow instance."""
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled|failed|waiting)$")
    state_data: Optional[Dict[str, Any]] = None
    pending_dependencies: Optional[Dict[str, Any]] = None
    end_action_result: Optional[Dict[str, Any]] = None
    workflow_metadata: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow instance response."""
    id: UUID
    template_id: UUID
    conversation_id: UUID
    user_id: str
    status: str
    state_data: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_interaction_at: datetime
    end_action_result: Optional[Dict[str, Any]] = None
    workflow_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Type Workflow Template Association Schemas
class UserTypeWorkflowTemplateCreate(BaseModel):
    """Schema for creating a user type workflow template association."""
    user_type_id: UUID = Field(..., description="ID of the user type")
    workflow_template_id: UUID = Field(..., description="ID of the workflow template")


class UserTypeWorkflowTemplateResponse(BaseModel):
    """Schema for user type workflow template association response."""
    id: UUID
    user_type_id: UUID
    workflow_template_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


