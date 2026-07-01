import boto3
import logging

from app.providers.aws.regions import get_all_regions

logger = logging.getLogger(__name__)


class AWSRelationshipBuilder:

    def __init__(self):

        self.regions = get_all_regions()

        # Cache for boto3 clients
        self.clients = {}

        try:
            self.iam = self.get_client("iam")
        except Exception:
            logger.exception("Unable to initialize IAM client")
            self.iam = None

    def get_client(self, service, region=None):
        """
        Returns a cached boto3 client.

        A client is created only once for each
        (service, region) combination.
        """
        key = (service, region)

        if key not in self.clients:
            kwargs = {}
            if region:
                kwargs["region_name"] = region

            self.clients[key] = boto3.client(
                service,
                **kwargs
            )

        return self.clients[key]

    def build(self):
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
            self.alb_to_ec2,
        ]

        for builder in builders:
            try:
                relationships.extend(builder())
            except Exception:
                logger.exception(
                    "Relationship builder failed: %s",
                    builder.__name__
                )

        # Remove duplicate relationships
        seen = set()
        unique_relationships = []

        for relationship in relationships:
            key = (
                relationship["from"],
                relationship["to"],
                relationship["type"]
            )
            if key not in seen:
                seen.add(key)
                unique_relationships.append(relationship)

        logger.info(
            "Discovered %d unique relationships (%d duplicates removed)",
            len(unique_relationships),
            len(relationships) - len(unique_relationships)
        )

        return unique_relationships

    def ec2_to_vpc(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for reservation in page["Reservations"]:
                        for instance in reservation["Instances"]:
                            vpc = instance.get("VpcId")
                            if not vpc:
                                continue
                            relationships.append({
                                "from": instance["InstanceId"],
                                "to": vpc,
                                "type": "IN_VPC"
                            })
            except Exception:
                logger.exception("EC2->VPC failed in %s", region)
        return relationships

    def ec2_to_subnet(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for reservation in page["Reservations"]:
                        for instance in reservation["Instances"]:
                            subnet = instance.get("SubnetId")
                            if subnet:
                                relationships.append({
                                    "from": instance["InstanceId"],
                                    "to": subnet,
                                    "type": "IN_SUBNET"
                                })
            except Exception:
                logger.exception("EC2->Subnet failed in %s", region)
        return relationships

    def ec2_to_sg(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for reservation in page["Reservations"]:
                        for instance in reservation["Instances"]:
                            for sg in instance.get("SecurityGroups", []):
                                relationships.append({
                                    "from": instance["InstanceId"],
                                    "to": sg["GroupId"],
                                    "type": "USES_SECURITY_GROUP"
                                })
            except Exception:
                logger.exception("EC2->SG failed in %s", region)
        return relationships

    def ec2_to_ebs(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for reservation in page["Reservations"]:
                        for instance in reservation["Instances"]:
                            for mapping in instance.get("BlockDeviceMappings", []):
                                ebs = mapping.get("Ebs")
                                if not ebs:
                                    continue
                                relationships.append({
                                    "from": instance["InstanceId"],
                                    "to": ebs["VolumeId"],
                                    "type": "ATTACHED_VOLUME"
                                })
            except Exception:
                logger.exception("EC2->EBS failed in %s", region)
        return relationships

    def subnet_to_vpc(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                response = ec2.describe_subnets()
                for subnet in response["Subnets"]:
                    relationships.append({
                        "from": subnet["SubnetId"],
                        "to": subnet["VpcId"],
                        "type": "IN_VPC"
                    })
            except Exception:
                logger.exception("Subnet->VPC failed in %s", region)
        return relationships

    def sg_to_vpc(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                response = ec2.describe_security_groups()
                for sg in response["SecurityGroups"]:
                    vpc = sg.get("VpcId")
                    if not vpc:
                        continue
                    relationships.append({
                        "from": sg["GroupId"],
                        "to": vpc,
                        "type": "IN_VPC"
                    })
            except Exception:
                logger.exception("SG->VPC failed in %s", region)
        return relationships

    def igw_to_vpc(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                response = ec2.describe_internet_gateways()
                for igw in response["InternetGateways"]:
                    for attachment in igw.get("Attachments", []):
                        relationships.append({
                            "from": igw["InternetGatewayId"],
                            "to": attachment["VpcId"],
                            "type": "ATTACHED_TO"
                        })
            except Exception:
                logger.exception("IGW->VPC failed in %s", region)
        return relationships

    def rds_to_vpc(self):
        relationships = []
        for region in self.regions:
            try:
                rds = self.get_client("rds", region)
                paginator = rds.get_paginator("describe_db_instances")
                for page in paginator.paginate():
                    for db in page["DBInstances"]:
                        vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                        if not vpc_id:
                            continue
                        relationships.append({
                            "from": db["DBInstanceIdentifier"],
                            "to": vpc_id,
                            "type": "IN_VPC"
                        })
            except Exception:
                logger.exception("RDS->VPC failed in %s", region)
        return relationships

    def rds_to_subnet(self):
        relationships = []
        for region in self.regions:
            try:
                rds = self.get_client("rds", region)
                paginator = rds.get_paginator("describe_db_instances")
                for page in paginator.paginate():
                    for db in page["DBInstances"]:
                        rds_id = db["DBInstanceIdentifier"]
                        subnet_group = db.get("DBSubnetGroup", {})
                        for subnet in subnet_group.get("Subnets", []):
                            subnet_id = subnet.get("SubnetIdentifier")
                            if subnet_id:
                                relationships.append({
                                    "from": rds_id,
                                    "to": subnet_id,
                                    "type": "IN_SUBNET"
                                })
            except Exception:
                logger.exception("RDS->Subnet failed in %s", region)
        return relationships

    def rds_to_sg(self):
        relationships = []
        for region in self.regions:
            try:
                rds = self.get_client("rds", region)
                paginator = rds.get_paginator("describe_db_instances")
                for page in paginator.paginate():
                    for db in page["DBInstances"]:
                        rds_id = db["DBInstanceIdentifier"]
                        for sg in db.get("VpcSecurityGroups", []):
                            relationships.append({
                                "from": rds_id,
                                "to": sg["VpcSecurityGroupId"],
                                "type": "USES_SECURITY_GROUP"
                            })
            except Exception:
                logger.exception("RDS->SG failed in %s", region)
        return relationships

    def ec2_to_iam(self):
        relationships = []
        for region in self.regions:
            try:
                ec2 = self.get_client("ec2", region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for reservation in page["Reservations"]:
                        for instance in reservation["Instances"]:
                            profile = instance.get("IamInstanceProfile")
                            if not profile:
                                continue
                            profile_arn = profile.get("Arn")
                            if not profile_arn:
                                continue
                            relationships.append({
                                "from": instance["InstanceId"],
                                "to": profile_arn,
                                "type": "ASSUMES_ROLE"
                            })
            except Exception:
                logger.exception("EC2->IAM failed in %s", region)
        return relationships

    def lambda_to_iam(self):
        relationships = []
        for region in self.regions:
            try:
                lmb = self.get_client("lambda", region)
                paginator = lmb.get_paginator("list_functions")
                for page in paginator.paginate():
                    for fn in page["Functions"]:
                        role_arn = fn.get("Role")
                        if not role_arn:
                            continue
                        relationships.append({
                            "from": fn["FunctionName"],
                            "to": role_arn,
                            "type": "USES_ROLE"
                        })
            except Exception:
                logger.exception("Lambda->IAM failed in %s", region)
        return relationships

    def alb_to_ec2(self):
        relationships = []
        for region in self.regions:
            try:
                elbv2 = self.get_client("elbv2", region)
                paginator = elbv2.get_paginator("describe_target_groups")
                for page in paginator.paginate():
                    for tg in page["TargetGroups"]:
                        arn = tg["TargetGroupArn"]
                        health = elbv2.describe_target_health(TargetGroupArn=arn)
                        for target in health["TargetHealthDescriptions"]:
                            instance_id = target["Target"]["Id"]
                            relationships.append({
                                "from": arn,
                                "to": instance_id,
                                "type": "TARGETS"
                            })
            except Exception:
                logger.exception("ALB->EC2 failed in %s", region)
        return relationships
