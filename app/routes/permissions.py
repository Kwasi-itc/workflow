from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..core.database import get_db
from ..schemas.workflow import (
    UserTypeWorkflowTemplateCreate,
    UserTypeWorkflowTemplateResponse,
)
from ..services.workflow_registry import WorkflowRegistry
from ..models.workflow import UserTypeWorkflowTemplate, WorkflowTemplate

router = APIRouter(prefix="/api/permissions", tags=["Permissions"])


@router.post("", response_model=UserTypeWorkflowTemplateResponse, status_code=201)
async def assign_workflow_to_user_type(
    permission: UserTypeWorkflowTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Assign a workflow template to a user type (grant permission).
    
    This allows the user type to access and use the workflow template.
    If the permission already exists, returns the existing association.
    """
    registry = WorkflowRegistry(db)
    
    # Verify template exists
    template = registry.get_template(permission.workflow_template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{permission.workflow_template_id}' not found",
                "workflow_template_id": str(permission.workflow_template_id)
            }
        )
    
    # Check if permission already exists
    existing = (
        db.query(UserTypeWorkflowTemplate)
        .filter(
            UserTypeWorkflowTemplate.user_type_id == str(permission.user_type_id),
            UserTypeWorkflowTemplate.workflow_template_id == str(permission.workflow_template_id)
        )
        .first()
    )
    
    if existing:
        # Return existing association (idempotent operation)
        return existing
    
    try:
        association = registry.assign_template_to_user_type(
            permission.user_type_id,
            permission.workflow_template_id
        )
        return association
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to assign workflow template to user type"
            }
        )


@router.delete("", status_code=204)
async def remove_workflow_from_user_type(
    user_type_id: UUID = Query(..., description="ID of the user type"),
    workflow_template_id: UUID = Query(..., description="ID of the workflow template"),
    db: Session = Depends(get_db)
):
    """
    Remove a workflow template from a user type (revoke permission).
    
    This revokes the user type's access to the workflow template.
    """
    registry = WorkflowRegistry(db)
    
    # Verify template exists (optional check for better error message)
    template = registry.get_template(workflow_template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{workflow_template_id}' not found",
                "workflow_template_id": str(workflow_template_id)
            }
        )
    
    try:
        removed = registry.remove_template_from_user_type(user_type_id, workflow_template_id)
        
        if not removed:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Permission not found",
                    "message": "Permission association not found",
                    "user_type_id": str(user_type_id),
                    "workflow_template_id": str(workflow_template_id),
                    "suggestion": "Check that the permission was previously assigned"
                }
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to remove workflow template from user type"
            }
        )


@router.get("/user-type/{user_type_id}", response_model=List[UserTypeWorkflowTemplateResponse])
async def get_permissions_for_user_type(
    user_type_id: UUID,
    is_active: Optional[bool] = Query(None, description="Filter by template active status"),
    db: Session = Depends(get_db)
):
    """
    Get all workflow permissions for a specific user type.
    
    Returns all workflow templates that have been assigned to the specified user type.
    Optionally filters by template active status.
    """
    query = (
        db.query(UserTypeWorkflowTemplate)
        .filter(UserTypeWorkflowTemplate.user_type_id == str(user_type_id))
    )
    
    # Apply active filter if requested
    if is_active is not None:
        query = query.join(WorkflowTemplate).filter(WorkflowTemplate.is_active == is_active)
    
    permissions = query.all()
    
    return permissions


@router.get("/workflow-template/{workflow_template_id}", response_model=List[UserTypeWorkflowTemplateResponse])
async def get_permissions_for_workflow_template(
    workflow_template_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all user types that have access to a specific workflow template.
    
    Returns all user types that have been granted permission to use the specified workflow template.
    """
    registry = WorkflowRegistry(db)
    
    # Verify template exists
    template = registry.get_template(workflow_template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{workflow_template_id}' not found",
                "workflow_template_id": str(workflow_template_id)
            }
        )
    
    permissions = (
        db.query(UserTypeWorkflowTemplate)
        .filter(UserTypeWorkflowTemplate.workflow_template_id == str(workflow_template_id))
        .all()
    )
    
    return permissions

