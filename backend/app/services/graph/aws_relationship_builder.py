from botocore.exceptions import ClientError
from botocore.exceptions import EndpointConnectionError
import boto3
import logging
from typing import Callable, Any

from app.providers.aws.regions import get_all_regions

logger = logging.getLogger(__name__)


class AWSRelationshipBuilder:
    # Relationship type constants
    IN_VPC = "IN_VPC"
    IN_SUBNET = "IN_SUBNET"
    USES_SECURITY_GROUP = "USES_SECURITY_GROUP"
    ATTACHED_VOLUME = "ATTACHED_VOLUME"
    ATTACHED_TO = "ATTACHED_TO"
    USES_ROLE = "USES_ROLE"
    ROUTES_TO = "ROUTES_TO"
    USES_TARGET_GROUP = "USES_TARGET_GROUP"
    TARGETS = "TARGETS"

    def __init__(self):
        self.regions = get_all_regions()
        # Cache for boto3 clients
        self.clients = {}
        try:
            self.iam = self.get_client("iam")
        except (ClientError, EndpointConnectionError, Exception):
            logger.exception("Unable to initialize IAM client")
            self.iam = None

    def get_client(self, service: str, region: str = None) -> Any:
        key = (service, region)
        if key not in self.clients:
            kwargs = {}
            if region:
                kwargs["region_name"] = region
            self.clients[key] = boto3.client(service, **kwargs)
        return self.clients[key]

    def scan_regions(self, service: str, callback: Callable) -> list[dict]:
        relationships = []
        for region in self.regions:
            try:
                client = self.get_client(service, region)
                relationships.extend(callback(client, region))
            except ClientError:
                logger.exception("%s scan failed in %s", service, region)
            except EndpointConnectionError:
                logger.exception("%s scan failed in %s", service, region)
            except Exception:
                logger.exception("%s scan failed in %s", service, region)
        return relationships

    def relationship(self, source: str, target: str, rel_type: str) -> dict:
        return {
            "from": source,
            "to": target,
            "type": rel_type
        }

    def build(self) -> list[dict]:
        relationships = []
        builders = [
            self.ec2_to_ebs,
            self.ec2_to_vpc,
            self.ec2_to_subnet,
            self.ec2_to_sg,
            self.subnet_to_vpc,
            self.sg_to_vpc,
            self.igw_to_vpc,
            self.rds_to_vpc,
            self.rds_to_subnet,
            self.rds_to_sg,
            self.ec2_to_iam,
            self.lambda_to_iam,
            self.lambda_to_vpc,
            self.lambda_to_subnet,
            self.lambda_to_sg,
            self.alb_to_ec2,
        ]

        for builder in builders:
            try:
                relationships.extend(builder())
            except (ClientError, EndpointConnectionError, Exception):
                logger.exception("Relationship builder failed: %s", builder.__name__)

        # Remove duplicate relationships
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel["from"], rel["to"], rel["type"])
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        logger.info(
            "Discovered %d unique relationships (%d duplicates removed)",
            len(unique_relationships),
            len(relationships) - len(unique_relationships)
        )
        return unique_relationships

    def ec2_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        vpc = instance.get("VpcId")
                        if vpc:
                            rels.append(self.relationship(instance["InstanceId"], vpc, self.IN_VPC))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_subnet(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        subnet = instance.get("SubnetId")
                        if subnet:
                            rels.append(self.relationship(instance["InstanceId"], subnet, self.IN_SUBNET))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_sg(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        for sg in instance.get("SecurityGroups", []):
                            rels.append(self.relationship(instance["InstanceId"], sg["GroupId"], self.USES_SECURITY_GROUP))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_ebs(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        for mapping in instance.get("BlockDeviceMappings", []):
                            ebs = mapping.get("Ebs")
                            if ebs:
                                rels.append(self.relationship(instance["InstanceId"], ebs["VolumeId"], self.ATTACHED_VOLUME))
            return rels
        return self.scan_regions("ec2", collect)

    def subnet_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_subnets(**params)
                for subnet in response.get("Subnets", []):
                    rels.append(self.relationship(subnet["SubnetId"], subnet["VpcId"], self.IN_VPC))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def sg_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_security_groups(**params)
                for sg in response.get("SecurityGroups", []):
                    vpc = sg.get("VpcId")
                    if vpc:
                        rels.append(self.relationship(sg["GroupId"], vpc, self.IN_VPC))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def igw_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_internet_gateways(**params)
                for igw in response.get("InternetGateways", []):
                    for attachment in igw.get("Attachments", []):
                        rels.append(self.relationship(igw["InternetGatewayId"], attachment["VpcId"], self.ATTACHED_TO))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def rds_to_vpc(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                    if vpc_id:
                        rels.append(self.relationship(db["DBInstanceIdentifier"], vpc_id, self.IN_VPC))
            return rels
        return self.scan_regions("rds", collect)

    def rds_to_subnet(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    rds_id = db["DBInstanceIdentifier"]
                    for subnet in db.get("DBSubnetGroup", {}).get("Subnets", []):
                        subnet_id = subnet.get("SubnetIdentifier")
                        if subnet_id:
                            rels.append(self.relationship(rds_id, subnet_id, self.IN_SUBNET))
            return rels
        return self.scan_regions("rds", collect)

    def rds_to_sg(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    rds_id = db["DBInstanceIdentifier"]
                    for sg in db.get("VpcSecurityGroups", []):
                        rels.append(self.relationship(rds_id, sg["VpcSecurityGroupId"], self.USES_SECURITY_GROUP))
            return rels
        return self.scan_regions("rds", collect)

    def ec2_to_iam(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        profile = instance.get("IamInstanceProfile")
                        if not profile:
                            continue
                        profile_arn = profile.get("Arn")
                        if not profile_arn:
                            continue
                        
                        try:
                            profile_name = profile_arn.split("/")[-1]
                            if self.iam:
                                res = self.iam.get_instance_profile(
                                    InstanceProfileName=profile_name
                                )
                                roles = res.get("InstanceProfile", {}).get("Roles", [])
                                for role in roles:
                                    rels.append(self.relationship(instance["InstanceId"], role["Arn"], self.USES_ROLE))
                        except Exception as e:
                            logger.warning(
                                "Failed to resolve IAM Role for instance profile %s: %s",
                                profile_arn, str(e)
                            )
            return rels
        return self.scan_regions("ec2", collect)

    def lambda_to_iam(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    role_arn = fn.get("Role")
                    if role_arn:
                        rels.append(self.relationship(fn["FunctionName"], role_arn, self.USES_ROLE))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_vpc(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    vpc_id = config.get("VpcId")
                    if vpc_id:
                        rels.append(self.relationship(fn["FunctionName"], vpc_id, self.IN_VPC))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_subnet(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    for subnet in config.get("SubnetIds", []):
                        rels.append(self.relationship(fn["FunctionName"], subnet, self.IN_SUBNET))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_sg(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    for sg in config.get("SecurityGroupIds", []):
                        rels.append(self.relationship(fn["FunctionName"], sg, self.USES_SECURITY_GROUP))
            return rels
        return self.scan_regions("lambda", collect)

    def alb_to_ec2(self) -> list[dict]:
        def collect(elbv2, region):
            rels = []
            for page in elbv2.get_paginator("describe_load_balancers").paginate():
                for lb in page["LoadBalancers"]:
                    lb_arn = lb["LoadBalancerArn"]
                    for tg_page in elbv2.get_paginator("describe_target_groups").paginate(LoadBalancerArn=lb_arn):
                        for tg in tg_page["TargetGroups"]:
                            tg_arn = tg["TargetGroupArn"]
                            rels.append(self.relationship(lb_arn, tg_arn, self.USES_TARGET_GROUP))
                            
                            health = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                            for target in health["TargetHealthDescriptions"]:
                                instance_id = target["Target"]["Id"]
                                rels.append(self.relationship(tg_arn, instance_id, self.TARGETS))
            return rels
        return self.scan_regions("elbv2", collect)
