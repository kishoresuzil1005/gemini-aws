import re
from typing import Tuple

BLOCKED_PATTERNS = [
    r"delete.{0,40}production",
    r"drop.{0,30}database",
    r"rm\s+-rf",
    r"terminate.{0,30}all",
    r"format.{0,20}disk",
    r"revoke.{0,30}all.{0,20}iam",
]

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",          # AWS Access Key ID
    r"(?i)(password|secret|token|api_key)\s*[:=]\s*\S+",
]

class PromptGuard:
    """
    Scans user input for dangerous or policy-violating instructions
    before they reach the LLM.
    """
    def validate(self, user_input: str) -> Tuple[bool, str]:
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False, f"Request blocked by safety policy. Matched rule: '{pattern}'"
        return True, ""

class OutputFilter:
    """
    Scans LLM responses for accidental secrets or dangerous commands before sending to frontend.
    """
    def sanitize(self, response: str) -> str:
        for pattern in SECRET_PATTERNS:
            response = re.sub(pattern, "[REDACTED]", response, flags=re.IGNORECASE)
        return respons