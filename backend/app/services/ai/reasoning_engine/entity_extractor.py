"""
Entity Extractor — Phase 1
============================
Tokenises and normalises the user's raw question, detecting:
  - Explicit resource IDs / ARNs
  - Service hints (ec2, rds, s3, lambda, …)
  - Environment hints (prod, staging, dev, …)
  - Owner / team hints
  - Tag filters  (tag:Env=prod)
  - AWS region hints
"""

from __future__ import annotations

import re
from typing import Dict, List

from app.services.ai.orchestrator.models import CandidateQuery

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

_ARN_RE = re.compile(r"\barn:aws:[a-z0-9\-]+:[a-z0-9\-]*:\d*:[^\s,;\"']+\b", re.IGNORECASE)
_RES_ID_RE = re.compile(
    r"\b(?:i|vpc|subnet|sg|vol|eni|igw|nat|rtb|ami|snap|tgw|acl|eip|lb|arn)-[a-z0-9]{4,}\b",
    re.IGNORECASE,
)
_TAG_RE = re.compile(r"tag:([A-Za-z0-9_\-]+)=([A-Za-z0-9_\-]+)")
_REGION_RE = re.compile(
    r"\b(us-east-[12]|us-west-[12]|eu-west-[123]|eu-central-1|ap-southeast-[12]|"
    r"ap-northeast-[123]|ap-south-1|sa-east-1|ca-central-1)\b",
    re.IGNORECASE,
)

_SERVICES = [
    "ec2", "rds", "s3", "lambda", "ecs", "eks", "elasticache", "dynamodb",
    "sqs", "sns", "cloudfront", "route53", "elb", "alb", "nlb", "vpc",
    "iam", "kms", "secretsmanager", "ssm", "cloudwatch", "guardduty",
    "inspector", "waf", "shield", "config", "cloudtrail", "glue", "emr",
    "redshift", "athena", "kinesis", "firehose", "eventbridge", "step functions",
    "api gateway", "appsync", "cognito", "amplify", "codestar",
]

_ENVIRONMENTS = ["prod", "production", "staging", "stage", "dev", "development",
                 "test", "qa", "uat", "sandbox", "preprod", "pre-prod"]

_STOP_WORDS = frozenset(
    "why is are my our the a an unhealthy failing broken what how who where "
    "down issue problem error not working when did status show list tell me about "
    "explain describe check analyze analyse inspect review audit".split()
)


class EntityExtractor:
    """
    @deprecated
    Legacy Compatibility Wrapper
    Extracts entities (like AWS resource IDs, types, and keywords) 
    from a natural language query.
    All methods are pure functions — no I/O, no LLM calls.
    """

    def extract(self, raw_input: str) -> CandidateQuery:
        """Main entry point. Returns a CandidateQuery."""
        lower = raw_input.lower()

        # 1. Resource IDs and ARNs
        arns = _ARN_RE.findall(raw_input)
        ids = _RES_ID_RE.findall(raw_input)
        resource_ids: List[str] = list(dict.fromkeys(arns + ids))  # deduplicated, order kept

        # 2. Service hints
        service_hints = [s for s in _SERVICES if re.search(r"\b" + re.escape(s) + r"\b", lower)]

        # 3. Environment hints
        env_hints = [e for e in _ENVIRONMENTS if re.search(r"\b" + re.escape(e) + r"\b", lower)]

        # 4. Tag filters
        tag_filters: Dict[str, str] = {}
        for m in _TAG_RE.finditer(raw_input):
            tag_filters[m.group(1)] = m.group(2)

        # 5. Region hints
        regions = list({m.group(0).lower() for m in _REGION_RE.finditer(raw_input)})

        # 6. Meaningful tokens (clean words, no stop words)
        words = re.findall(r"[a-zA-Z0-9][-a-zA-Z0-9_]*", lower)
        tokens = [w for w in words if w not in _STOP_WORDS and len(w) > 2]

        # 7. Owner hints (words ending in -team, words before "team", emails)
        owner_hints: List[str] = []
        for m in re.finditer(r"(\w+[\-_]?team|\w+@\w+\.\w+)", lower):
            owner_hints.append(m.group(0))
        # Extend env hints with region
        env_hints = list(dict.fromkeys(env_hints + regions))

        return CandidateQuery(
            raw_input=raw_input,
            tokens=list(dict.fromkeys(tokens)),
            resource_ids=resource_ids,
            service_hints=list(dict.fromkeys(service_hints)),
            environment_hints=env_hints,
            owner_hints=owner_hints,
            tag_filters=tag_filters,
        )
