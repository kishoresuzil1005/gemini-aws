from typing import List, Dict, Any, Optional
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.context.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.services.ai.assistant.assistant_models import ChatResponse
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult
from app.services.ai.assistant.actions.action_models import ActionResult

from app.services.ai.routing.task_planner import TaskPlanner
from app.services.ai.routing.model_router import ModelRouter
from app.services.ai.routing.provider_router import ProviderRouter, ProviderType
from app.services.ai.routing.complexity import ComplexityAnalyzer
import logging
import time

logger = logging.getLogger("RoutingLayer")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

from app.services.ai.assistant.response.confidence_engine import ConfidenceEngine
from app.services.ai.assistant.response.evidence_engine import EvidenceEngine
from app.services.ai.assistant.response.validation_engine import ValidationEngine
from app.services.ai.assistant.response.hallucination_detector import HallucinationDetector
from app.services.ai.assistant.response.source_attribution import SourceAttribution
from app.services.ai.assistant.response.explanation_builder import ExplanationBuilder
from app.services.ai.assistant.response.response_formatter import ResponseFormatter

class ResponseGenerator:
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.confidence_engine = ConfidenceEngine()
        self.evidence_engine = EvidenceEngine()
        self.validation = ValidationEngine()
        self.detector = HallucinationDetector()
        self.attribution = SourceAttribution()
        self.explainer = ExplanationBuilder()
        self.formatter = ResponseFormatter()

    def generate(self, question: str, history_str: str, context_str: str, intent: str, target: str, reasoning_result: ReasoningResult, request_id: str, stream: bool = False, action_result: Optional[ActionResult] = None) -> ChatResponse:
        prompt = build_user_prompt(question, history_str, context_str, intent)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        return self.generate_messages(
            messages=messages,
            context_str=context_str,
            intent=intent,
            target=target,
            reasoning_result=reasoning_result,
            request_id=request_id,
            stream=stream,
            action_result=action_result,
        )

    def generate_messages(self, messages: List[Dict[str, str]], context_str: str, intent: str, target: str, reasoning_result: ReasoningResult, request_id: str, stream: bool = False, action_result: Optional[ActionResult] = None) -> ChatResponse:
        """Generate a response from messages built by the canonical PromptBuilder."""
        start_time = time.time()
        
        task_type = TaskPlanner.map_intent(intent)
        prompt_size = sum(len(m.get("content", "")) for m in messages)
        # Use finding count or basic graph nodes as proxy for resources if available
        resource_count = len(reasoning_result.findings) if reasoning_result and reasoning_result.findings else 1
        
        complexity = ComplexityAnalyzer.calculate(task_type, prompt_size, resource_count)
        
        model_profile = ModelRouter.select_profile(task_type, complexity, resource_count)
        
        profile_name = "UNKNOWN"
        from app.services.ai.routing.model_profiles import MODEL_PROFILES
        for name, profile in MODEL_PROFILES.items():
            if profile["model"] == model_profile["model"]:
                profile_name = name
                break
        
        provider_type = ProviderType.OLLAMA
        routed_provider = ProviderRouter.get_provider(provider_type, self.provider)
        
        raw_answer = routed_provider.generate_response(messages=messages, request_id=request_id, model_profile=model_profile, stream=stream)
        
        total_time = time.time() - start_time
        logger.info(
            f"Routing Stats | Task: {task_type.value} | Complexity: {complexity} | "
            f"Profile: {profile_name} | Provider: {provider_type.value} | "
            f"Model: {model_profile['model']} | Total Time: {total_time:.2f}s"
        )
        
        # Phase 5: Production Explainable AI
        if self.detector.detect(raw_answer, context_str):
            raw_answer = "No evidence found. Unable to determine."
            
        if not self.validation.validate(raw_answer, {}):
             raw_answer = "Validation failed for the generated response."

        sources = list(set([f.source_tool for f in reasoning_result.findings])) if reasoning_result else []
        evidence = [e.description for e in reasoning_result.evidence] if reasoning_result else []
        tools_used = list(set([f.source_tool for f in reasoning_result.findings])) if reasoning_result else []
        confidence = self.confidence_engine.calculate(evidence, tools_used, raw_answer)
        
        if reasoning_result and reasoning_result.explanation:
            explanation = f"{raw_answer}\n\n---\n{reasoning_result.explanation}"
        else:
            explanation = self.explainer.build_explanation(raw_answer, evidence, sources)
        
        # We attach the extra metadata directly to ChatResponse for now
        response = ChatResponse(
            answer=explanation,
            intent=intent,
            resource=target,
            sources=sources
        )
        
        # We could also use the formatter if we had a richer model or dict return
        # formatted_dict = self.formatter.format_response(explanation, intent, target, evidence, sources, confidence, tools_used)
        response.confidence = confidence
        response.evidence = evidence
        response.tools_used = tools_used
        
        return response
