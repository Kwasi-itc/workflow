"""
Workflow Dependency Management Service

Handles dependency resolution, checking, and workflow resumption.
"""
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.workflow import Workflow, WorkflowTemplate


class WorkflowDependencyService:
    """Service for managing workflow dependencies and resolution."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _check_workflow_dependency(
        self,
        workflow: Workflow,
        workflow_identifier: str
    ) -> Dict[str, Any]:
        """Check if a workflow dependency is satisfied."""
        # Find the dependent workflow
        # Try by name first, then by ID
        dependent_workflow = (
            self.db.query(Workflow)
            .join(WorkflowTemplate)
            .filter(
                and_(
                    Workflow.user_id == workflow.user_id,
                    or_(
                        WorkflowTemplate.name == workflow_identifier,
                        WorkflowTemplate.id == workflow_identifier
                    ),
                    Workflow.status == 'completed'
                )
            )
            .order_by(Workflow.completed_at.desc())
            .first()
        )
        
        if dependent_workflow:
            return {
                'type': 'workflow',
                'workflow_name': workflow_identifier,
                'satisfied': True,
                'workflow_id': dependent_workflow.id
            }
        
        # Check if there's an active workflow (still in progress)
        active_workflow = (
            self.db.query(Workflow)
            .join(WorkflowTemplate)
            .filter(
                and_(
                    Workflow.user_id == workflow.user_id,
                    or_(
                        WorkflowTemplate.name == workflow_identifier,
                        WorkflowTemplate.id == workflow_identifier
                    ),
                    Workflow.status.in_(['active', 'waiting'])
                )
            )
            .first()
        )
        
        if active_workflow:
            return {
                'type': 'workflow',
                'workflow_name': workflow_identifier,
                'satisfied': False,
                'message': f'Dependent workflow {workflow_identifier} is still in progress',
                'workflow_id': active_workflow.id
            }
        
        return {
            'type': 'workflow',
            'workflow_name': workflow_identifier,
            'satisfied': False,
            'message': f'Dependent workflow {workflow_identifier} not found or not completed'
        }
    
    def check_workflow_dependencies(
        self,
        workflow: Workflow
    ) -> Dict[str, Any]:
        """
        Check if all workflow-level dependencies are satisfied.
        
        Note: This method currently only checks for workflow-to-workflow dependencies.
        API dependencies (the new structure) are not checked here - they should be
        checked by an API executor service that makes the actual HTTP calls.
        
        Args:
            workflow: The workflow instance
            
        Returns:
            Dict with 'satisfied' (bool) and 'pending' (list)
        """
        template = workflow.template
        if not template:
            return {'satisfied': False, 'pending': [], 'error': 'Template not found'}
        
        workflow_deps = template.workflow_dependencies or []
        if not workflow_deps:
            return {'satisfied': True, 'pending': []}
        
        # Handle new dependency structure (list of objects with name, api, on_failure)
        # For now, we skip API dependency checking here - that should be done by an API executor
        # This method only checks for workflow-to-workflow dependencies if they exist
        # in the on_failure handlers
        
        # If dependencies are API dependencies (new structure), we consider them satisfied
        # for workflow-to-workflow dependency purposes, as they'll be checked separately
        if workflow_deps and isinstance(workflow_deps[0], dict) and 'api' in workflow_deps[0]:
            # New structure: API dependencies - these are checked by API executor, not here
            # We only need to check if any on_failure handlers reference workflows
            # For now, we'll return satisfied since API dependencies are handled elsewhere
            return {'satisfied': True, 'pending': []}
        
        # Old structure: list of workflow names/IDs (backward compatibility)
        pending = []
        satisfied = True
        
        for dep in workflow_deps:
            # Extract dependency identifier
            if isinstance(dep, dict):
                dep_name = dep.get('name') or dep.get('workflow_name') or str(dep)
            else:
                dep_name = str(dep)
            
            dep_info = self._check_workflow_dependency(workflow, dep_name)
            if not dep_info.get('satisfied', False):
                satisfied = False
                pending.append(dep_info)
        
        return {
            'satisfied': satisfied,
            'pending': pending
        }
    
    def can_proceed(
        self,
        workflow: Workflow
    ) -> Dict[str, Any]:
        """
        Check if workflow can proceed (all dependencies satisfied).
        
        Args:
            workflow: The workflow instance
            
        Returns:
            Dict with 'can_proceed' (bool), 'reason' (str), and dependency info
        """
        # Check workflow-level dependencies
        workflow_deps = self.check_workflow_dependencies(workflow)
        if not workflow_deps.get('satisfied', False):
            return {
                'can_proceed': False,
                'reason': 'workflow_dependencies',
                'workflow_dependencies': workflow_deps
            }
        
        return {
            'can_proceed': True,
            'workflow_dependencies': workflow_deps
        }
    
    def resume_workflow_if_ready(
        self,
        workflow: Workflow
    ) -> Dict[str, Any]:
        """
        Check if a waiting workflow can be resumed.
        If all dependencies are satisfied, update status to 'active'.
        
        Args:
            workflow: The workflow instance
            
        Returns:
            Dict with 'resumed' (bool) and status info
        """
        if workflow.status != 'waiting':
            return {
                'resumed': False,
                'reason': f'Workflow is not in waiting status (current: {workflow.status})'
            }
        
        # Check all dependencies
        workflow_deps = self.check_workflow_dependencies(workflow)
        
        # If all dependencies satisfied, resume
        if workflow_deps.get('satisfied', True):
            workflow.status = 'active'
            workflow.pending_dependencies = {}
            self.db.commit()
            self.db.refresh(workflow)
            
            return {
                'resumed': True,
                'status': 'active',
                'workflow_dependencies': workflow_deps
            }
        
        # Still waiting
        return {
            'resumed': False,
            'reason': 'Dependencies not yet satisfied',
            'workflow_dependencies': workflow_deps
        }
    
    def set_workflow_waiting(
        self,
        workflow: Workflow,
        pending_dependencies: Dict[str, Any]
    ) -> Workflow:
        """
        Set workflow status to 'waiting' and capture pending dependency data.
        
        Args:
            workflow: The workflow instance
            pending_dependencies: Dict describing what remains pending
            
        Returns:
            Updated workflow
        """
        workflow.status = 'waiting'
        workflow.pending_dependencies = pending_dependencies or {}
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow

