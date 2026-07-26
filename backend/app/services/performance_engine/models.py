from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PerformanceMetric(BaseModel):
    name: str
    value: float
    unit: str

class LatencyFinding(BaseModel):
    resource_id: str
    component: str
    latency_ms: float
    status: str

class ThroughputFinding(BaseModel):
    resource_id: str
    metric: str
    value: float
    capacity_percentage: float

class UtilizationFinding(BaseModel):
    resource_id: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_mbps: float

class BottleneckFinding(BaseModel):
    resource_id: str
    bottleneck_type: str
    severity: str
    description: str

class CapacityFinding(BaseModel):
    resource_id: str
    current_utilization: float
    peak_utilization: float
    headroom_percent: float
    saturation_risk: str

class ScalingRecommendation(BaseModel):
    resource_id: str
    scaling_type: str # 'HORIZONTAL', 'VERTICAL'
    action: str
    reason: str

class OptimizationOpportunity(BaseModel):
    category: str
    description: str
    expected_improvement: str

class PerformanceRecommendation(BaseModel):
    title: str
    description: str
    reason: str
    evidence: str
    dependencies: List[str]
    estimated_performance_gain: str
    cost_impact: str
    security_impact: str
    business_impact: str
    rollback_plan: str
    affected_resources: List[str]

class PerformanceAnomaly(BaseModel):
    resource_id: str
    anomaly_type: str
    description: str
    severity: str

class PerformanceTrend(BaseModel):
    metric: str
    direction: str
    rate: float

class PerformanceForecast(BaseModel):
    metric: str
    projected_value: float
    timeframe: str

class CapacityForecast(BaseModel):
    metric: str
    exhaustion_date: str
    headroom_trend: str

class GrowthForecast(BaseModel):
    metric: str
    growth_rate: float
    timeframe: str

class CrossEngineFinding(BaseModel):
    resource_id: str
    finding_type: str
    description: str
    cost_impact: float
    security_impact: str
    dependencies: List[str]

class CrossEngineRecommendation(BaseModel):
    title: str
    description: str
    cost_tradeoff: str
    security_tradeoff: str
    performance_gain: str

class ApplicationPerformanceFinding(BaseModel):
    resource_id: str
    metric: str
    latency_ms: float
    cache_hit_ratio: float
    thread_utilization: float
    status: str

class ApplicationOptimizationRecommendation(BaseModel):
    recommendation: str
    latency_improvement: str

class ApplicationPerformanceProfile(BaseModel):
    resource_id: str
    findings: List[ApplicationPerformanceFinding]
    recommendations: List[ApplicationOptimizationRecommendation]

class ApplicationPerformanceReport(BaseModel):
    profiles: List[ApplicationPerformanceProfile]

class DatabasePerformanceFinding(BaseModel):
    resource_id: str
    query_latency_ms: float
    lock_contention: float
    buffer_efficiency: float
    status: str

class DatabaseOptimizationRecommendation(BaseModel):
    recommendation: str

class DatabasePerformanceProfile(BaseModel):
    resource_id: str
    findings: List[DatabasePerformanceFinding]
    recommendations: List[DatabaseOptimizationRecommendation]

class NetworkPerformanceFinding(BaseModel):
    resource_id: str
    packet_loss: float
    latency_ms: float
    bandwidth_utilization: float
    status: str

class NetworkOptimizationRecommendation(BaseModel):
    recommendation: str

class ContainerPerformanceFinding(BaseModel):
    resource_id: str
    restart_count: int
    cpu_throttling: float
    oom_kills: int
    status: str

class ClusterPerformanceProfile(BaseModel):
    cluster_id: str
    findings: List[ContainerPerformanceFinding]
    recommendations: List[ScalingRecommendation]

class ServerlessPerformanceFinding(BaseModel):
    resource_id: str
    cold_starts: int
    timeouts: int
    concurrency_utilization: float
    status: str

class ServerlessOptimizationRecommendation(BaseModel):
    recommendation: str

class PredictivePerformanceReport(BaseModel):
    resource_id: str
    forecasts: List[PerformanceForecast]
    capacity_forecasts: List[CapacityForecast]
    growth_forecasts: List[GrowthForecast]
    capacity_exhaustion_date: str
    scaling_requirements: str

class PerformanceFinding(BaseModel):
    id: str
    title: str
    description: str
    resource_id: str
    finding_type: str
    recommendations: List[PerformanceRecommendation]

class RiskScore(BaseModel):
    score: int
    level: str

class PerformanceRisk(BaseModel):
    severity: str
    description: str
    risk_score: RiskScore
    confidence: float

class PerformanceScore(BaseModel):
    overall: int
    latency_score: int
    throughput_score: int
    utilization_score: int

class PerformanceProfile(BaseModel):
    resource_id: str
    score: PerformanceScore
    latency: LatencyFinding
    throughput: ThroughputFinding
    utilization: UtilizationFinding
    capacity: CapacityFinding
    anomalies: List[PerformanceAnomaly]
    bottlenecks: List[BottleneckFinding]
    recommendations: List[PerformanceRecommendation]
    forecasts: List[PerformanceForecast]
    application: Optional[ApplicationPerformanceProfile] = None
    database: Optional[DatabasePerformanceProfile] = None
    network: Optional[NetworkPerformanceFinding] = None
    container: Optional[ClusterPerformanceProfile] = None
    serverless: Optional[ServerlessPerformanceFinding] = None
    cross_engine: List[CrossEngineFinding] = Field(default_factory=list)
