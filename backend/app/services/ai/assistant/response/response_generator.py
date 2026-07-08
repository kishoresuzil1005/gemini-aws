from typing import List, Dict, Any
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.context.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.services.ai.assistant.assistant_models import ChatResponse, ToolResponse

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

    def generate(self, question: str, history_str: str, context_str: str, intent: str, target: str, tool_responses: List[ToolResponse], request_id: str, stream: bool = False) -> ChatResponse:
        prompt = build_user_prompt(question, history_str, context_str, intent)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        raw_answer = self.provider.generate_response(messages=messages, request_id=request_id, stream=stream)
        
        # Phase 5: Production Explainable AI
        if self.detector.detect(raw_answer, context_str):
            raw_answer = "No evidence found. Unable to determine."
            
        if not self.validation.validate(raw_answer, {}):
             raw_answer = "Validation failed for the generated response."

        sources = self.attribution.attribute(target, tool_responses)
        evidence = self.evidence_engine.extract_evidence(tool_responses, raw_answer)
        tools_used = [tr.tool_name for tr in tool_responses]
        confidence = self.confidence_engine.calculate(evidence, tools_used, raw_answer)
        
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
