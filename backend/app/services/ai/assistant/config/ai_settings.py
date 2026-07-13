import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AIConfiguration:
    """
    Single source of truth for all AI tuning parameters.
    Loaded from environment variables with sensible production defaults.
    Extends the basic AISettings in llm/config.py with full platform-level config.
    """
    # ── Ollama Connection ───────────────────────────────────────────────────
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://ollama:11434"))
    default_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3"))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("AI_TIMEOUT", "120")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("AI_MAX_RETRIES", "3")))

    # ── Inference Parameters ────────────────────────────────────────────────
    temperature: float = field(default_factory=lambda: float(os.getenv("AI_TEMPERATURE", "0.2")))
    top_p: float = field(default_factory=lambda: float(os.getenv("AI_TOP_P", "0.9")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("AI_MAX_TOKENS", "4096")))
    stream_enabled: bool = field(default_factory=lambda: os.getenv("AI_STREAM_ENABLED", "true").lower() == "true")

    # ── Model Routing Rules ─────────────────────────────────────────────────
    model_routing: Dict[str, str] = field(default_factory=lambda: {
        "terraform": "deepseek-coder",
        "kubernetes": "llama3",
        "security": "llama3",
        "finops": "qwen2",
        "architecture": "llama3",
        "default": "llama3"
    })

    # ── Safety ─────────────────────────────────────────────────────────────
    safety_enabled: bool = True
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r"delete.{0,40}production",
        r"rm\s+-rf",
        r"terminate.{0,30}all",
        r"drop.{0,30}database"
    ])

    # ── RAG ────────────────────────────────────────────────────────────────
    rag_retrieval_limit: int = field(default_factory=lambda: int(os.getenv("RAG_LIMIT", "8")))
    rag_min_score: float = field(default_factory=lambda: float(os.getenv("RAG_MIN_SCORE", "0.65")))
    rag_initial_retrieval: int = 20

    # ── Context Window ──────────────────────────────────────────────────────
    max_conversation_turns: int = 20
    context_compression_enabled: bool = True

    # ── Prompt Versioning ───────────────────────────────────────────────────
    active_prompt_version: str = field(default_factory=lambda: os.getenv("PROMPT_VERSION", "v1"))

    # ── Observability ───────────────────────────────────────────────────────
    metrics_enabled: bool = True
    citation_enabled: bool = True
    response_scoring_enabled: bool = True


# Singleton instance for import across the codebase
ai_config = AIConfiguration()