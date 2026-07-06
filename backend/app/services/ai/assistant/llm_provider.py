from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        pass

class MockLLMProvider(LLMProvider):
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        # A simple mock that looks for keywords in the prompt to simulate reasoning
        if "hello-api" in prompt and "insecure" in prompt:
            return (
                "The Lambda function `hello-api` is insecure because it is exposed through an API Gateway "
                "and it has two primary issues:\n\n"
                "1. **IAM Role is over-privileged**: It uses a role that grants excessive permissions.\n"
                "2. **Lambda is not inside a VPC**: It lacks network isolation.\n\n"
                "**Priority**: MEDIUM\n"
                "**Blast Radius**: LOW\n\n"
                "**Suggested Remediation**:\n"
                "- Apply Least Privilege to the IAM Role.\n"
                "- Attach the Lambda to a VPC."
            )
        elif "Automate" in prompt or "safely" in prompt:
            return (
                "Yes, this can be automated safely. The orchestration engine has generated an execution package "
                "requiring approval from the **DevOps Team**. The safe execution order is to first attach the VPC, "
                "then update the IAM policy. Rollback plans are prepared."
            )
        elif "Terraform" in prompt:
            return (
                "Here is the Terraform generated for the remediation:\n"
                "```hcl\n"
                "resource \"aws_iam_role_policy\" \"least_privilege\" {\n"
                "  name   = \"least-privilege-policy\"\n"
                "  role   = \"hello-api\"\n"
                "  ...\n"
                "}\n"
                "```"
            )
        else:
            return "I am your AI Cloud Operations Engineer. I can analyze security, calculate blast radius, and execute orchestrations."
