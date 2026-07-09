import re

with open("backend/app/services/graph/aws_relationship_builder.py", "r") as f:
    text = f.read()

# Replace relationship method
old_rel = """    def relationship(
        self,
        source: str,
        target: str,
        rel_type: str
    ) -> dict:

        def get_resource_type(resource_id: str) -> str:

            if not resource_id:
                return "Resource"

            if resource_id.startswith("i-"):
                return "EC2"

            elif resource_id.startswith("vol-"):
                return "EBS"

            elif resource_id.startswith("vpc-"):
                return "VPC"

            elif resource_id.startswith("subnet-"):
                return "Subnet"

            elif resource_id.startswith("sg-"):
                return "SecurityGroup"

            elif resource_id.startswith("igw-"):
                return "InternetGateway"

            elif resource_id.startswith("eni-"):
                return "NetworkInterface"

            elif resource_id.startswith("rtb-"):
                return "RouteTable"

            elif resource_id.startswith("nat-"):
                return "NatGateway"

            elif resource_id.startswith("eipalloc-"):
                return "ElasticIP"

            elif resource_id.startswith("arn:aws:iam"):
                return "IAM"

            elif resource_id.startswith("arn:aws:elasticloadbalancing:"):

                if ":targetgroup/" in resource_id:
                    return "TargetGroup"

                return "ALB"

            return "Resource"

        return {
            "from": source,
            "to": target,
            "type": rel_type,
            "source_type": get_resource_type(source),
            "target_type": get_resource_type(target)
        }"""

new_rel = """    def relationship(
        self,
        source: str,
        target: str,
        rel_type: str,
        source_type: str,
        target_type: str
    ) -> dict:
        return {
            "from": source,
            "to": target,
            "type": rel_type,
            "source_type": source_type,
            "target_type": target_type
        }"""

text = text.replace(old_rel, new_rel)

reps = [
    (r"self\.relationship\(instance\[\"InstanceId\"\], vpc, self\.IN_VPC\)",
     r'self.relationship(instance["InstanceId"], vpc, self.IN_VPC, "EC2", "VPC")'),
    (r"self\.relationship\(instance\[\"InstanceId\"\], subnet, self\.IN_SUBNET\)",
     r'self.relationship(instance["InstanceId"], subnet, self.IN_SUBNET, "EC2", "Subnet")'),
    (r"self\.relationship\(instance\[\"InstanceId\"\], sg\[\"GroupId\"\], self\.USES_SECURITY_GROUP\)",
     r'self.relationship(instance["InstanceId"], sg["GroupId"], self.USES_SECURITY_GROUP, "EC2", "SecurityGroup")'),
    (r"self\.relationship\(instance\[\"InstanceId\"\], ebs\[\"VolumeId\"\], self\.ATTACHED_VOLUME\)",
     r'self.relationship(instance["InstanceId"], ebs["VolumeId"], self.ATTACHED_VOLUME, "EC2", "EBS")'),
    (r"self\.relationship\(subnet\[\"SubnetId\"\], subnet\[\"VpcId\"\], self\.IN_VPC\)",
     r'self.relationship(subnet["SubnetId"], subnet["VpcId"], self.IN_VPC, "Subnet", "VPC")'),
    (r"self\.relationship\(sg\[\"GroupId\"\], vpc, self\.IN_VPC\)",
     r'self.relationship(sg["GroupId"], vpc, self.IN_VPC, "SecurityGroup", "VPC")'),
    (r"self\.relationship\(igw\[\"InternetGatewayId\"\], attachment\[\"VpcId\"\], self\.ATTACHED_TO\)",
     r'self.relationship(igw["InternetGatewayId"], attachment["VpcId"], self.ATTACHED_TO, "InternetGateway", "VPC")'),
    (r"self\.relationship\(db\[\"DBInstanceIdentifier\"\], vpc_id, self\.IN_VPC\)",
     r'self.relationship(db["DBInstanceIdentifier"], vpc_id, self.IN_VPC, "RDS", "VPC")'),
    (r"self\.relationship\(rds_id, subnet_id, self\.IN_SUBNET\)",
     r'self.relationship(rds_id, subnet_id, self.IN_SUBNET, "RDS", "Subnet")'),
    (r"self\.relationship\(rds_id, sg\[\"VpcSecurityGroupId\"\], self\.USES_SECURITY_GROUP\)",
     r'self.relationship(rds_id, sg["VpcSecurityGroupId"], self.USES_SECURITY_GROUP, "RDS", "SecurityGroup")'),
    (r"self\.relationship\(instance\[\"InstanceId\"\], role\[\"Arn\"\], self\.USES_ROLE\)",
     r'self.relationship(instance["InstanceId"], role["Arn"], self.USES_ROLE, "EC2", "IAM")'),
    (r"self\.relationship\(fn\[\"FunctionName\"\], role_arn, self\.USES_ROLE\)",
     r'self.relationship(fn["FunctionName"], role_arn, self.USES_ROLE, "Lambda", "IAM")'),
    (r"self\.relationship\(fn\[\"FunctionName\"\], vpc_id, self\.IN_VPC\)",
     r'self.relationship(fn["FunctionName"], vpc_id, self.IN_VPC, "Lambda", "VPC")'),
    (r"self\.relationship\(fn\[\"FunctionName\"\], subnet, self\.IN_SUBNET\)",
     r'self.relationship(fn["FunctionName"], subnet, self.IN_SUBNET, "Lambda", "Subnet")'),
    (r"self\.relationship\(fn\[\"FunctionName\"\], sg, self\.USES_SECURITY_GROUP\)",
     r'self.relationship(fn["FunctionName"], sg, self.USES_SECURITY_GROUP, "Lambda", "SecurityGroup")'),
    (r"self\.relationship\(rt\[\"RouteTableId\"\], subnet_id, self\.ASSOCIATED_WITH\)",
     r'self.relationship(rt["RouteTableId"], subnet_id, self.ASSOCIATED_WITH, "RouteTable", "Subnet")'),
    (r"self\.relationship\(\s*rt\[\"RouteTableId\"\],\s*vpc_id,\s*self\.IN_VPC\s*\)",
     r'self.relationship(rt["RouteTableId"], vpc_id, self.IN_VPC, "RouteTable", "VPC")'),
    (r"self\.relationship\(rt\[\"RouteTableId\"\], gateway, self\.ROUTES_TO\)",
     r'self.relationship(rt["RouteTableId"], gateway, self.ROUTES_TO, "RouteTable", "InternetGateway")'),
    (r"self\.relationship\(rt\[\"RouteTableId\"\], nat, self\.ROUTES_TO\)",
     r'self.relationship(rt["RouteTableId"], nat, self.ROUTES_TO, "RouteTable", "NatGateway")'),
    (r"self\.relationship\(nat\[\"NatGatewayId\"\], subnet, self\.IN_SUBNET\)",
     r'self.relationship(nat["NatGatewayId"], subnet, self.IN_SUBNET, "NatGateway", "Subnet")'),
    (r"self\.relationship\(nat\[\"NatGatewayId\"\], allocation, self\.USES_ELASTIC_IP\)",
     r'self.relationship(nat["NatGatewayId"], allocation, self.USES_ELASTIC_IP, "NatGateway", "ElasticIP")'),
    (r"self\.relationship\(eni\[\"NetworkInterfaceId\"\], instance_id, self\.ATTACHED_TO\)",
     r'self.relationship(eni["NetworkInterfaceId"], instance_id, self.ATTACHED_TO, "NetworkInterface", "EC2")'),
    (r"self\.relationship\(eni_id, sg\[\"GroupId\"\], self\.USES_SECURITY_GROUP\)",
     r'self.relationship(eni_id, sg["GroupId"], self.USES_SECURITY_GROUP, "NetworkInterface", "SecurityGroup")'),
    (r"self\.relationship\(eni\[\"NetworkInterfaceId\"\], subnet, self\.IN_SUBNET\)",
     r'self.relationship(eni["NetworkInterfaceId"], subnet, self.IN_SUBNET, "NetworkInterface", "Subnet")'),
    (r"self\.relationship\(eni\[\"NetworkInterfaceId\"\], vpc, self\.IN_VPC\)",
     r'self.relationship(eni["NetworkInterfaceId"], vpc, self.IN_VPC, "NetworkInterface", "VPC")'),
    (r"self\.relationship\(group_name, instance\[\"InstanceId\"\], self\.MANAGES\)",
     r'self.relationship(group_name, instance["InstanceId"], self.MANAGES, "AutoScalingGroup", "EC2")'),
    (r"self\.relationship\(cluster_name, nodegroup, self\.HAS_NODEGROUP\)",
     r'self.relationship(cluster_name, nodegroup, self.HAS_NODEGROUP, "EKSCluster", "NodeGroup")'),
    (r"self\.relationship\(nodegroup, instance\[\"InstanceId\"\], self\.MANAGES\)",
     r'self.relationship(nodegroup, instance["InstanceId"], self.MANAGES, "NodeGroup", "EC2")'),
    (r"self\.relationship\(lb_arn, tg_arn, self\.USES_TARGET_GROUP\)",
     r'self.relationship(lb_arn, tg_arn, self.USES_TARGET_GROUP, "ALB", "TargetGroup")'),
    (r"self\.relationship\(tg_arn, instance_id, self\.TARGETS\)",
     r'self.relationship(tg_arn, instance_id, self.TARGETS, "TargetGroup", "EC2")'),
]
for p, r in reps:
    text = re.sub(p, r, text)

eip_1_old = """                            self.relationship(
                                allocation_id,
                                instance_id,
                                "ASSIGNED_TO"
                            )"""

eip_1_new = """                            {
                                "from": allocation_id,
                                "to": instance_id,
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "EC2"
                            }"""

eip_2_old = """                            self.relationship(
                                allocation_id,
                                eni,
                                "ASSIGNED_TO"
                            )"""

eip_2_new = """                            {
                                "from": allocation_id,
                                "to": eni,
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "NetworkInterface"
                            }"""

eip_3_old = """                            self.relationship(
                                allocation_id,
                                nat_map[allocation_id],
                                "ASSIGNED_TO"
                            )"""

eip_3_new = """                            {
                                "from": allocation_id,
                                "to": nat_map[allocation_id],
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "NatGateway"
                            }"""

text = text.replace(eip_1_old, eip_1_new)
text = text.replace(eip_2_old, eip_2_new)
text = text.replace(eip_3_old, eip_3_new)

with open("backend/app/services/graph/aws_relationship_builder.py", "w") as f:
    f.write(text)

print("Replacement complete")
