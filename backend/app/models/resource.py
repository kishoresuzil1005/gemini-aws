import time
from sqlalchemy import Column, Integer, String, Float, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.database import Base

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
    
    # Phase 4
    metadata = Column(JSONB, nullable=True)
    scan_id = Column(UUID(as_uuid=True), nullable=True)
    resource_version = Column(Integer, default=1)

class ResourceNodeDB(Base):
    __tablename__ = "resource_nodes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(100), index=True, nullable=False, unique=True)
    resource_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=True)
    provider = Column(String(50), nullable=False)

class ResourceSnapshotDB(Base):
    __tablename__ = "resource_snapshots"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource_id = Column(String(255), index=True, nullable=False)
    snapshot_json = Column(Text, nullable=False)
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
