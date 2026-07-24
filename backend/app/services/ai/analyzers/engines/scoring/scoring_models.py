"""
Pure Scoring Models.
Independent models for calculating Risk, Confidence, and Priority.
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.services.ai.analyzers.base.analyzer_models import RiskLevel, Confidence, RecommendationPriority

class RiskScore(BaseModel):
    level: RiskLevel = Field(...)
    numeric_score: float = Field(..., description="0.0 to 100.0")
    reason: str = Field(...)

class ConfidenceScore(BaseModel):
    level: Confidence = Field(...)
    percentage: float = Field(..., description="0.0 to 100.0")
    reason: str = Field(...)

class PriorityScore(BaseModel):
    level: RecommendationPriority = Field(...)
    weight: int = Field(..., description="1 to 10 weight for sorting.")
    reason: str = Field(...)

class ImpactScore(BaseModel):
    business_impact: str = Field(...)
    technical_impact: str = Field(...)
