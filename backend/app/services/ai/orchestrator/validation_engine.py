from app.services.ai.orchestrator.orchestration_models import ValidationPlan

class ValidationEngine:
    def generate_validation(self, resource_type: str, resource_id: str) -> ValidationPlan:
        if resource_type == "EC2":
            return ValidationPlan(
                check_type="StatusCheck",
                command=f"aws ec2 describe-instances --instance-ids {resource_id} --query 'Reservations[*].Instances[*].State.Name'",
                expected_result="running"
            )
        elif resource_type == "RDS":
            return ValidationPlan(
                check_type="StatusCheck",
                command=f"aws rds describe-db-instances --db-instance-identifier {resource_id} --query 'DBInstances[*].DBInstanceStatus'",
                expected_result="available"
            )
        elif resource_type == "Lambda":
            return ValidationPlan(
                check_type="InvocationCheck",
                command=f"aws lambda invoke --function-name {resource_id} --dry-run response.json",
                expected_result="StatusCode: 204"
            )
        elif resource_type == "IAM":
            return ValidationPlan(
                check_type="PolicyCheck",
                command=f"aws iam list-attached-role-policies --role-name {resource_id}",
                expected_result="LeastPrivilege policy present"
            )
        elif resource_type == "ALB":
            return ValidationPlan(
                check_type="HealthCheck",
                command=f"aws elbv2 describe-target-health --target-group-arn <tg-arn>",
                expected_result="healthy"
            )
            
        return ValidationPlan(
            check_type="GenericCheck",
            command="echo 'Verify resource state in AWS Console'",
            expected_result="Healthy/Available"
        