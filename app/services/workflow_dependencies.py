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
        
        pending = []
        satisfied = True
        
        for dep_name in workflow_deps:
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
            workflow.waiting_for = None
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
        waiting_for: Dict[str, Any]
    ) -> Workflow:
        """
        Set workflow status to 'waiting' with dependency info.
        
        Args:
            workflow: The workflow instance
            waiting_for: Dict describing what the workflow is waiting for
            
        Returns:
            Updated workflow
        """
        workflow.status = 'waiting'
        workflow.waiting_for = waiting_for
        
        # Update pending_dependencies
        pending = workflow.pending_dependencies or {}
        if waiting_for.get('type') == 'workflow':
            pending.setdefault('workflows', []).append(waiting_for)
        elif waiting_for.get('type') == 'external':
            pending.setdefault('external', []).append(waiting_for)
        
        workflow.pending_dependencies = pending
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow

