from typing import List
from app.services.ai.remediation_models import RemediationPlan
from app.services.ai.recommendation_engine import Recommendation, AIRecommendationEngine
from app.services.ai.terraform_generator import TerraformGenerator
from app.services.ai.awscli_generator import AWSCLIGenerator
from app.services.ai.cloudformation_generator import CloudFormationGenerator
from app.services.ai.playbook_generator import PlaybookGenerator

class RemediationPlanner:
    def __init__(self):
        self.tf_gen = TerraformGenerator()
        self.cli_gen = AWSCLIGenerator()
        self.cfn_gen = CloudFormationGenerator()
        self.play_gen = PlaybookGenerator()

    def _determine_template_names(self, issue_title: str) -> dict:
        """
        Maps a recommendation's issue title to the underlying deterministic templates.
        """
        if "Public Exposure on EC2" in issue_title:
            return {
                "tf": "move_ec2_private.tf",
                "cli": "move_ec2_private.txt",
                "cfn": "move_ec2_private.yaml",
                "play": "public_ec2.md"
            }
        elif "Public Exposure on RDS" in issue_title:
            return {
                "tf": "private_rds.tf",
                "cli": "private_rds.txt",
                "cfn": "private_rds.yaml",
                "play": "public_rds.md"
            }
        elif "Open Port" in issue_title or "SSH" in issue_title:
            return {
                "tf": "restrict_ssh.tf",
                "cli": "restrict_ssh.txt",
                "cfn": "restrict_ssh.yaml",
                "play": "open_ssh.md"
            }
        elif "WAF Missing" in issue_title or "WAF" in issue_title:
            return {
                "tf": "attach_waf.tf",
                "cli": "attach_waf.txt",
                "cfn": "attach_waf.yaml",
                "play": "waf_missing.md"
            }
        elif "Missing VPC Attachment" in issue_title:
            return {
                "tf": "attach_lambda_vpc.tf",
                "cli": "attach_lambda_vpc.txt",
                "cfn": "attach_lambda_vpc.yaml",
                "play": "vpc_missing.md"
            }
        elif "Over-privileged IAM" in issue_title:
            return {
                "tf": "least_privilege_iam.tf",
                "cli": "least_privilege_iam.txt",
                "cfn": "least_privilege_iam.yaml",
                "play": "least_privilege_iam.md"
            }
            
        # Default mapping if none found
        return {"tf": "", "cli": "", "cfn": "", "play": ""}

    def create_plan(self, recommendation: Recommendation) -> RemediationPlan:
        templates = self._determine_template_names(recommendation.issue_title)
        
        return RemediationPlan(
            recommendation_id=f"rec-{recommendation.resource_id}-{hash(recommendation.issue_title)}",
            resource_id=recommendation.resource_id,
            issue=recommendation.issue_title,
            priority=recommendation.priority,
            terraform=self.tf_gen.generate(templates["tf"], recommendation.resource_id) if templates["tf"] else "",
            aws_cli=self.cli_gen.generate(templates["cli"], recommendation.resource_id) if templates["cli"] else "",
            cloudformation=self.cfn_gen.generate(templates["cfn"], recommendation.resource_id) if templates["cfn"] else "",
            manual_steps=self.play_gen.generate(templates["play"], recommendation.resource_id) if templates["play"] else "No manual playbook available.",
            rollback="Revert changes via previous infrastructure state.",
            estimated_time="15 minutes",
            downtime="Possible downtime depending on resource type and changes.",
            risk=recommendation.priority
        )

    def plan_for_resource(self, resource_id: str) -> List[RemediationPlan]:
        engine = AIRecommendationEngine()
        recs = engine.analyze_resource(resource_id)
        
        plans = []
        for rec in recs:
            if rec.priority not in ["INFO", "GOOD"]:
                plans.append(self.create_plan(rec))
        return plans

    def plan_environment(self) -> List[RemediationPlan]:
        engine = AIRecommendationEngine()
        recs = engine.analyze_environment()
        
        plans = []
        for rec in recs:
            if rec.priority not in ["INFO", "GOOD"]:
                plans.append(self.create_plan(rec))
        return plans
