import pytest
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome
from app.services.ai.assistant.learning.core.learning_repository import LearningRepository
from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory
from app.services.ai.assistant.learning.prediction.success_predictor import SuccessPredictor
from app.services.ai.assistant.learning.prediction.failure_predictor import FailurePredictor
from app.services.ai.assistant.learning.engines.recommendation_engine import RecommendationEngine

def test_learning_pipeline():
    repo = LearningRepository()
    memory = DecisionMemory(repo)
    
    # Simulate 100 historical executions for "Restart EC2"
    # 98 successful, 2 failed
    for _ in range(98):
        memory.remember(ExecutionOutcome(
            workflow_id="wf-123",
            action="Restart EC2",
            status="SUCCESS",
            latency_ms=45000,
            user_accepted=True
        ))
        
    for _ in range(2):
        memory.remember(ExecutionOutcome(
            workflow_id="wf-124",
            action="Restart EC2",
            status="FAILURE",
            latency_ms=10000,
            user_accepted=True
        ))
        
    # Setup the intelligence predictors
    success_pred = SuccessPredictor(memory)
    fail_pred = FailurePredictor(memory)
    recommendation_engine = RecommendationEngine(success_pred, fail_pred)
    
    # Generate a scored recommendation based on historical memory
    score = recommendation_engine.generate_recommendation("Restart EC2")
    
    assert score.success_rate == 98.0
    assert score.predicted_failure_probability == 2.0
    assert score.confidence_score == 96.0 # 98.0 - 2.0
