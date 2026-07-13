from typing import Dict, Any, List
from app.services.ai.assistant.memory.memory_manager import MemoryManager
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.memory.session_manager import SessionManager
from app.services.ai.assistant.history.history_manager import HistoryManager
from app.services.ai.assistant.conversation.conversation_manager import ConversationManager
from app.services.ai.assistant.intent_classifier import IntentClassifier
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.planner import Planner
from app.services.ai.assistant.plan_executor import PlanExecutor
from app.services.ai.assistant.execution_plan import PlanStatus
from app.services.ai.assistant.context.context_builder import ContextBuilder
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine
from app.services.ai.assistant.response.response_generator import ResponseGenerator

from app.services.ai.assistant.actions.action_models import ActionRequest, ActionContext, ActionResult, ActionStatus
from app.services.ai.assistant.actions.action_planner import ActionPlanner
from app.services.ai.assistant.actions.action_validator import ActionValidator
from app.services.ai.assistant.actions.policy_engine import PolicyEngine
from app.services.ai.assistant.actions.approval_engine import ApprovalEngine
from app.services.ai.assistant.actions.dry_run_engine import DryRunEngine
from app.services.ai.assistant.actions.action_executor import ActionExecutor
from app.services.ai.assistant.actions.rollback_manager import RollbackManager
from app.services.ai.assistant.actions.execution_logger import ExecutionLogger
from app.services.ai.assistant.actions.audit_engine import AuditEngine
from app.services.ai.assistant.actions.action_state_machine import ActionStateMachine
from app.providers.provider_registry import ProviderRegistry
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider
from app.providers.aws.aws_provider import AWSProvider
from app.providers.azure.azure_provider import AzureProvider
from app.providers.gcp.gcp_provider import GCPProvider
from app.providers.kubernetes.kubernetes_provider import KubernetesProvider
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.ollama_provider import OllamaProvider
from app.services.ai.assistant.llm.config import settings
from app.services.ai.assistant.resource_validator import ResourceValidator
from app.services.ai.assistant.resource_extractor import ResourceExtractor
import uuid
from app.services.ai.assistant.assistant_models import ChatResponse, ChatRequest

class GraphAssistant:
    def __init__(self, memory_manager: MemoryManager = None, provider: BaseProvider = None):
        if not memory_manager:
            memory_store = MemoryStore()
            memory_manager = MemoryManager(memory_store)
        self.memory = memory_manager
        
        self.session_manager = SessionManager()
        self.history_manager = HistoryManager(self.memory.store)
        self.conversation = ConversationManager(self.memory, self.session_manager, self.history_manager)
        
        self.classifier = IntentClassifier()
        self.extractor = ResourceExtractor()
        self.planner = Planner()
        self.tool_router = ToolRouter()
        self.plan_executor = PlanExecutor(self.tool_router)
        self.reasoning_engine = ReasoningEngine()
        self.context_builder = ContextBuilder()
        self.provider = provider or OllamaProvider(settings)
        self.generator = ResponseGenerator(self.provider)
        self.validator = ResourceValidator(self.memory)

        # Action Subsystem
        self.action_state_machine = ActionStateMachine()
        self.action_planner = ActionPlanner()
        self.action_validator = ActionValidator(self.action_state_machine)
        self.policy_engine = PolicyEngine(self.action_state_machine)
        self.approval_engine = ApprovalEngine(self.action_state_machine, testing_mode=True)
        self.dry_run_engine = DryRunEngine()
        self.provider_registry = ProviderRegistry()
        self.provider_registry.register(CloudProvider.AWS, lambda: AWSProvider())
        self.provider_registry.register(CloudProvider.AZURE, lambda: AzureProvider())
        self.provider_registry.register(CloudProvider.GCP, lambda: GCPProvider())
        self.provider_registry.register(CloudProvider.KUBERNETES, lambda: KubernetesProvider())
        self.action_executor = ActionExecutor(self.provider_registry, self.action_state_machine)
        self.rollback_manager = RollbackManager()
        self.execution_logger = ExecutionLogger()
        self.audit_engine = AuditEngine()

    def chat(self, request: ChatRequest, stream: bool = False) -> ChatResponse:
        request_id = str(uuid.uuid4())
        print(f"[Req: {request_id}] Starting AI Chat for Conversation: {request.conversation_id}")
        
        # 1. Intent Classification & Candidate Extraction
        intent_data = self.classifier.classify(request.message)
        candidate = self.extractor.extract(request.message)
        
        # 2. Resource Resolution
        resolved = self.validator.resolve(candidate, request.conversation_id)
        
        # 3. Short-circuit on missing resources
        if candidate and resolved.confidence < 1.0 and intent_data.get("intent") not in ["DOCUMENTATION", "UNKNOWN"]:
            return ChatResponse(
                status="error",
                data=None,
                errors=[
                    {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Resource '{candidate}' was not found.",
                        "resource": candidate,
                        "did_you_mean": resolved.suggestions,
                    }
                ],
            )
            
        # 4. Bind validated context
        intent_data["target_resource"] = resolved.resource_id
        
        # 5. Conversation Context Processing
        ctx = self.conversation.process_turn(request.conversation_id, intent_data)
        ctx.current_resource_type = resolved.resource_type
        ctx.current_resource_confidence = resolved.confidence
        
        # 6. Add to Memory (Only if Valid!)
        self.memory.add_message(request.conversation_id, "user", request.message)
        
        # 7. Planning
        execution_plan = None
        if ctx.current_intent != "UNKNOWN":
            execution_plan = self.planner.create_plan(
                conversation_id=request.conversation_id,
                intent=ctx.current_intent,
                resource_id=ctx.current_resource,
                resource_type=ctx.current_resource_type
            )
            
        # 8. Tool Execution
        tool_results = []
        if execution_plan and execution_plan.status != PlanStatus.FAILED:
            tool_results = self.plan_executor.execute(execution_plan)
            
        # 8.5 Reasoning Engine
        reasoning_result = self.reasoning_engine.process(request.conversation_id, tool_results)

        # 8.7 Action Engine
        action_result = None
        if ctx.current_intent in ACTION_POLICIES:
            req_context = ActionContext(
                user_id="user123",
                provider_name="MOCK",
                execution_id=str(uuid.uuid4()),
                correlation_id=request.conversation_id,
                request_id=request_id
            )
            req = ActionRequest(
                action_name=ctx.current_intent,
                resource_id=ctx.current_resource,
                context=req_context
            )
            
            plan = self.action_planner.plan_action(req, reasoning_result)
            is_valid, _ = self.action_validator.validate(plan)
            if is_valid:
                self.action_state_machine.transition(plan, ActionStatus.VALIDATED)
                policy_ok, _ = self.policy_engine.check_policies(plan)
                if policy_ok:
                    dry_run = self.dry_run_engine.simulate(plan)
                    self.action_state_machine.transition(plan, ActionStatus.DRY_RUN_COMPLETE)
                    if self.approval_engine.requires_approval(plan):
                        app_req = self.approval_engine.request_approval(plan, dry_run.summary)
                        approval_res = self.approval_engine.process_approval(plan) # Auto-approves in test mode
                    else:
                        approval_res = None
                    
                    if plan.status in [ActionStatus.APPROVED, ActionStatus.DRY_RUN_COMPLETE]:
                        exec_result = self.action_executor.execute(plan)
                        rollback_plan = self.rollback_manager.prepare_rollback(plan)
                        self.execution_logger.log_execution(plan, exec_result)
                        self.audit_engine.record_audit(plan, approval_res, exec_result, rollback_plan)
                        
                        action_result = ActionResult(
                            status=plan.status,
                            action_completed=exec_result.provider_status == "SUCCESS",
                            rollback_created=rollback_plan.rollback_available,
                            audit_logged=True,
                            user_message=f"Action {req.action_name} executed.",
                            execution_result=exec_result,
                            dry_run=dry_run
                        )

        # 9. Context Building
        memory_summary = self.memory.summarize_memory(request.conversation_id)
        context_str = self.context_builder.build_structured_context(ctx, reasoning_result, action_result, memory_context=memory_summary)
        
        # 10. History formatting
        history_str = self.conversation.get_formatted_history(request.conversation_id, limit=5)
        
        # 11. Structured Logging (Phase 9/10)
        import time
        import logging
        logger = logging.getLogger("GraphAssistant")
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)
            
        used_tools = [tr.tool_name for tr in tool_results] if tool_results else []
        prompt_len = len(request.message)
        context_len = len(context_str)
        
        logger.info(f"Intent: {ctx.current_intent}")
        logger.info(f"Resource: {ctx.current_resource}")
        logger.info(f"Tool: {', '.join(used_tools) if used_tools else 'None'}")
        logger.info(f"Prompt: {prompt_len} chars")
        logger.info(f"Context: {context_len} chars")
        logger.info(f"Model: {settings.ollama_model}")
        
        gen_start_time = time.time()
        
        # 12. Response Generation
        chat_response = self.generator.generate(
            question=request.message,
            history_str=history_str,
            context_str=context_str,
            intent=ctx.current_intent,
            target=ctx.current_resource,
            reasoning_result=reasoning_result,
            action_result=action_result,
            request_id=request_id,
            stream=stream
        )
        
        gen_elapsed = time.time() - gen_start_time
        logger.info(f"Time: {gen_elapsed:.2f} sec")
        
        # 13. Save assistant response
        self.memory.add_message(request.conversation_id, "assistant", chat_response.answer)
        
        return chat_respons