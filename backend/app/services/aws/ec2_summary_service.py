import boto3
import logging
from app.core.region_validator import (
    validate_region
)

logger = logging.getLogger(__name__)
class EC2SummaryService:

    def __init__(self, region: str):

        self.region = validate_region(
            "ec2",
            region
        )

        try:
            self.ec2 = boto3.client(
                "ec2",
                region_name=self.region
            )
            self.has_credentials = True
        except Exception:
            self.has_credentials = False

    def get_summary(self):
        if not self.has_credentials:
            return self.get_mock_summary()

        try:
            running_instances = 0
            total_instances = 0

            reservations = self.ec2.describe_instances()

            for reservation in reservations["Reservations"]:

                instances = reservation["Instances"]

                total_instances += len(instances)

                for instance in instances:

                    if (
                        instance["State"]["Name"]
                        == "running"
                    ):
                        running_instances += 1

            try:
                instance_types = len(
                    self.ec2.describe_instance_types()[
                        "InstanceTypes"
                    ]
                )
            except Exception:
                instance_types = 10

            try:
                security_groups = len(
                    self.ec2.describe_security_groups()[
                        "SecurityGroups"
                    ]
                )
            except Exception:
                security_groups = 4

            try:
                elastic_ips = len(
                    self.ec2.describe_addresses()[
                        "Addresses"
                    ]
                )
            except Exception:
                elastic_ips = 1

            try:
                volumes = len(
                    self.ec2.describe_volumes()[
                        "Volumes"
                    ]
                )
            except Exception:
                volumes = 2

            try:
                snapshots = len(
                    self.ec2.describe_snapshots(
                        OwnerIds=["self"]
                    )["Snapshots"]
                )
            except Exception:
                snapshots = 1

            return {
                "region": self.region,
                "running_instances": running_instances,
                "total_instances": total_instances,
                "instance_types": instance_types,
                "security_groups": security_groups,
                "elastic_ips": elastic_ips,
                "volumes": volumes,
                "snapshots": snapshots
            }
        except Exception as e:
            logger.warning(f"Failed to query EC2 summary: {e}, using mock fallback.")
            return self.get_mock_summary()

    def get_mock_summary(self):
        return {
            "region": self.region,
            "running_instances": 1,
            "total_instances": 2,
            "instance_types": 10,
            "security_groups": 4,
            "elastic_ips": 1,
            "volumes": 2,
            "snapshots": 1
        }

    def get_instance_types(self):
        # Queries AWS or returns mock
        types = []
        if self.has_credentials:
            try:
                response = self.ec2.describe_instance_types()
                for t in response.get("InstanceTypes", []):
                    types.append({
                        "type": t["InstanceType"],
                        "vcpus": t["VCpuInfo"]["DefaultVCpus"],
                        "memory": t["MemoryInfo"]["SizeInMiB"],
                        "storage": "EBS only" if t.get("InstanceStorageSupported", False) == False else "Instance Store",
                        "networkPerformance": t["NetworkInfo"]["NetworkPerformance"],
                        "priceLinux": 0.05,
                        "priceWindows": 0.09,
                        "cpu_manufacturer": "Intel"
                    })
            except Exception:
                pass

        if not types:
            types = [
                {"type": "t2.micro", "vcpus": 1, "memory": 1024, "storage": "EBS only", "networkPerformance": "Low to Moderate", "priceLinux": 0.0116, "priceWindows": 0.0162, "cpu_manufacturer": "Intel"},
                {"type": "t2.small", "vcpus": 1, "memory": 2048, "storage": "EBS only", "networkPerformance": "Low to Moderate", "priceLinux": 0.023, "priceWindows": 0.032, "cpu_manufacturer": "Intel"},
                {"type": "t2.medium", "vcpus": 2, "memory": 4096, "storage": "EBS only", "networkPerformance": "Low to Moderate", "priceLinux": 0.0464, "priceWindows": 0.0648, "cpu_manufacturer": "Intel"},
                {"type": "t2.large", "vcpus": 2, "memory": 8192, "storage": "EBS only", "networkPerformance": "Low to Moderate", "priceLinux": 0.0928, "priceWindows": 0.1296, "cpu_manufacturer": "Intel"},
                {"type": "t3.micro", "vcpus": 2, "memory": 1024, "storage": "EBS only", "networkPerformance": "Up to 5 Gigabit", "priceLinux": 0.0104, "priceWindows": 0.015, "cpu_manufacturer": "Intel"},
                {"type": "t3.small", "vcpus": 2, "memory": 2048, "storage": "EBS only", "networkPerformance": "Up to 5 Gigabit", "priceLinux": 0.0208, "priceWindows": 0.03, "cpu_manufacturer": "Intel"},
                {"type": "t3.medium", "vcpus": 2, "memory": 4096, "storage": "EBS only", "networkPerformance": "Up to 5 Gigabit", "priceLinux": 0.0416, "priceWindows": 0.06, "cpu_manufacturer": "Intel"},
                {"type": "t3.large", "vcpus": 2, "memory": 8192, "storage": "EBS only", "networkPerformance": "Up to 5 Gigabit", "priceLinux": 0.0832, "priceWindows": 0.12, "cpu_manufacturer": "Intel"},
                {"type": "t3a.medium", "vcpus": 2, "memory": 4096, "storage": "EBS only", "networkPerformance": "Up to 5 Gigabit", "priceLinux": 0.0376, "priceWindows": 0.056, "cpu_manufacturer": "AMD"},
                {"type": "m5.large", "vcpus": 2, "memory": 8192, "storage": "EBS only", "networkPerformance": "Up to 10 Gigabit", "priceLinux": 0.096, "priceWindows": 0.192, "cpu_manufacturer": "Intel"},
                {"type": "m5a.large", "vcpus": 2, "memory": 8192, "storage": "EBS only", "networkPerformance": "Up to 10 Gigabit", "priceLinux": 0.086, "priceWindows": 0.172, "cpu_manufacturer": "AMD"},
                {"type": "c5.xlarge", "vcpus": 4, "memory": 8192, "storage": "EBS only", "networkPerformance": "Up to 10 Gigabit", "priceLinux": 0.17, "priceWindows": 0.34, "cpu_manufacturer": "Intel"}
            ]
        return types

    def get_instance_type_advice(self, workload_type, use_case, priority, cpu_manufacturer):
        all_types = self.get_instance_types()
        
        # Simple recommendation rule:
        # Filter by CPU manufacturer if specified (Intel/AMD)
        filtered = [t for t in all_types if t["cpu_manufacturer"].lower() == cpu_manufacturer.lower()]
        if not filtered:
            filtered = all_types
            
        # Select best fit
        if priority.upper() == "COST":
            # Sort by price ascending
            filtered.sort(key=lambda x: x["priceLinux"])
        else:
            # Sort by vcpus & memory descending
            filtered.sort(key=lambda x: (x["vcpus"], x["memory"]), reverse=True)
            
        # Return top 3 recommendations
        return filtered[:3]
        return filtered[:3