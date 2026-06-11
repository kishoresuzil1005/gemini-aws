import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Create PostgreSQL database engine
# We set pool_pre_ping to check active connections and prevent idle timeouts
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization_id = Column(Integer, nullable=True)
    role = Column(String(50), default="ORG_ADMIN") # SUPER_ADMIN, ORG_ADMIN, ENGINEER, VIEWER
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))


class OrganizationDB(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="BASIC") # BASIC, PREMIUM, ENTERPRISE
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))


class CloudAccountDB(Base):
    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, nullable=True)
    provider = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    credentials_hint = Column(String(255), nullable=True)
    region = Column(String(100), nullable=False)
    account_id = Column(String(100), nullable=True)
    role_arn = Column(String(255), nullable=True)
    status = Column(String(50), default="ACTIVE") # ACTIVE, DISCONNECTED, ERROR
    credentials_type = Column(String(100), nullable=True, default="STS_ROLE") # STS_ROLE, SERVICE_PRINCIPAL, SERVICE_ACCOUNT
    cloud_metadata = Column(Text, nullable=True) # JSON Metadata string
    permissions = Column(Text, nullable=True) # comma-separated permissions string
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))


class DiscoveryResourceDB(Base):
    __tablename__ = "discovery_resources"

    id = Column(String(100), primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    configuration_hint = Column(Text, nullable=True)
    cost_estimate = Column(Float, default=0.0)
    dependencies_string = Column(Text, default="")


class SavedMigrationDB(Base):
    __tablename__ = "saved_migrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    source_cloud = Column(String(50), nullable=False)
    target_cloud = Column(String(50), nullable=False)
    services_migrated = Column(String(255), nullable=False)
    terraform_code = Column(Text, nullable=False)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))


class CloudIncidentDB(Base):
    __tablename__ = "cloud_incidents"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False) # CRITICAL, WARNING, HEALTHY
    resource_id = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE") # ACTIVE, HEALING, RESOLVED
    timestamp = Column(String(50), nullable=False)


class BackgroundJobDB(Base):
    __tablename__ = "background_jobs"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    progress = Column(Float, default=0.0)
    status = Column(String(50), default="QUEUED") # QUEUED, RUNNING, COMPLETED, FAILED
    timestamp = Column(String(50), nullable=False)


class MetricDB(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(100), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(BigInteger, index=True, nullable=False)

class LogDB(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(100), index=True, nullable=True)
    severity = Column(String(50), default="INFO")
    message = Column(Text, nullable=False)
    timestamp = Column(BigInteger, index=True, nullable=False)

class AlertDB(Base):
    __tablename__ = "alerts"
    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="ACTIVE")
    timestamp = Column(BigInteger, index=True, nullable=False)

class CostReportDB(Base):
    __tablename__ = "cost_reports"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    period_start = Column(BigInteger, index=True, nullable=False)
    period_end = Column(BigInteger, index=True, nullable=False)

class AutomationActionDB(Base):
    __tablename__ = "automation_actions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    target_resource_id = Column(String(100), nullable=True)
    action_type = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING")
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

class ResourceNodeDB(Base):
    __tablename__ = "resource_nodes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(100), index=True, nullable=False, unique=True)
    resource_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=True)
    provider = Column(String(50), nullable=False)

class ResourceEdgeDB(Base):
    __tablename__ = "resource_edges"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_id = Column(String(100), index=True, nullable=False)
    target_id = Column(String(100), index=True, nullable=False)
    relationship = Column(String(100), nullable=True)

class ResourceDB(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cloud_account_id = Column(Integer, nullable=True)
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), index=True, nullable=False)
    name = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True) # JSON store
    discovered_at = Column(BigInteger, default=lambda: int(time.time() * 1000))
    instance_type = Column(String(100), nullable=True)
    instance_class = Column(String(100), nullable=True)
    size_gb = Column(Float, nullable=True)
    memory_size = Column(Integer, nullable=True)
    monthly_requests = Column(BigInteger, nullable=True)
    avg_duration_ms = Column(Float, nullable=True)

class ScanHistoryDB(Base):
    __tablename__ = "scan_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    account_id = Column(
        String(50),
        nullable=True
    )

    scan_start = Column(
        DateTime,
        nullable=True
    )

    scan_end = Column(
        DateTime,
        nullable=True
    )

    status = Column(
        String(50),
        nullable=True
    )

    resources_found = Column(
        Integer,
        default=0
    )

class ResourceRelationshipDB(Base):
    __tablename__ = "resource_relationships"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_resource_id = Column(String(255), nullable=False)
    target_resource_id = Column(String(255), nullable=False)
    relationship_type = Column(String(100), nullable=False)

class ResourceSnapshotDB(Base):
    __tablename__ = "resource_snapshots"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(255), index=True, nullable=False)
    snapshot_json = Column(Text, nullable=False)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))


class PricingCacheDB(Base):
    __tablename__ = "pricing_cache"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service = Column(String(50), nullable=False)
    sku = Column(String(255), nullable=True)
    resource_type = Column(String(100), nullable=True)
    price_per_hour = Column(Float, nullable=False)
    region = Column(String(50), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class OptimizationRecommendationDB(Base):
    __tablename__ = "optimization_recommendations"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    resource_id = Column(
        String(255),
        nullable=False
    )

    resource_type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(50),
        nullable=False
    )

    issue = Column(
        Text,
        nullable=False
    )

    recommendation = Column(
        Text,
        nullable=False
    )

    monthly_savings = Column(
        Float,
        default=0.0
    )

    created_at = Column(
        BigInteger,
        default=lambda:
        int(time.time() * 1000)
    )


class AnomalyDB(Base):
    __tablename__ = "anomalies"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    anomaly_type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(50),
        nullable=False
    )

    resource_id = Column(
        String(255),
        nullable=True
    )

    message = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="ACTIVE"
    )

    detected_at = Column(
        BigInteger,
        default=lambda: int(time.time() * 1000)
    )


class BudgetDB(Base):
    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    limit_amount = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        BigInteger,
        default=lambda: int(time.time() * 1000)
    )


class RemediationRequestDB(Base):
    __tablename__ = "remediation_requests"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    resource_id = Column(
        String(255),
        nullable=False
    )

    resource_type = Column(
        String(100),
        nullable=False
    )

    action = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        default="PENDING"
    )

    execution_result = Column(
        Text,
        nullable=True
    )

    executed_at = Column(
        BigInteger,
        nullable=True
    )

    created_at = Column(
        BigInteger,
        default=lambda: int(time.time() * 1000)
    )



# Initialize Database (creates all tables in Postgres or SQLite)
def init_db():
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
            ("avg_duration_ms", "DOUBLE PRECISION")
        ]
        for col_name, col_type in resources_cols:
            try:
                conn.execute(text(f"ALTER TABLE resources ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                # Silently catch as the column might already exist or driver doesn't support transaction commits
                pass
        
        # Drop NOT NULL on cloud_account_id if needed
        try:
            conn.execute(text("ALTER TABLE resources ALTER COLUMN cloud_account_id DROP NOT NULL"))
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
