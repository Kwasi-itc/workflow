from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from urllib.parse import unquote

from ..core.database import get_db
from ..schemas.workflow import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
)
from ..services.workflow_registry import WorkflowRegistry
from ..models.workflow import Workflow

router = APIRouter(prefix="/api/workflow-templates", tags=["Workflow Templates"])


@router.post("", response_model=WorkflowTemplateResponse, status_code=201)
async def create_workflow_template(
    template: WorkflowTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new workflow template.
    
    This allows adding new workflows without writing code - just define the template structure.
    """
    registry = WorkflowRegistry(db)
    
    # Check if template name already exists
    existing = registry.get_template_by_name(template.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Template name already exists",
                "message": f"Workflow template with name '{template.name}' already exists",
                "existing_template_id": str(existing.id)
            }
        )
    
    try:
        created_template = registry.register_template(template)
        return created_template
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to create workflow template"
            }
        )


@router.get("", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all workflow templates with optional filtering and search.
    
    Supports filtering by category and active status, and searching by name/description.
    """
    registry = WorkflowRegistry(db)
    templates = registry.list_templates(
        category=category,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=limit
    )
    return templates


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a workflow template by ID.
    
    Returns the full template definition including all configuration.
    """
    registry = WorkflowRegistry(db)
    template = registry.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{template_id}' not found",
                "template_id": str(template_id)
            }
        )
    
    return template


@router.get("/name/{name}", response_model=WorkflowTemplateResponse)
async def get_workflow_template_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get a workflow template by its unique name.
    
    The name parameter is URL-decoded automatically.
    """
    # URL decode the name in case it's encoded
    decoded_name = unquote(name)
    
    # Basic validation
    if not decoded_name or not decoded_name.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid name",
                "message": "Template name cannot be empty"
            }
        )
    
    registry = WorkflowRegistry(db)
    template = registry.get_template_by_name(decoded_name.strip())
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with name '{decoded_name}' not found",
                "name": decoded_name
            }
        )
    
    return template


@router.put("/{template_id}", response_model=WorkflowTemplateResponse)
async def update_workflow_template(
    template_id: UUID,
    template: WorkflowTemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a workflow template.
    
    All fields in the request body are optional. Only provided fields will be updated.
    """
    registry = WorkflowRegistry(db)
    
    # Check if template exists first
    existing_template = registry.get_template(template_id)
    if not existing_template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{template_id}' not found",
                "template_id": str(template_id)
            }
        )
    
    # Check if name is being updated and if it conflicts
    if template.name:
        name_conflict = registry.get_template_by_name(template.name)
        if name_conflict and name_conflict.id != template_id:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Template name already exists",
                    "message": f"Workflow template with name '{template.name}' already exists",
                    "existing_template_id": str(name_conflict.id)
                }
            )
    
    try:
        updated_template = registry.update_template(template_id, template)
        if not updated_template:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Template not found",
                    "message": f"Workflow template with ID '{template_id}' not found",
                    "template_id": str(template_id)
                }
            )
        return updated_template
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to update workflow template"
            }
        )


@router.delete("/{template_id}", status_code=204)
async def delete_workflow_template(
    template_id: UUID,
    force: bool = Query(False, description="Force delete even if active workflows exist"),
    db: Session = Depends(get_db)
):
    """
    Delete a workflow template.
    
    By default, prevents deletion if there are active workflow instances using this template.
    Set force=true to delete regardless of active workflows.
    """
    registry = WorkflowRegistry(db)
    
    # Check if template exists
    template = registry.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Template not found",
                "message": f"Workflow template with ID '{template_id}' not found",
                "template_id": str(template_id)
            }
        )
    
    # Check for active workflows if not forcing deletion
    if not force:
        active_workflows_count = (
            db.query(Workflow)
            .filter(
                Workflow.template_id == str(template_id),
                Workflow.status.in_(['active', 'waiting'])
            )
            .count()
        )
        
        if active_workflows_count > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Cannot delete template with active workflows",
                    "message": f"Template has {active_workflows_count} active or waiting workflow instance(s)",
                    "active_workflows_count": active_workflows_count,
                    "template_id": str(template_id),
                    "suggestion": "Set force=true to delete anyway, or wait for workflows to complete"
                }
            )
    
    try:
        deleted = registry.delete_template(template_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Template not found",
                    "message": f"Workflow template with ID '{template_id}' not found",
                    "template_id": str(template_id)
                }
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to delete workflow template"
            }
        )


@router.post("/bulk", status_code=201)
async def create_workflow_templates_bulk(
    templates: List[WorkflowTemplateCreate],
    skip_duplicates: bool = Query(False, description="Skip templates with duplicate names instead of failing"),
    db: Session = Depends(get_db)
):
    """
    Create multiple workflow templates in a single request.
    
    Accepts an array of workflow templates and creates them all. Useful for bulk imports.
    
    - If `skip_duplicates=true`, templates with existing names will be skipped
    - If `skip_duplicates=false` (default), the entire operation fails if any template name already exists
    
    Returns a summary with created templates, skipped templates (if any), and errors (if any).
    """
    registry = WorkflowRegistry(db)
    
    created_templates = []
    skipped_templates = []
    errors = []
    
    for idx, template in enumerate(templates):
        try:
            # Check if template name already exists
            existing = registry.get_template_by_name(template.name)
            if existing:
                if skip_duplicates:
                    skipped_templates.append({
                        "index": idx,
                        "name": template.name,
                        "reason": "Template name already exists",
                        "existing_template_id": str(existing.id)
                    })
                    continue
                else:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error": "Template name already exists",
                            "message": f"Workflow template with name '{template.name}' already exists at index {idx}",
                            "template_name": template.name,
                            "index": idx,
                            "existing_template_id": str(existing.id),
                            "suggestion": "Set skip_duplicates=true to skip duplicates"
                        }
                    )
            
            # Create the template
            created_template = registry.register_template(template)
            created_templates.append(WorkflowTemplateResponse.model_validate(created_template))
            
        except HTTPException:
            raise
        except ValueError as e:
            errors.append({
                "index": idx,
                "name": template.name if hasattr(template, 'name') else f"template_{idx}",
                "error": "Validation failed",
                "message": str(e)
            })
        except Exception as e:
            errors.append({
                "index": idx,
                "name": template.name if hasattr(template, 'name') else f"template_{idx}",
                "error": "Internal server error",
                "message": f"Failed to create workflow template: {str(e)}"
            })
    
    # If there are errors and we're not skipping duplicates, fail the entire operation
    if errors and not skip_duplicates:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bulk creation failed",
                "message": f"Failed to create {len(errors)} template(s)",
                "errors": errors,
                "created_count": len(created_templates),
                "total_count": len(templates)
            }
        )
    
    # Return results with summary
    response_data = {
        "created": created_templates,
        "summary": {
            "total": len(templates),
            "created": len(created_templates),
            "skipped": len(skipped_templates),
            "errors": len(errors)
        }
    }
    
    if skipped_templates:
        response_data["skipped"] = skipped_templates
    
    if errors:
        response_data["errors"] = errors
    
    # If nothing was created, return 400 with details
    if not created_templates:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "No templates created",
                "message": "All templates were skipped or failed",
                **response_data
            }
        )
    
    return response_data


@router.get("/user-type/{user_type_id}", response_model=List[WorkflowTemplateResponse])
async def get_templates_for_user_type(
    user_type_id: UUID,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all workflow templates available to a specific user type.
    
    Returns only templates that have been assigned to the specified user type via permissions.
    """
    registry = WorkflowRegistry(db)
    
    try:
        templates = registry.get_templates_for_user_type(user_type_id)
        
        # Apply additional filter if requested
        if is_active is not None:
            templates = [t for t in templates if t.is_active == is_active]
        
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve templates for user type"
            }
        )


