"""
Workflow Registry Service

Manages workflow templates and provides validation and discovery functionality.
This allows adding new workflows without writing code - just add templates via API.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json

from ..models.workflow import WorkflowTemplate, UserTypeWorkflowTemplate
from ..schemas.workflow import WorkflowTemplateCreate, WorkflowTemplateUpdate


class WorkflowRegistry:
    """Registry for managing workflow templates."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_template(self, template_data: WorkflowTemplateCreate) -> WorkflowTemplate:
        """
        Register a new workflow template.
        
        Args:
            template_data: Template creation data
            
        Returns:
            Created workflow template
        """
        # Validate template structure
        self._validate_template(template_data)
        
        # Create template
        template = WorkflowTemplate(**template_data.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def get_template(self, template_id: UUID) -> Optional[WorkflowTemplate]:
        """Get a workflow template by ID."""
        return self.db.query(WorkflowTemplate).filter(WorkflowTemplate.id == str(template_id)).first()
    
    def get_template_by_name(self, name: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by name."""
        return self.db.query(WorkflowTemplate).filter(WorkflowTemplate.name == name).first()
    
    def list_templates(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTemplate]:
        """
        List workflow templates with optional filtering and search.
        
        Args:
            category: Filter by category
            is_active: Filter by active status
            search: Search term to match in name and description (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return
        """
        query = self.db.query(WorkflowTemplate)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if is_active is not None:
            query = query.filter(WorkflowTemplate.is_active == is_active)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (WorkflowTemplate.name.ilike(search_term)) |
                (WorkflowTemplate.description.ilike(search_term))
            )
        
        return query.offset(skip).limit(limit).all()
    
    def update_template(
        self,
        template_id: UUID,
        template_data: WorkflowTemplateUpdate
    ) -> Optional[WorkflowTemplate]:
        """
        Update a workflow template.
        
        Args:
            template_id: ID of template to update
            template_data: Update data
            
        Returns:
            Updated template or None if not found
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        
        # Validate if state_schema is being updated
        if 'state_schema' in update_data:
            # Create a temporary template object for validation
            temp_data = {
                **{k: getattr(template, k) for k in ['name', 'description', 'category', 
                    'guidelines', 'state_schema', 'end_action_type', 
                    'end_action_target', 'is_active']},
                **update_data
            }
            self._validate_template_structure(temp_data)
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def delete_template(self, template_id: UUID) -> bool:
        """
        Delete a workflow template.
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            True if deleted, False if not found
        """
        template = self.get_template(template_id)
        if not template:
            return False
        
        self.db.delete(template)
        self.db.commit()
        return True
    
    def get_templates_for_user_type(self, user_type_id: UUID) -> List[WorkflowTemplate]:
        """
        Get all workflow templates available to a specific user type.
        
        Args:
            user_type_id: ID of the user type
            
        Returns:
            List of available workflow templates
        """
        return (
            self.db.query(WorkflowTemplate)
            .join(UserTypeWorkflowTemplate)
            .filter(
                and_(
                    UserTypeWorkflowTemplate.user_type_id == str(user_type_id),
                    WorkflowTemplate.is_active == True
                )
            )
            .all()
        )
    
    def assign_template_to_user_type(
        self,
        user_type_id: UUID,
        workflow_template_id: UUID
    ) -> UserTypeWorkflowTemplate:
        """
        Assign a workflow template to a user type (grant permission).
        
        Args:
            user_type_id: ID of the user type
            workflow_template_id: ID of the workflow template
            
        Returns:
            Created association
        """
        # Check if association already exists
        existing = (
            self.db.query(UserTypeWorkflowTemplate)
            .filter(
                and_(
                    UserTypeWorkflowTemplate.user_type_id == str(user_type_id),
                    UserTypeWorkflowTemplate.workflow_template_id == str(workflow_template_id)
                )
            )
            .first()
        )
        
        if existing:
            return existing
        
        association = UserTypeWorkflowTemplate(
            user_type_id=str(user_type_id),
            workflow_template_id=str(workflow_template_id)
        )
        self.db.add(association)
        self.db.commit()
        self.db.refresh(association)
        
        return association
    
    def remove_template_from_user_type(
        self,
        user_type_id: UUID,
        workflow_template_id: UUID
    ) -> bool:
        """
        Remove a workflow template from a user type (revoke permission).
        
        Args:
            user_type_id: ID of the user type
            workflow_template_id: ID of the workflow template
            
        Returns:
            True if removed, False if not found
        """
        association = (
            self.db.query(UserTypeWorkflowTemplate)
            .filter(
                and_(
                    UserTypeWorkflowTemplate.user_type_id == str(user_type_id),
                    UserTypeWorkflowTemplate.workflow_template_id == str(workflow_template_id)
                )
            )
            .first()
        )
        
        if not association:
            return False
        
        self.db.delete(association)
        self.db.commit()
        return True
    
    def _validate_template(self, template_data: WorkflowTemplateCreate) -> None:
        """Validate workflow template structure."""
        self._validate_template_structure(template_data.model_dump())
    
    def _validate_template_structure(self, template_dict: Dict[str, Any]) -> None:
        """
        Validate the structure of a workflow template.
        
        Args:
            template_dict: Template data as dictionary
            
        Raises:
            ValueError: If validation fails
        """
        # Validate state_schema (basic JSON Schema validation)
        state_schema = template_dict.get('state_schema', {})
        if not isinstance(state_schema, dict):
            raise ValueError("State schema must be a dictionary")
        
        # Validate workflow_dependencies if present
        workflow_dependencies = template_dict.get('workflow_dependencies')
        if workflow_dependencies:
            if not isinstance(workflow_dependencies, list):
                raise ValueError("workflow_dependencies must be a list")
            for dep in workflow_dependencies:
                if not isinstance(dep, dict):
                    raise ValueError("Each workflow dependency must be a dependency object")
                
                # Full dependency object format
                if 'name' not in dep:
                    raise ValueError("Workflow dependency must have 'name' field")
                if 'api' not in dep:
                    raise ValueError("Workflow dependency must have 'api' field")
                if 'on_failure' not in dep:
                    raise ValueError("Workflow dependency must have 'on_failure' field")
                
                # Validate api structure
                api = dep.get('api', {})
                if not isinstance(api, dict):
                    raise ValueError("Workflow dependency 'api' must be an object")
                if 'endpoint' not in api:
                    raise ValueError("Workflow dependency 'api' must have 'endpoint' field")
                if 'method' not in api:
                    raise ValueError("Workflow dependency 'api' must have 'method' field")
                
                # Workflow dependencies only support GET requests
                if api.get('method') != 'GET':
                    raise ValueError("Workflow dependency 'api.method' must be 'GET'")
                
                # Validate that body is null/empty for GET requests
                if api.get('method') == 'GET' and api.get('body') is not None and len(api.get('body', [])) > 0:
                    raise ValueError("Workflow dependency 'api.body' must be null or empty for GET requests")
                
                # Validate on_failure structure
                on_failure = dep.get('on_failure', {})
                if not isinstance(on_failure, dict):
                    raise ValueError("Workflow dependency 'on_failure' must be an object")
                if 'action_type' not in on_failure:
                    raise ValueError("Workflow dependency 'on_failure' must have 'action_type' field")
                if 'action_target' not in on_failure:
                    raise ValueError("Workflow dependency 'on_failure' must have 'action_target' field")
                
                valid_action_types = ['workflow', 'api_call']
                if on_failure.get('action_type') not in valid_action_types:
                    raise ValueError(f"Workflow dependency 'on_failure.action_type' must be one of: {', '.join(valid_action_types)}")
                
                # Validate action_target based on action_type
                action_target = on_failure.get('action_target', {})
                if not isinstance(action_target, dict):
                    raise ValueError("Workflow dependency 'on_failure.action_target' must be an object")
                
                if on_failure.get('action_type') == 'workflow':
                    if 'workflow_id' not in action_target:
                        raise ValueError("Workflow dependency 'on_failure.action_target' must have 'workflow_id' field when action_type is 'workflow'")
                elif on_failure.get('action_type') == 'api_call':
                    if 'endpoint' not in action_target:
                        raise ValueError("Workflow dependency 'on_failure.action_target' must have 'endpoint' field when action_type is 'api_call'")
                    if 'method' not in action_target:
                        raise ValueError("Workflow dependency 'on_failure.action_target' must have 'method' field when action_type is 'api_call'")
        
        # Validate end_action_type
        end_action_type = template_dict.get('end_action_type')
        valid_end_actions = ['api_call', 'workflow', 'none']
        if end_action_type not in valid_end_actions:
            raise ValueError(f"End action type must be one of: {', '.join(valid_end_actions)}")
        
        # Validate end_action_target based on end_action_type
        end_action_target = template_dict.get('end_action_target')
        if end_action_type == 'none':
            if end_action_target is not None:
                raise ValueError("end_action_target must be None when end_action_type is 'none'")
        elif end_action_type == 'api_call':
            if end_action_target is None:
                raise ValueError("end_action_target is required when end_action_type is 'api_call'")
            if not isinstance(end_action_target, dict):
                raise ValueError("end_action_target must be an object when end_action_type is 'api_call'")
            if 'endpoint' not in end_action_target:
                raise ValueError("end_action_target must have 'endpoint' field when end_action_type is 'api_call'")
            if 'method' not in end_action_target:
                raise ValueError("end_action_target must have 'method' field when end_action_type is 'api_call'")
        elif end_action_type == 'workflow':
            if end_action_target is None:
                raise ValueError("end_action_target is required when end_action_type is 'workflow'")
            if not isinstance(end_action_target, dict):
                raise ValueError("end_action_target must be an object when end_action_type is 'workflow'")
            if 'workflow_name' not in end_action_target:
                raise ValueError("end_action_target must have 'workflow_name' field when end_action_type is 'workflow'")

