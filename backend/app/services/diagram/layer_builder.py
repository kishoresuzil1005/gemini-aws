class LayerBuilder:
    """
    Maps AWS resource types to logical architecture layers.
    """

    LAYER_MAP = {

        # ----------------------------
        # Internet
        # ----------------------------

        "InternetGateway": "Internet",
        "Route53": "Internet",
        "CloudFront": "Internet",
        "WAF": "Internet",

        # ----------------------------
        # Networking
        # ----------------------------

        "VPC": "Networking",
        "Subnet": "Networking",
        "SecurityGroup": "Networking",
        "NATGateway": "Networking",
        "ALB": "Networking",
        "NLB": "Networking",

        # ----------------------------
        # Compute
        # ----------------------------

        "EC2": "Compute",
        "Lambda": "Compute",
        "ECS": "Compute",
        "EKS": "Compute",
        "AutoScaling": "Compute",

        # ----------------------------
        # Database
        # ----------------------------

        "RDS": "Database",
        "DynamoDB": "Database",
        "Redshift": "Database",
        "ElastiCache": "Database",

        # ----------------------------
        # Storage
        # ----------------------------

        "S3": "Storage",
        "EBS": "Storage",
        "EFS": "Storage",

        # ----------------------------
        # Monitoring
        # ----------------------------

        "CloudWatch": "Monitoring",
        "CloudTrail": "Monitoring",
        "SNS": "Monitoring",
        "EventBridge": "Monitoring",

        # ----------------------------
        # Security
        # ----------------------------

        "IAM": "Security",
        "KMS": "Security",
        "GuardDuty": "Security",
        "Inspector": "Security",
        "SecurityHub": "Security",
        "SecretsManager": "Security"
    }

    def get_layer(self, resource_type: str) -> str:
        """
        Return the logical architecture layer
        for a given AWS resource type.
        """
        return self.LAYER_MAP.get(resource_type, "Other"