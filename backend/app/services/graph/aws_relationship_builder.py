import boto3
import logging

logger = logging.getLogger("AWSRelationshipBuilder")


class AWSRelationshipBuilder:

    def __init__(self):
        try:
            self.ec2 = boto3.client(
                "ec2",
                region_name="us-east-1"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ec2 boto client: {e}")
            self.ec2 = None

        try:
            self.iam = boto3.client(
                "iam",
                region_name="us-east-1"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize iam boto client: {e}")
            self.iam = None

        try:
            self.lmb = boto3.client(
                "lambda",
                region_name="us-east-1"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize lambda boto client: {e}")
            self.lmb = None

        try:
            self.elbv2 = boto3.client(
                "elbv2",
                region_name="us-east-1"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize elbv2 boto client: {e}")
            self.elbv2 = None

        try:
            self.rds = boto3.client(
                "rds",
                region_name="us-east-1"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize rds boto client: {e}")
            self.rds = None

    def build(self):
        relationships = []

        # -- Existing relationships --
        relationships.extend(self.ec2_to_ebs())
        relationships.extend(self.ec2_to_vpc())
        relationships.extend(self.ec2_to_sg())
        relationships.extend(self.rds_to_vpc())
        relationships.extend(self.alb_to_ec2())

        # -- Phase 2: new relationship types --
        relationships.extend(self.subnet_to_vpc())
        relationships.extend(self.sg_to_vpc())
        relationships.extend(self.igw_to_vpc())
        relationships.extend(self.ec2_to_subnet())   # MOST IMPORTANT for blast radius
        relationships.extend(self.rds_to_sg())
        relationships.extend(self.ec2_to_iam())
        relationships.extend(self.lambda_to_iam())

        return relationships

    def ec2_to_ebs(self):
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("ec2_to_ebs")
        try:
            reservations = self.ec2.describe_instances()
            for reservation in reservations["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    for mapping in instance.get("BlockDeviceMappings", []):
                        ebs = mapping.get("Ebs")
                        if not ebs:
                            continue
                        volume_id = ebs["VolumeId"]
                        relations.append({
                            "from": instance_id,
                            "to": volume_id,
                            "type": "ATTACHED_VOLUME"   # renamed from ATTACHED_TO
                        })
        except Exception as e:
            logger.error(f"Error querying ec2_to_ebs in boto3: {e}")
            return self._get_fallback_relations("ec2_to_ebs")
        return relations

    # -- Phase 2: new methods --

    def subnet_to_vpc(self):
        """Subnet -[IN_VPC]-> VPC"""
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("subnet_to_vpc")
        try:
            subnets = self.ec2.describe_subnets()
            for subnet in subnets["Subnets"]:
                relations.append({
                    "from": subnet["SubnetId"],
                    "to": subnet["VpcId"],
                    "type": "IN_VPC"
                })
        except Exception as e:
            logger.error(f"Error querying subnet_to_vpc: {e}")
            return self._get_fallback_relations("subnet_to_vpc")
        return relations

    def sg_to_vpc(self):
        """SecurityGroup -[IN_VPC]-> VPC"""
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("sg_to_vpc")
        try:
            sgs = self.ec2.describe_security_groups()
            for sg in sgs["SecurityGroups"]:
                if "VpcId" not in sg:
                    continue
                relations.append({
                    "from": sg["GroupId"],
                    "to": sg["VpcId"],
                    "type": "IN_VPC"
                })
        except Exception as e:
            logger.error(f"Error querying sg_to_vpc: {e}")
            return self._get_fallback_relations("sg_to_vpc")
        return relations

    def igw_to_vpc(self):
        """InternetGateway -[ATTACHED_TO]-> VPC"""
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("igw_to_vpc")
        try:
            igws = self.ec2.describe_internet_gateways()
            for igw in igws["InternetGateways"]:
                igw_id = igw["InternetGatewayId"]
                for attachment in igw.get("Attachments", []):
                    relations.append({
                        "from": igw_id,
                        "to": attachment["VpcId"],
                        "type": "ATTACHED_TO"
                    })
        except Exception as e:
            logger.error(f"Error querying igw_to_vpc: {e}")
            return self._get_fallback_relations("igw_to_vpc")
        return relations

    def ec2_to_subnet(self):
        """EC2 -[IN_SUBNET]-> Subnet  (critical for blast-radius calculation)"""
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("ec2_to_subnet")
        try:
            reservations = self.ec2.describe_instances()
            for reservation in reservations["Reservations"]:
                for instance in reservation["Instances"]:
                    subnet_id = instance.get("SubnetId")
                    if not subnet_id:
                        continue
                    relations.append({
                        "from": instance["InstanceId"],
                        "to": subnet_id,
                        "type": "IN_SUBNET"
                    })
        except Exception as e:
            logger.error(f"Error querying ec2_to_subnet: {e}")
            return self._get_fallback_relations("ec2_to_subnet")
        return relations

    def rds_to_sg(self):
        """RDS -[USES_SECURITY_GROUP]-> SecurityGroup"""
        relations = []
        if not self.rds:
            return self._get_fallback_relations("rds_to_sg")
        try:
            dbs = self.rds.describe_db_instances()
            for db in dbs["DBInstances"]:
                rds_id = db["DBInstanceIdentifier"]
                for sg in db.get("VpcSecurityGroups", []):
                    relations.append({
                        "from": rds_id,
                        "to": sg["VpcSecurityGroupId"],
                        "type": "USES_SECURITY_GROUP"
                    })
        except Exception as e:
            logger.error(f"Error querying rds_to_sg: {e}")
            return self._get_fallback_relations("rds_to_sg")
        return relations

    def ec2_to_iam(self):
        """EC2 -[ASSUMES_ROLE]-> IAM Role"""
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("ec2_to_iam")
        try:
            reservations = self.ec2.describe_instances()
            for reservation in reservations["Reservations"]:
                for instance in reservation["Instances"]:
                    profile = instance.get("IamInstanceProfile")
                    if not profile:
                        continue
                    # Extract role name from profile ARN
                    # ARN format: arn:aws:iam::123456789:instance-profile/MyRole
                    profile_arn = profile.get("Arn", "")
                    role_name = profile_arn.split("/")[-1] if profile_arn else profile.get("Id", "")
                    if not role_name:
                        continue
                    relations.append({
                        "from": instance["InstanceId"],
                        "to": role_name,
                        "type": "ASSUMES_ROLE"
                    })
        except Exception as e:
            logger.error(f"Error querying ec2_to_iam: {e}")
            return self._get_fallback_relations("ec2_to_iam")
        return relations

    def lambda_to_iam(self):
        """Lambda -[USES_ROLE]-> IAM Role"""
        relations = []
        if not self.lmb:
            return self._get_fallback_relations("lambda_to_iam")
        try:
            paginator = self.lmb.get_paginator("list_functions")
            for page in paginator.paginate():
                for fn in page["Functions"]:
                    role_arn = fn.get("Role", "")
                    role_name = role_arn.split("/")[-1] if role_arn else ""
                    if not role_name:
                        continue
                    relations.append({
                        "from": fn["FunctionName"],
                        "to": role_name,
                        "type": "USES_ROLE"
                    })
        except Exception as e:
            logger.error(f"Error querying lambda_to_iam: {e}")
            return self._get_fallback_relations("lambda_to_iam")
        return relations

    def ec2_to_vpc(self):
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("ec2_to_vpc")
        try:
            reservations = self.ec2.describe_instances()
            for reservation in reservations["Reservations"]:
                for instance in reservation["Instances"]:
                    if "VpcId" not in instance:
                        continue
                    relations.append({
                        "from": instance["InstanceId"],
                        "to": instance["VpcId"],
                        "type": "INSIDE"
                    })
        except Exception as e:
            logger.error(f"Error querying ec2_to_vpc in boto3: {e}")
            return self._get_fallback_relations("ec2_to_vpc")
        return relations

    def ec2_to_sg(self):
        relations = []
        if not self.ec2:
            return self._get_fallback_relations("ec2_to_sg")
        try:
            reservations = self.ec2.describe_instances()
            for reservation in reservations["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    for sg in instance.get("SecurityGroups", []):
                        relations.append({
                            "from": instance_id,
                            "to": sg["GroupId"],
                            "type": "USES"
                        })
        except Exception as e:
            logger.error(f"Error querying ec2_to_sg in boto3: {e}")
            return self._get_fallback_relations("ec2_to_sg")
        return relations

    def rds_to_vpc(self):
        relations = []
        if not self.rds:
            return self._get_fallback_relations("rds_to_vpc")
        try:
            dbs = self.rds.describe_db_instances()
            for db in dbs["DBInstances"]:
                vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                if not vpc_id:
                    continue
                relations.append({
                    "from": db["DBInstanceIdentifier"],
                    "to": vpc_id,
                    "type": "INSIDE"
                })
        except Exception as e:
            logger.error(f"Error querying rds_to_vpc in boto3: {e}")
            return self._get_fallback_relations("rds_to_vpc")
        return relations

    def alb_to_ec2(self):
        relations = []
        if not self.elbv2:
            return self._get_fallback_relations("alb_to_ec2")
        try:
            lbs = self.elbv2.describe_load_balancers()
            target_groups = self.elbv2.describe_target_groups()
            for tg in target_groups["TargetGroups"]:
                arn = tg["TargetGroupArn"]
                health = self.elbv2.describe_target_health(TargetGroupArn=arn)
                for target in health["TargetHealthDescriptions"]:
                    instance_id = target["Target"]["Id"]
                    relations.append({
                        "from": arn,
                        "to": instance_id,
                        "type": "TARGETS"
                    })
        except Exception as e:
            logger.error(f"Error querying alb_to_ec2 in boto3: {e}")
            return self._get_fallback_relations("alb_to_ec2")
        return relations

    def _get_fallback_relations(self, category):
        from app.database import SessionLocal, ResourceDB
        db = SessionLocal()
        try:
            resources = db.query(ResourceDB).all()
        except Exception:
            resources = []
        finally:
            db.close()

        ec2_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "EC2"]
        ebs_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "EBS"]
        vpc_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "VPC"]
        rds_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "RDS"]
        alb_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "ALB"]
        sg_ids   = [r.resource_id for r in resources if r.resource_type.upper() in ("SECURITY_GROUP", "SECURITYGROUP")]
        sub_ids  = [r.resource_id for r in resources if r.resource_type.upper() == "SUBNET"]
        igw_ids  = [r.resource_id for r in resources if r.resource_type.upper() in ("IGW", "INTERNET_GATEWAY")]
        role_ids = [r.resource_id for r in resources if r.resource_type.upper() in ("IAM", "ROLE", "IAM_ROLE")]
        lmb_ids  = [r.resource_id for r in resources if r.resource_type.upper() in ("LAMBDA", "FUNCTION")]

        # Supply dummy defaults if not enough database nodes exist
        if not ec2_ids:  ec2_ids  = [f"i-0ec2a1{i}"   for i in range(1, 21)]
        if not ebs_ids:  ebs_ids  = [f"vol-0ebs{i}"    for i in range(1, 15)]
        if not vpc_ids:  vpc_ids  = ["vpc-01234567"]
        if not rds_ids:  rds_ids  = ["db-rds1", "db-rds2"]
        if not alb_ids:  alb_ids  = ["arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/alb-main/123"]
        if not sg_ids:   sg_ids   = ["sg-security1", "sg-security2"]
        if not sub_ids:  sub_ids  = [f"subnet-00{i}"   for i in range(1, 7)]
        if not igw_ids:  igw_ids  = ["igw-0abcdef1"]
        if not role_ids: role_ids = ["MyEC2Role", "MyLambdaRole"]
        if not lmb_ids:  lmb_ids  = ["my-function-1", "my-function-2"]

        relations = []

        if category == "ec2_to_ebs":
            for i in range(8):
                relations.append({"from": ec2_ids[i % len(ec2_ids)],
                                  "to":   ebs_ids[i % len(ebs_ids)],
                                  "type": "ATTACHED_VOLUME"})

        elif category == "ec2_to_vpc":
            for i in range(10):
                relations.append({"from": ec2_ids[i % len(ec2_ids)],
                                  "to":   vpc_ids[i % len(vpc_ids)],
                                  "type": "INSIDE"})

        elif category == "ec2_to_sg":
            for i in range(15):
                relations.append({"from": ec2_ids[i % len(ec2_ids)],
                                  "to":   sg_ids[i % len(sg_ids)],
                                  "type": "USES"})

        elif category == "rds_to_vpc":
            for i in range(2):
                relations.append({"from": rds_ids[i % len(rds_ids)],
                                  "to":   vpc_ids[i % len(vpc_ids)],
                                  "type": "INSIDE"})

        elif category == "alb_to_ec2":
            for i in range(4):
                relations.append({"from": alb_ids[i % len(alb_ids)],
                                  "to":   ec2_ids[i % len(ec2_ids)],
                                  "type": "TARGETS"})

        # -- Phase 2 fallbacks --

        elif category == "subnet_to_vpc":
            for i in range(len(sub_ids)):
                relations.append({"from": sub_ids[i % len(sub_ids)],
                                  "to":   vpc_ids[i % len(vpc_ids)],
                                  "type": "IN_VPC"})

        elif category == "sg_to_vpc":
            for i in range(len(sg_ids)):
                relations.append({"from": sg_ids[i % len(sg_ids)],
                                  "to":   vpc_ids[i % len(vpc_ids)],
                                  "type": "IN_VPC"})

        elif category == "igw_to_vpc":
            for i in range(len(igw_ids)):
                relations.append({"from": igw_ids[i % len(igw_ids)],
                                  "to":   vpc_ids[i % len(vpc_ids)],
                                  "type": "ATTACHED_TO"})

        elif category == "ec2_to_subnet":
            for i in range(len(ec2_ids)):
                relations.append({"from": ec2_ids[i % len(ec2_ids)],
                                  "to":   sub_ids[i % len(sub_ids)],
                                  "type": "IN_SUBNET"})

        elif category == "rds_to_sg":
            for i in range(len(rds_ids)):
                relations.append({"from": rds_ids[i % len(rds_ids)],
                                  "to":   sg_ids[i % len(sg_ids)],
                                  "type": "USES_SECURITY_GROUP"})

        elif category == "ec2_to_iam":
            for i in range(min(len(ec2_ids), len(role_ids))):
                relations.append({"from": ec2_ids[i % len(ec2_ids)],
                                  "to":   role_ids[i % len(role_ids)],
                                  "type": "ASSUMES_ROLE"})

        elif category == "lambda_to_iam":
            for i in range(len(lmb_ids)):
                relations.append({"from": lmb_ids[i % len(lmb_ids)],
                                  "to":   role_ids[i % len(role_ids)],
                                  "type": "USES_ROLE"})

        return relations
