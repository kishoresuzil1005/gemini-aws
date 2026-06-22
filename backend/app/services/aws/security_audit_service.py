import boto3


class SecurityAuditService:

    RISKY_PORTS = {
        22: ("SSH", "HIGH"),
        23: ("Telnet", "CRITICAL"),
        3389: ("RDP", "CRITICAL"),

        3306: ("MySQL", "CRITICAL"),
        5432: ("PostgreSQL", "CRITICAL"),
        1433: ("SQL Server", "CRITICAL"),
        1521: ("Oracle", "CRITICAL"),

        6379: ("Redis", "CRITICAL"),
        11211: ("Memcached", "HIGH"),

        27017: ("MongoDB", "CRITICAL"),

        9200: ("OpenSearch", "HIGH"),
        9300: ("OpenSearch Cluster", "HIGH"),

        6443: ("Kubernetes API", "CRITICAL"),

        2375: ("Docker API", "CRITICAL"),
        2376: ("Docker TLS", "HIGH"),

        9090: ("Prometheus", "MEDIUM"),
        3000: ("Grafana", "MEDIUM"),

        8081: ("Jenkins", "HIGH"),
        9000: ("SonarQube", "MEDIUM")
    }

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        return [
            r["RegionName"]
            for r in ec2.describe_regions()["Regions"]
        ]

    @classmethod
    def find_risky_security_groups(cls):

        findings = []

        for region in cls.get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                groups = (
                    ec2.describe_security_groups()
                    ["SecurityGroups"]
                )

                for sg in groups:

                    for rule in sg.get(
                        "IpPermissions",
                        []
                    ):

                        from_port = rule.get(
                            "FromPort"
                        )

                        to_port = rule.get(
                            "ToPort"
                        )

                        if from_port is None:
                            # Protocols like -1 (all) don't have port bounds in same way
                            # but we can look for specific risky port bounds
                            continue

                        for ip in rule.get(
                            "IpRanges",
                            []
                        ):

                            cidr = ip.get(
                                "CidrIp"
                            )

                            if cidr != "0.0.0.0/0":
                                continue

                            # Check if the port or range exposes any of our RISKY_PORTS
                            for r_port, (service_name, severity) in cls.RISKY_PORTS.items():
                                # Check if r_port is within [from_port, to_port] (inclusive)
                                # inside rule if to_port is provided, otherwise just equals from_port
                                limit_to = to_port if to_port is not None else from_port
                                if from_port <= r_port <= limit_to:
                                    findings.append({
                                        "region": region,
                                        "group_id": sg["GroupId"],
                                        "group_name": sg["GroupName"],
                                        "risk": service_name,
                                        "severity": severity,
                                        "port": r_port,
                                        "source": cidr
                                    })

            except Exception:
                continue

        return findings
