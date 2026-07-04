import time
from sqlalchemy import Column, Integer, String, Float, Text, BigInteger
from app.database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization_id = Column(Integer, nullable=True)
    role = Column(String(50), default="ORG_ADMIN")
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

class OrganizationDB(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="BASIC")
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
    status = Column(String(50), default="ACTIVE")
    credentials_type = Column(String(100), nullable=True, default="STS_ROLE")
    cloud_metadata = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

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
    severity = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    timestamp = Column(String(50), nullable=False)

class BackgroundJobDB(Base):
    __tablename__ = "background_jobs"
    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    progress = Column(Float, default=0.0)
    status = Column(String(50), default="QUEUED")
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
