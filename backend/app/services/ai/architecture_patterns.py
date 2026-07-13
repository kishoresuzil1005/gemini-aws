from typing import Dict, Any, Optional

class ArchitecturePatterns:
    def __init__(self):
        self.patterns = {
            "web_application": {
                "name": "Production Three-Tier Web Application",
                "description": "A highly available, secure, and scalable web application architecture across multiple availability zones.",
                "flow": [
                    "Users",
                    "Route53",
                    "CloudFront",
                    "AWS WAF",
                    "Application Load Balancer",
                    "Auto Scaling Group",
                    "Private EC2",
                    "RDS Multi-AZ",
                    "S3",
                    "CloudWatch",
                    "SNS"
                ],
                "services": ["Route53", "CloudFront", "AWS WAF", "ALB", "EC2", "Auto Scaling", "RDS", "S3", "CloudWatch", "SNS", "IAM", "VPC", "Subnets"],
                "high_availability": ["Multi AZ", "Auto Scaling", "Health Checks", "ALB", "Route53 Failover"],
                "security": ["IAM", "Security Groups", "KMS", "WAF", "CloudTrail", "GuardDuty", "Secrets Manager"],
                "monitoring": ["CloudWatch", "CloudTrail", "SNS", "X-Ray"],
                "cost": ["Savings Plans", "Auto Scaling", "Lifecycle Policies", "S3 Intelligent Tiering"],
                "best_practices": [
                    "Deploy stateless EC2 instances in an Auto Scaling Group.",
                    "Keep databases in private subnets with strict Security Groups.",
                    "Use WAF on CloudFront to block malicious traffic at the edge.",
                    "Use IAM roles for EC2 instead of access keys."
                ]
            },
            "serverless": {
                "name": "Serverless API Architecture",
                "description": "A fully managed, auto-scaling, pay-as-you-go serverless architecture.",
                "flow": [
                    "Users",
                    "Route53",
                    "CloudFront",
                    "API Gateway",
                    "Lambda",
                    "DynamoDB",
                    "S3",
                    "CloudWatch",
                    "SNS"
                ],
                "services": ["API Gateway", "Lambda", "DynamoDB", "S3", "CloudWatch", "SNS", "IAM", "KMS"],
                "high_availability": ["Multi-region deployment (optional)", "Global DynamoDB Tables", "Regional API Gateway"],
                "security": ["API Gateway WAF", "Cognito/IAM Auth", "Lambda Execution Roles", "KMS Encryption"],
                "monitoring": ["CloudWatch Metrics", "X-Ray Tracing", "CloudWatch Logs"],
                "cost": ["Pay per invocation", "Provisioned concurrency tuning", "DynamoDB On-Demand"],
                "best_practices": [
                    "Keep Lambda functions small and single-purpose.",
                    "Reuse database connections outside the Lambda handler.",
                    "Use API Gateway caching to reduce Lambda invocations."
                ]
            },
            "kubernetes": {
                "name": "Highly Available Kubernetes Platform",
                "description": "An enterprise-grade container orchestration platform using Amazon EKS.",
                "flow": [
                    "Users",
                    "Route53",
                    "ALB",
                    "Amazon EKS",
                    "Pods",
                    "Services",
                    "RDS",
                    "EFS",
                    "CloudWatch"
                ],
                "services": ["Route53", "ALB", "EKS", "Node Groups", "Pods", "Services", "Ingress", "EFS", "RDS", "CloudWatch", "IAM"],
                "high_availability": ["EKS Multi-AZ Control Plane", "Managed Node Groups across AZs", "Cluster Autoscaler", "HPA"],
                "security": ["IRSA (IAM Roles for Service Accounts)", "Network Policies", "Security Groups for Pods", "Private Endpoint"],
                "monitoring": ["Prometheus/Grafana", "CloudWatch Container Insights", "EKS Control Plane Logging"],
                "cost": ["Spot Instances for stateless workloads", "Karpenter for efficient bin-packing", "Graviton Processors"],
                "best_practices": [
                    "Use IAM Roles for Service Accounts (IRSA) for least-privilege.",
                    "Implement resource requests and limits for all Pods.",
                    "Deploy worker nodes in private subnets only."
                ]
            },
            "microservices": {
                "name": "ECS Microservices Architecture",
                "description": "Containerized microservices running on AWS Fargate/ECS.",
                "flow": [
                    "Users",
                    "Route53",
                    "CloudFront",
                    "ALB",
                    "ECS",
                    "Service Discovery",
                    "Redis",
                    "RDS",
                    "SQS",
                    "SNS"
                ],
                "services": ["Route53", "CloudFront", "ALB", "ECS", "Fargate", "ElastiCache", "RDS", "SQS", "SNS", "CloudWatch", "IAM"],
                "high_availability": ["Fargate Multi-AZ", "Target Tracking Scaling", "Service Discovery"],
                "security": ["Task Execution Roles", "VPC Endpoints", "Security Groups"],
                "monitoring": ["CloudWatch Container Insights", "X-Ray"],
                "cost": ["Fargate Spot", "Right-sizing tasks"],
                "best_practices": ["Decouple services using SQS.", "Store secrets in AWS Secrets Manager."]
            },
            "data_platform": {
                "name": "Serverless Data Lake Platform",
                "description": "A scalable and cost-effective data ingestion and analytics platform.",
                "flow": [
                    "Data Sources",
                    "S3",
                    "Glue",
                    "Athena",
                    "Redshift",
                    "QuickSight"
                ],
                "services": ["S3", "AWS Glue", "Amazon Athena", "Redshift", "QuickSight", "Lake Formation", "IAM"],
                "high_availability": ["S3 Durability", "Serverless Glue/Athena"],
                "security": ["S3 SSE-KMS", "Lake Formation access control", "VPC Endpoints"],
                "monitoring": ["CloudWatch", "AWS CloudTrail"],
                "cost": ["S3 Intelligent Tiering", "Partitioning data in S3", "Redshift Serverless"],
                "best_practices": ["Use Parquet/ORC formats for Athena queries.", "Implement strict Lake Formation controls."]
            },
            "cloudops": {
                "name": "CloudOps AI Platform",
                "description": "Intelligent Cloud Operations dashboard and AI backend.",
                "flow": [
                    "Users",
                    "Frontend",
                    "API Gateway",
                    "FastAPI",
                    "Discovery Engine",
                    "Neo4j",
                    "PostgreSQL",
                    "Qdrant",
                    "Ollama",
                    "AWS APIs",
                    "CloudWatch",
                    "Cost Explorer",
                    "Security Hub"
                ],
                "services": ["API Gateway", "FastAPI", "Neo4j", "PostgreSQL", "Qdrant", "Redis", "Celery", "Ollama", "AWS Discovery", "CloudWatch", "Cost Explorer", "IAM"],
                "high_availability": ["ECS Fargate for API", "Managed PostgreSQL Multi-AZ"],
                "security": ["Cognito Auth", "Strict IAM for Discovery Engine", "VPC isolation"],
                "monitoring": ["Datadog / CloudWatch"],
                "cost": ["Spot instances for Celery workers", "Optimize local LLM hosting"],
                "best_practices": ["Cache graph queries in Redis.", "Ensure discovery IAM roles are read-only."]
            }
        }

    def get_pattern(self, workload: str) -> Optional[Dict[str, Any]]:
        # Map detected workloads to pattern keys if there are discrepancies
        # For our implementation, workload strings mostly match exactly.
        key = workload
        if key not in self.patterns:
            key = "web_application" # Default fallback
            
        return self.patterns.get(key)
        
    def get_all_patterns(self) -> Dict[str, Any]:
        return self.pattern