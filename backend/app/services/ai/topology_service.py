import boto3
from app.services.aws.aws_regions import get_all_regions


class TopologyService:

    def __init__(self):
        self.ec2_resources = []

    def _load_ec2_resources(self):
        self.ec2_resources = []
        regions = get_all_regions()
        for region in regions:
            try:
                ec2 = boto3.client("ec2", region_name=region)
                reservations = ec2.describe_instances().get("Reservations", [])
                for reservation in reservations:
                    for instance in reservation.get("Instances", []):
                        instance_id = instance["InstanceId"]
                        name = ""
                        for tag in instance.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"] or ""
                        
                        # Fallback name
                        if not name:
                            name = instance_id

                        # Gather all security groups
                        sgs = []
                        for sg in instance.get("SecurityGroups", []):
                            sgs.append({
                                "GroupId": sg["GroupId"],
                                "GroupName": sg["GroupName"]
                            })

                        self.ec2_resources.append({
                            "name": name,
                            "instance_id": instance_id,
                            "vpc_id": instance.get("VpcId"),
                            "subnet_id": instance.get("SubnetId"),
                            "security_groups": sgs
                        })
            except Exception:
                continue

    def find_dependencies(self, resource):
        if not resource:
            return {
                "success": False,
                "message": "Resource search value is empty"
            }

        resource = resource.lower()
        self._load_ec2_resources()

        # EC2
        for ec2 in self.ec2_resources:
            if (
                ec2["name"].lower() == resource
                or ec2["instance_id"].lower() == resource
            ):
                return {
                    "success": True,
                    "resource": ec2["name"],
                    "instance_id": ec2["instance_id"],
                    "dependencies": {
                        "vpc": ec2["vpc_id"],
                        "subnet": ec2["subnet_id"],
                        "security_groups": ec2["security_groups"]
                    }
                }

        return {
            "success": False,
            "message": f"Resource '{resource}' not found"
        }
