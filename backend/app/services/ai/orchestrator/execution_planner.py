from typing import List
from app.services.ai.remediation_models import RemediationPlan
from app.services.ai.orchestrator.orchestration_models import ExecutionStep

class ExecutionPlanner:
    def plan(self, plan: RemediationPlan) -> List[ExecutionStep]:
        steps = []
        issue = plan.issue
        
        if "Public Exposure on EC2" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Identify Target VPC", action="Read",
                    command="aws ec2 describe-vpcs", estimated_time="1m", rollback="N/A"
                ),
                ExecutionStep(
                    id="step-2", title="Create Private Subnet", action="Create",
                    command="aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24", estimated_time="2m", rollback="aws ec2 delete-subnet"
                ),
                ExecutionStep(
                    id="step-3", title="Create AMI Snapshot", action="Backup",
                    command=f"aws ec2 create-image --instance-id {plan.resource_id} --name 'Private-Migration'", estimated_time="10m", rollback="aws ec2 deregister-image"
                ),
                ExecutionStep(
                    id="step-4", title="Launch New Instance", action="Create",
                    command="aws ec2 run-instances --image-id <ami-id> --subnet-id <new-subnet-id>", estimated_time="3m", rollback="aws ec2 terminate-instances"
                ),
                ExecutionStep(
                    id="step-5", title="Terminate Old Instance", action="Delete",
                    command=f"aws ec2 terminate-instances --instance-ids {plan.resource_id}", estimated_time="1m", rollback="Restore from AMI"
                )
            ]
        elif "Public Exposure on RDS" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Modify RDS Instance", action="Update",
                    command=f"aws rds modify-db-instance --db-instance-identifier {plan.resource_id} --no-publicly-accessible --apply-immediately",
                    estimated_time="5m", rollback="aws rds modify-db-instance --publicly-accessible"
                )
            ]
        elif "Over-privileged IAM" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Audit CloudTrail", action="Read",
                    command=f"aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue={plan.resource_id}",
                    estimated_time="5m", rollback="N/A"
                ),
                ExecutionStep(
                    id="step-2", title="Attach Least Privilege Policy", action="Update",
                    command=f"aws iam put-role-policy --role-name {plan.resource_id} --policy-name LeastPrivilege --policy-document file://policy.json",
                    estimated_time="1m", rollback="aws iam delete-role-policy"
                )
            ]
        elif "Open Port" in issue or "SSH" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Revoke Open SSH", action="Update",
                    command=f"aws ec2 revoke-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr 0.0.0.0/0",
                    estimated_time="1m", rollback="aws ec2 authorize-security-group-ingress"
                ),
                ExecutionStep(
                    id="step-2", title="Allow VPN SSH", action="Update",
                    command=f"aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr <vpn-cidr>",
                    estimated_time="1m", rollback="aws ec2 revoke-security-group-ingress"
                )
            ]
        elif "WAF Missing" in issue or "WAF" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Create Web ACL", action="Create",
                    command="aws wafv2 create-web-acl --name <name> --scope REGIONAL --default-action Allow={}",
                    estimated_time="2m", rollback="aws wafv2 delete-web-acl"
                ),
                ExecutionStep(
                    id="step-2", title="Associate WAF", action="Update",
                    command=f"aws wafv2 associate-web-acl --web-acl-arn <arn> --resource-arn <alb-arn>",
                    estimated_time="1m", rollback="aws wafv2 disassociate-web-acl"
                )
            ]
        elif "Missing VPC Attachment" in issue:
            steps = [
                ExecutionStep(
                    id="step-1", title="Update Lambda VPC Config", action="Update",
                    command=f"aws lambda update-function-configuration --function-name {plan.resource_id} --vpc-config SubnetIds=<subnet>,SecurityGroupIds=<sg>",
                    estimated_time="2m", rollback="aws lambda update-function-configuration --vpc-config SubnetIds=[],SecurityGroupIds=[]"
                )
            ]
        else:
            steps = [
                ExecutionStep(
                    id="step-1", title="Apply Generic Fix", action="Update",
                    command="Apply template", estimated_time="5m", rollback="Revert"
                )
            ]
            
        return steps
