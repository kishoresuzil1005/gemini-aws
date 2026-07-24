from app.services.ai.routing.task_planner import TaskType

class ComplexityAnalyzer:
    @staticmethod
    def calculate(task_type: TaskType, prompt_size: int, resource_count: int) -> int:
        score = 0
        if task_type in [TaskType.ARCHITECTURE, TaskType.PLANNING]:
            score += 4
        elif task_type == TaskType.SECURITY:
            score += 2
            
        if resource_count > 100:
            score += 3
        elif resource_count > 20:
            score += 1
            
        if prompt_size > 15000: # Approx 3000 tokens
            score += 3
        elif prompt_size > 5000:
            score += 1
            
        return min(score, 10)
