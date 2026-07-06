from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class ResourceEdgeDB(Base):
    __tablename__ = "resource_edges"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_id = Column(String(100), index=True, nullable=False)
    target_id = Column(String(100), index=True, nullable=False)
    relationship = Column(String(100), nullable=True)

class ResourceRelationshipDB(Base):
    __tablename__ = "resource_relationships"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_resource_id = Column(Text, nullable=False)
    target_resource_id = Column(Text, nullable=False)
    relationship_type = Column(String(100), nullable=False)
