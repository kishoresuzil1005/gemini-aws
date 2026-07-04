import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, BigInteger, DateTime
from app.database import Base

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
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    issue = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    monthly_savings = Column(Float, default=0.0)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

class AnomalyDB(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="ACTIVE")
    detected_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

class BudgetDB(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    limit_amount = Column(Float, nullable=False)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))

class RemediationRequestDB(Base):
    __tablename__ = "remediation_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING")
    execution_result = Column(Text, nullable=True)
    executed_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))
