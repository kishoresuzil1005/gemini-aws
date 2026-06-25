class LayerBuilder:

    LAYER_MAP = {

        "InternetGateway": "Internet",
        "Route53": "Internet",
        "CloudFront": "Internet",
        "WAF": "Internet",

        "VPC": "Networking",
        "Subnet": "Networking",
        "SecurityGroup": "Networking",
        "NATGateway": "Networking",
        "ALB": "Networking",
        "NLB": "Networking",

        "EC2": "Compute",
        "Lambda": "Compute",
        "ECS": "Compute",
        "EKS": "Compute",
        "AutoScaling": "Compute",

        "RDS": "Database",
        "DynamoDB": "Database",
        "Redshift": "Database",
        "ElastiCache": "Database",

        "S3": "Storage",
        "EBS": "Storage",
        "EFS": "Storage",

        "CloudWatch": "Monitoring",
        "CloudTrail": "Monitoring",
        "SNS": "Monitoring",
        "EventBridge": "Monitoring",

        "IAM": "Security",
        "KMS": "Security",
        "GuardDuty": "Security",
        "SecurityHub": "Security",
        "Inspector": "Security",
        "SecretsManager": "Security"
    }

    def get_layer(self, resource_type):

        return self.LAYER_MAP.get(

            resource_type,

            "Other"

        )
