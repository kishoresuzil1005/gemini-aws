import time
import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class ScanHistoryDB(Base):
    __tablename__ = "scan_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    account_id = Column(String(50), nullable=True)
    scan_start = Column(DateTime, nullable=True)
    scan_end = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)
    
    # Phase 4 Metrics
    resources_found = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    duration = Column(Integer, default=0) # duration in seconds
