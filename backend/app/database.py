import time
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Create PostgreSQL database engine
# We set pool_pre_ping to check active connections and prevent idle timeouts
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CloudAccountDB(Base):
    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    credentials_hint = Column(String(255), nullable=True)
    region = Column(String(100), nullable=False)
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


# Initialize Database (creates all tables in Postgres)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
