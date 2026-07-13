from app.services.ai.assistant.learning.core.learning_engine import LearningEngine

class OnlineLearningEngine:
    """Triggers immediate reinforcement learning directly after a workflow finishes."""
    
    def __init__(self, learning_engine: LearningEngine):
        self.learning_engine = learning_engine
        
    def trigger_update(self):
        self.learning_engine.process_feedback_loop(