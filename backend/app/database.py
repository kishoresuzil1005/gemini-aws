import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from app.models import (
        UserDB, OrganizationDB, CloudAccountDB, SavedMigrationDB, CloudIncidentDB,
        BackgroundJobDB, MetricDB, LogDB, AlertDB, CostReportDB, AutomationActionDB,
        ResourceDB, ResourceNodeDB, ResourceSnapshotDB, DiscoveryResourceDB,
        ScanHistoryDB, ResourceEdgeDB, ResourceRelationshipDB, PricingCacheDB,
        OptimizationRecommendationDB, AnomalyDB, BudgetDB, RemediationRequestDB
    )
    Base.metadata.create_all(bind=engine)
    
    # Self-healing migrations for existing tables and newly added schema properties
    from sqlalchemy import text
    with engine.connect() as conn:
        # columns to add to resources if not already present
        resources_cols = [
            ("instance_type", "VARCHAR(100)"),
            ("instance_class", "VARCHAR(100)"),
            ("size_gb", "DOUBLE PRECISION"),
            ("memory_size", "INTEGER"),
            ("monthly_requests", "BIGINT"),
            ("avg_duration_ms", "DOUBLE PRECISION"),
            ("metadata", "JSONB"),
            ("scan_id", "UUID"),
            ("resource_version", "INTEGER")
        ]
        for col_name, col_type in resources_cols:
            try:
                conn.execute(text(f"ALTER TABLE resources ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass
        
        try:
            conn.execute(text("ALTER TABLE resources ALTER COLUMN cloud_account_id DROP NOT NULL"))
            conn.commit()
        except Exception:
            pass

        # columns to add to scan_history
        scan_history_cols = [
            ("resources_found", "INTEGER"),
            ("errors", "INTEGER"),
            ("warnings", "INTEGER"),
            ("duration", "INTEGER")
        ]
        for col_name, col_type in scan_history_cols:
            try:
                conn.execute(text(f"ALTER TABLE scan_history ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass

        # columns to add to remediation_requests
        remediation_cols = [
            ("execution_result", "TEXT"),
            ("executed_at", "BIGINT")
        ]
        for col_name, col_type in remediation_cols:
            try:
                conn.execute(text(f"ALTER TABLE remediation_requests ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

