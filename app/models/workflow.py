from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Boolean, Text, CheckConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from ..core.database import Base


class WorkflowTemplate(Base):
    """
    Database model for workflow templates/types.
    Defines reusable workflow structures that can be instantiated.
    """
    __tablename__ = "workflow_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Basic Info
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Workflow Definition
    guidelines = Column(Text, nullable=True)  # Instructions for LLM on how to guide users
    state_schema = Column(JSON, nullable=False)  # Desired output JSON structure
    
    # Dependencies
    workflow_dependencies = Column(JSON, nullable=True)  # Array of workflow template names/IDs this workflow depends on
    
    # End Action
    end_action_type = Column(String(100), nullable=False)
    end_action_target = Column(JSON, nullable=True)  # Changed to JSON to support structured objects
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    workflow_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    workflows = relationship("Workflow", back_populates="template")
    user_type_associations = relationship("UserTypeWorkflowTemplate", back_populates="workflow_template", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "end_action_type IN ('api_call', 'workflow', 'none')",
            name="valid_end_action_type"
        ),
    )

    def __repr__(self):
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


class Workflow(Base):
    """
    Database model for workflow instances.
    Represents an active or completed workflow execution tied to a conversation.
    """
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Template Reference
    template_id = Column(String(36), ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Conversation Context
    # Note: Foreign key removed since 'conversations' table may be in a different module/database
    conversation_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # String to match Conversation.user_id type
    
    # Workflow State
    status = Column(String(50), nullable=False, default='active', index=True)
    state_data = Column(JSON, nullable=False, default=dict)
    
    # Dependency Tracking
    pending_dependencies = Column(JSON, nullable=True, default=dict)  # {workflow: [workflow_ids], external: [external_deps]}
    
    # Execution Tracking
    started_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    last_interaction_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # End Action Result
    end_action_result = Column(JSON, nullable=True)
    
    # Metadata
    workflow_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="workflows")
    # Note: Conversation relationship would need to be defined if Conversation model exists
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled', 'failed', 'waiting')",
            name="valid_status"
        ),
    )

    def __repr__(self):
        return f"<Workflow(id={self.id}, template_id={self.template_id}, status='{self.status}')>"


class UserTypeWorkflowTemplate(Base):
    """
    Association table for user types and workflow templates.
    Defines which workflows are available to which user types.
    """
    __tablename__ = "user_type_workflow_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Associations - Note: Foreign key removed since 'user_types' table may be in a different module/database
    user_type_id = Column(String(36), nullable=False, index=True)
    workflow_template_id = Column(String(36), ForeignKey("workflow_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    # Note: UserType relationship would need to be defined if UserType model exists
    workflow_template = relationship("WorkflowTemplate", back_populates="user_type_associations")

    # Constraints
    __table_args__ = (
        Index('unique_user_type_workflow', 'user_type_id', 'workflow_template_id', unique=True),
    )

    def __repr__(self):
        return f"<UserTypeWorkflowTemplate(user_type_id={self.user_type_id}, workflow_template_id={self.workflow_template_id})>"


# Create indexes for better query performance
Index('idx_workflow_templates_name', WorkflowTemplate.name)
Index('idx_workflow_templates_category', WorkflowTemplate.category)
Index('idx_workflow_templates_active', WorkflowTemplate.is_active)

Index('idx_workflows_template_id', Workflow.template_id)
Index('idx_workflows_conversation_id', Workflow.conversation_id)
Index('idx_workflows_user_id', Workflow.user_id)
Index('idx_workflows_status', Workflow.status)
Index('idx_workflows_status_created', Workflow.status, Workflow.created_at.desc())
Index('idx_workflows_user_status', Workflow.user_id, Workflow.status, Workflow.created_at.desc())

# Note: SQLite doesn't support partial unique indexes the same way PostgreSQL does
# This constraint should be enforced at the application level or via a unique constraint
# on (conversation_id, status) with a check, but SQLite limitations apply
# For now, we'll rely on application-level validation

Index('idx_user_type_workflow_user_type', UserTypeWorkflowTemplate.user_type_id)
Index('idx_user_type_workflow_template', UserTypeWorkflowTemplate.workflow_template_id)

