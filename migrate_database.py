"""
Database Migration Script

This script updates the database schema to match the current models.
It adds missing columns without dropping existing data.
Works with both SQLite and PostgreSQL.
"""
from sqlalchemy import text, inspect
from app.core.database import engine, Base
from app.models.workflow import WorkflowTemplate, Workflow, UserTypeWorkflowTemplate

def get_column_type_for_json(database_url: str) -> str:
    """Get the appropriate column type for JSON based on database."""
    if database_url.startswith("postgresql"):
        return "JSONB"  # PostgreSQL supports JSONB
    else:
        return "TEXT"  # SQLite stores JSON as TEXT

def migrate_database():
    """Add missing columns to existing tables."""
    from app.core.database import DATABASE_URL
    
    inspector = inspect(engine)
    json_type = get_column_type_for_json(DATABASE_URL)
    
    with engine.begin() as conn:  # Use begin() for transaction management
        # Check and add workflow_dependencies column to workflow_templates
        if 'workflow_templates' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('workflow_templates')]
            
            if 'workflow_dependencies' not in columns:
                print(f"Adding 'workflow_dependencies' column to workflow_templates ({json_type})...")
                conn.execute(text(f"ALTER TABLE workflow_templates ADD COLUMN workflow_dependencies {json_type}"))
                print("[OK] Added workflow_dependencies column")
            else:
                print("[OK] workflow_dependencies column already exists")
        
        # Check and add end_action_target column
        if 'workflow_templates' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('workflow_templates')]
            
            if 'end_action_target' in columns:
                print(f"[OK] end_action_target column exists ({json_type})")
            else:
                print(f"Adding 'end_action_target' column to workflow_templates ({json_type})...")
                conn.execute(text(f"ALTER TABLE workflow_templates ADD COLUMN end_action_target {json_type}"))
                print("[OK] Added end_action_target column")
        
        # Ensure all tables exist
        print("\nCreating any missing tables...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Database migration complete!")

        # Remove deprecated columns
        inspector = inspect(engine)
        if 'workflows' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('workflows')]
            if 'waiting_for' in columns:
                print("Removing deprecated 'waiting_for' column from workflows...")
                drop_stmt = "ALTER TABLE workflows DROP COLUMN waiting_for"
                try:
                    conn.execute(text(drop_stmt))
                    print("[OK] Removed waiting_for column")
                except Exception as exc:
                    print(f"[WARN] Failed to drop waiting_for column automatically: {exc}")
                    print("       Please remove it manually if your database supports DROP COLUMN.")

if __name__ == "__main__":
    print("Starting database migration...\n")
    migrate_database()
    print("\nMigration finished successfully!")

