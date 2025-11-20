from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, cast, String
from typing import List, Optional, Dict
from uuid import UUID

from ..core.database import get_db
from ..schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
)
from ..models.workflow import Workflow, WorkflowTemplate
from ..services.workflow_dependencies import WorkflowDependencyService

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new workflow instance.
    
    Automatically checks workflow dependencies and sets status to 'waiting' if dependencies are not satisfied.
    Prevents creating multiple active workflows for the same conversation.
    """
    # Verify template exists
    template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == str(workflow.template_id)).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{workflow.template_id}' not found",
                "template_id": str(workflow.template_id)
            }
        )
    
    if not template.is_active:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Template is inactive",
                "message": "Cannot create workflow from inactive template",
                "template_id": str(workflow.template_id),
                "template_name": template.name
            }
        )
    
    # Check if there's already an active workflow for this conversation
    existing_active = (
        db.query(Workflow)
        .filter(
            and_(
                Workflow.conversation_id == str(workflow.conversation_id),
                Workflow.status.in_(['active', 'waiting'])
            )
        )
        .first()
    )
    
    if existing_active:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Active workflow exists",
                "message": f"An active or waiting workflow already exists for this conversation",
                "conversation_id": str(workflow.conversation_id),
                "existing_workflow_id": str(existing_active.id),
                "existing_workflow_status": existing_active.status,
                "suggestion": "Complete or cancel the existing workflow first"
            }
        )
    
    try:
        workflow_data = workflow.model_dump()
        workflow_data['template_id'] = str(workflow_data['template_id'])
        workflow_data['conversation_id'] = str(workflow_data['conversation_id'])
        
        workflow_instance = Workflow(**workflow_data)
        db.add(workflow_instance)
        db.commit()
        db.refresh(workflow_instance)
        
        # Access template relationship to trigger lazy load
        _ = workflow_instance.template
        
        # Check workflow-level dependencies
        dep_service = WorkflowDependencyService(db)
        workflow_deps = dep_service.check_workflow_dependencies(workflow_instance)
        
        # If workflow dependencies not satisfied, set to waiting
        if not workflow_deps.get('satisfied', True):
            pending_info = {
                'workflow_dependencies': workflow_deps
            }
            dep_service.set_workflow_waiting(workflow_instance, pending_info)
            db.commit()
            db.refresh(workflow_instance)
            # Access template relationship to trigger lazy load
            _ = workflow_instance.template
        
        return workflow_instance
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_details = str(e)
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": f"Failed to create workflow instance: {error_details}",
                "traceback": traceback_str
            }
        )


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    conversation_id: Optional[UUID] = Query(None, description="Filter by conversation ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    template_id: Optional[UUID] = Query(None, description="Filter by template ID"),
    status: Optional[str] = Query(None, description="Filter by status (active, completed, cancelled, failed, waiting)"),
    search: Optional[str] = Query(None, description="Search in workflow metadata (case-insensitive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all workflow instances with optional filtering and search.
    
    Supports filtering by conversation, user, template, and status.
    Also supports searching in workflow metadata.
    """
    # Validate status if provided
    valid_statuses = ['active', 'completed', 'cancelled', 'failed', 'waiting']
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid status",
                "message": f"Status must be one of: {', '.join(valid_statuses)}",
                "provided_status": status,
                "valid_statuses": valid_statuses
            }
        )
    
    query = db.query(Workflow)
    
    # Apply filters
    if conversation_id:
        query = query.filter(Workflow.conversation_id == str(conversation_id))
    
    if user_id:
        query = query.filter(Workflow.user_id == user_id)
    
    if template_id:
        query = query.filter(Workflow.template_id == str(template_id))
    
    if status:
        query = query.filter(Workflow.status == status)
    
    # Apply search in metadata
    if search:
        from app.core.database import DATABASE_URL
        search_term = f"%{search.lower()}%"
        
        # Use database-specific JSON search
        if DATABASE_URL.startswith("postgresql"):
            # PostgreSQL JSONB: cast to text for searching
            query = query.filter(
                cast(Workflow.workflow_metadata, String).ilike(search_term)
            )
        else:
            # SQLite: cast JSON (stored as TEXT) to String for searching
            query = query.filter(
                cast(Workflow.workflow_metadata, String).ilike(search_term)
            )
    
    # Order by most recent first
    query = query.order_by(Workflow.created_at.desc())
    
    workflows = query.offset(skip).limit(limit).all()
    
    # Load template relationships (access to trigger lazy load)
    for workflow in workflows:
        _ = workflow.template
    
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a workflow instance by ID.
    
    Returns the full workflow details including current state, status, and template information.
    """
    workflow = db.query(Workflow).filter(Workflow.id == str(workflow_id)).first()
    
    if not workflow:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Workflow not found",
                "message": f"Workflow with ID '{workflow_id}' not found",
                "workflow_id": str(workflow_id)
            }
        )
    
    # Access template relationship to trigger lazy load
    _ = workflow.template
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a workflow instance.
    
    All fields in the request body are optional. Only provided fields will be updated.
    Automatically checks dependencies and handles status transitions.
    """
    workflow_instance = db.query(Workflow).filter(Workflow.id == str(workflow_id)).first()
    
    if not workflow_instance:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Workflow not found",
                "message": f"Workflow with ID '{workflow_id}' not found",
                "workflow_id": str(workflow_id)
            }
        )
    
    # Validate status if provided
    valid_statuses = ['active', 'completed', 'cancelled', 'failed', 'waiting']
    update_data = workflow.model_dump(exclude_unset=True)
    
    if 'status' in update_data:
        if update_data['status'] not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid status",
                    "message": f"Status must be one of: {', '.join(valid_statuses)}",
                    "provided_status": update_data['status'],
                    "valid_statuses": valid_statuses
                }
            )
    
    try:
        dep_service = WorkflowDependencyService(db)
        
        # Handle status change to completed
        if 'status' in update_data and update_data['status'] == 'completed':
            from datetime import datetime
            update_data['completed_at'] = datetime.utcnow()
        
        # Check dependencies before allowing workflow to proceed (only if status is being changed to active)
        if 'status' in update_data and update_data['status'] == 'active':
            can_proceed = dep_service.can_proceed(workflow_instance)
            if not can_proceed.get('can_proceed', False):
                # Set workflow to waiting if dependencies not satisfied
                pending_info = {
                    'workflow_dependencies': can_proceed.get('workflow_dependencies', {})
                }
                dep_service.set_workflow_waiting(workflow_instance, pending_info)
                db.commit()
                db.refresh(workflow_instance)
                _ = workflow_instance.template
                
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Dependencies not satisfied",
                        "message": "Cannot proceed: workflow dependencies not satisfied",
                        "pending_dependencies": pending_info,
                        "dependencies": can_proceed,
                        "workflow_id": str(workflow_id)
                    }
                )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(workflow_instance, field, value)
        
        # If workflow was waiting, try to resume
        if workflow_instance.status == 'waiting':
            resume_result = dep_service.resume_workflow_if_ready(workflow_instance)
            if resume_result.get('resumed'):
                db.commit()
                db.refresh(workflow_instance)
                _ = workflow_instance.template
        
        db.commit()
        db.refresh(workflow_instance)
        # Access template relationship to trigger lazy load
        _ = workflow_instance.template
        
        return workflow_instance
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to update workflow instance"
            }
        )


@router.get("/{workflow_id}/dependencies", response_model=Dict)
async def check_workflow_dependencies(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Check workflow dependencies status.
    
    Returns detailed information about workflow dependencies, including:
    - Whether dependencies are satisfied
    - What the workflow is waiting for
    - Pending dependencies
    """
    workflow = db.query(Workflow).filter(Workflow.id == str(workflow_id)).first()
    
    if not workflow:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Workflow not found",
                "message": f"Workflow with ID '{workflow_id}' not found",
                "workflow_id": str(workflow_id)
            }
        )
    
    db.refresh(workflow, ['template'])
    
    try:
        dep_service = WorkflowDependencyService(db)
        workflow_deps = dep_service.check_workflow_dependencies(workflow)
        
        return {
            "workflow_id": str(workflow_id),
            "workflow_name": workflow.template.name if workflow.template else None,
            "status": workflow.status,
            "workflow_dependencies": workflow_deps,
            "pending_dependencies": workflow.pending_dependencies,
            "can_proceed": workflow_deps.get('satisfied', False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to check workflow dependencies"
            }
        )


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a workflow instance.
    
    Permanently removes the workflow from the database.
    This action cannot be undone.
    """
    workflow = db.query(Workflow).filter(Workflow.id == str(workflow_id)).first()
    
    if not workflow:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Workflow not found",
                "message": f"Workflow with ID '{workflow_id}' not found",
                "workflow_id": str(workflow_id)
            }
        )
    
    try:
        db.delete(workflow)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to delete workflow instance"
            }
        )

