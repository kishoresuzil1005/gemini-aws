class AWSColorPalette:
    """
    AWS Architecture Center color palette.

    Provides category-based colors for
    AWS services.

    https://aws.amazon.com/architecture/icons/
    """

    COLORS = {

        #
        # Compute
        #

        "EC2": "#FF9900",
        "Lambda": "#FF9900",
        "ECS": "#FF9900",
        "EKS": "#FF9900",
        "AutoScaling": "#FF9900",

        #
        # Networking
        #

        "VPC": "#205493",
        "Subnet": "#205493",
        "InternetGateway": "#205493",
        "NATGateway": "#205493",
        "RouteTable": "#205493",
        "SecurityGroup": "#205493",
        "LoadBalancer": "#205493",
        "ALB": "#205493",

        #
        # Storage
        #

        "S3": "#3F8624",
        "EBS": "#3F8624",
        "EFS": "#3F8624",

        #
        # Database
        #

        "RDS": "#7B61FF",
        "DynamoDB": "#7B61FF",
        "Aurora": "#7B61FF",
        "Redshift": "#7B61FF",

        #
        # Security
        #

        "IAM": "#DD344C",
        "KMS": "#DD344C",
        "SecretsManager": "#DD344C",
        "GuardDuty": "#DD344C",

        #
        # Monitoring
        #

        "CloudWatch": "#1F73B7",
        "CloudTrail": "#1F73B7",
        "SNS": "#1F73B7",
        "SQS": "#1F73B7",

        #
        # Analytics
        #

        "Athena": "#8C4FFF",
        "Glue": "#8C4FFF",
        "EMR": "#8C4FFF",

        #
        # Integration
        #

        "StepFunctions": "#C925D1",
        "EventBridge": "#C925D1",

        #
        # Default
        #

        "Unknown": "#90A4AE"

    }

    @classmethod
    def get_fill(cls, resource_type: str) -> str:
        """
        Return the AWS fill color
        for a resource.
        """
        
        # Simple case-insensitive lookup
        if not resource_type:
            return cls.COLORS["Unknown"]
            
        # Try direct match
        if resource_type in cls.COLORS:
            return cls.COLORS[resource_type]
            
        # Try case-insensitive match
        for key, val in cls.COLORS.items():
            if key.lower() == resource_type.lower():
                return val

        return cls.COLORS["Unknown"]

    @classmethod
    def get_border(cls, resource_type: str) -> str:
        """
        Border color.

        Currently identical to fill,
        but separated for future themes.
        """

        return cls.get_fill(resource_type)

    @classmethod
    def supported_services(cls):

        return sorted(cls.COLORS.keys())