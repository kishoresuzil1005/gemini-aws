from app.services.diagram.graph_parser import GraphParser


class LayerBuilder:

    LAYER_MAP = {

        #
        # Internet
        #

        "InternetGateway": "Internet",
        "Route53": "Internet",
        "CloudFront": "Internet",
        "WAF": "Internet",

        #
        # Networking
        #

        "VPC": "Networking",
        "Subnet": "Networking",
        "SecurityGroup": "Networking",
        "NATGateway": "Networking",
        "ALB": "Networking",
        "NLB": "Networking",

        #
        # Compute
        #

        "EC2": "Compute",
        "Lambda": "Compute",
        "ECS": "Compute",
        "EKS": "Compute",
        "AutoScaling": "Compute",

        #
        # Database
        #

        "RDS": "Database",
        "DynamoDB": "Database",
        "Redshift": "Database",
        "ElastiCache": "Database",

        #
        # Storage
        #

        "S3": "Storage",
        "EBS": "Storage",
        "EFS": "Storage",

        #
        # Monitoring
        #

        "CloudWatch": "Monitoring",
        "CloudTrail": "Monitoring",
        "SNS": "Monitoring",
        "EventBridge": "Monitoring",

        #
        # Security
        #

        "IAM": "Security",
        "KMS": "Security",
        "SecretsManager": "Security",
        "GuardDuty": "Security",
        "SecurityHub": "Security",
        "Inspector": "Security"
    }

    def __init__(self):

        self.graph = GraphParser()

    def build(self):

        graph = self.graph.parse()

        layers = {

            "Internet": [],
            "Networking": [],
            "Compute": [],
            "Database": [],
            "Storage": [],
            "Monitoring": [],
            "Security": [],
            "Other": []

        }

        for node in graph["nodes"]:

            layer = self.LAYER_MAP.get(

                node["type"],

                "Other"

            )

            layers[layer].append(node)

        return {

            "layers": layers,

            "edges": graph["edges"]

        }
