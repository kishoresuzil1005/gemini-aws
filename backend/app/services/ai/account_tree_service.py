import boto3

from app.services.aws.aws_regions import get_all_regions


class AccountTreeService:

    def generate_tree(self):

        tree = []

        tree.append("AWS ACCOUNT")

        nodes = []
        edges = []

        # Add root account node
        nodes.append({
            "id": "aws_account",
            "type": "account",
            "label": "AWS Account"
        })

        regions = get_all_regions()

        active_regions_data = []

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                rds = boto3.client(
                    "rds",
                    region_name=region
                )

                elb = boto3.client(
                    "elbv2",
                    region_name=region
                )

                # Get VPCs
                try:
                    vpcs_resp = ec2.describe_vpcs()
                    vpcs = vpcs_resp.get("Vpcs", [])
                except Exception:
                    vpcs = []

                # Get Instances
                try:
                    reservations = ec2.describe_instances().get("Reservations", [])
                    instances = []
                    for reservation in reservations:
                        for inst in reservation.get("Instances", []):
                            name = inst["InstanceId"]
                            for tag in inst.get("Tags", []):
                                if tag["Key"] == "Name":
                                    name = tag["Value"]
                            instances.append({
                                "instance_id": inst["InstanceId"],
                                "name": name,
                                "state": inst["State"]["Name"],
                                "instance_type": inst["InstanceType"],
                                "vpc_id": inst.get("VpcId"),
                                "subnet_id": inst.get("SubnetId"),
                                "security_groups": inst.get("SecurityGroups", [])
                            })
                except Exception:
                    instances = []

                # Get Subnets
                try:
                    subnets = ec2.describe_subnets().get("Subnets", [])
                except Exception:
                    subnets = []

                # Get Security Groups
                try:
                    sgs = ec2.describe_security_groups().get("SecurityGroups", [])
                except Exception:
                    sgs = []

                # Get RDS Instances
                try:
                    databases = rds.describe_db_instances().get("DBInstances", [])
                except Exception:
                    databases = []

                # Get Load Balancers
                try:
                    lbs = elb.describe_load_balancers().get("LoadBalancers", [])
                except Exception:
                    lbs = []

                # Get Internet Gateways
                try:
                    igws = ec2.describe_internet_gateways().get("InternetGateways", [])
                except Exception:
                    igws = []

                # Get NAT Gateways
                try:
                    nat_gws_resp = ec2.describe_nat_gateways()
                    nat_gws = nat_gws_resp.get("NatGateways", [])
                except Exception:
                    nat_gws = []

                # If no resources found, skip this region entirely
                if not (vpcs or instances or subnets or sgs or databases or lbs or igws or nat_gws):
                    continue

                active_regions_data.append({
                    "region": region,
                    "vpcs": vpcs,
                    "instances": instances,
                    "subnets": subnets,
                    "sgs": sgs,
                    "databases": databases,
                    "lbs": lbs,
                    "igws": igws,
                    "nat_gws": nat_gws
                })

            except Exception:
                continue

        # Print/Draw Active Regions
        for idx_reg, reg_data in enumerate(active_regions_data):

            region_name = reg_data["region"]
            is_last_region = (idx_reg == len(active_regions_data) - 1)

            region_prefix = "└──" if is_last_region else "├──"
            tree.append(f"{region_prefix} {region_name}")

            sub_prefix = "    " if is_last_region else "│   "

            vpcs = reg_data["vpcs"]
            instances = reg_data["instances"]
            subnets = reg_data["subnets"]
            sgs = reg_data["sgs"]
            databases = reg_data["databases"]
            lbs = reg_data["lbs"]
            igws = reg_data["igws"]
            nat_gws = reg_data["nat_gws"]

            # Add region node & link to account with relationship type
            nodes.append({
                "id": region_name,
                "type": "region",
                "label": region_name
            })
            edges.append({
                "source": region_name,
                "target": "aws_account",
                "relationship": "PART_OF_ACCOUNT"
            })

            # VPCs Section
            if vpcs:

                tree.append(f"{sub_prefix}├── VPCs ({len(vpcs)})")

                for vpc in vpcs:

                    vpc_id = vpc["VpcId"]
                    vpc_name = vpc_id
                    for tag in vpc.get("Tags", []):
                        if tag["Key"] == "Name":
                            vpc_name = tag["Value"]

                    # Node for VPC
                    nodes.append({
                        "id": vpc_id,
                        "type": "vpc",
                        "label": vpc_name,
                        "region": region_name
                    })
                    edges.append({
                        "source": vpc_id,
                        "target": region_name,
                        "relationship": "IN_REGION"
                    })

                    tree.append(f"{sub_prefix}│   ├── {vpc_id} ({vpc_name})")

                    # Subnets inside this VPC
                    vpc_subnets = [s for s in subnets if s.get("VpcId") == vpc_id]
                    if vpc_subnets:
                        tree.append(f"{sub_prefix}│   │   ├── Subnets ({len(vpc_subnets)})")
                        for sub in vpc_subnets:
                            sub_id = sub["SubnetId"]
                            cidr = sub.get("CidrBlock", "N/A")
                            # Node for Subnet
                            nodes.append({
                                "id": sub_id,
                                "type": "subnet",
                                "label": sub_id,
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            edges.append({
                                "source": sub_id,
                                "target": vpc_id,
                                "relationship": "IN_VPC"
                            })
                            tree.append(f"{sub_prefix}│   │   │   ├── {sub_id} ({cidr})")

                    # Security Groups inside this VPC
                    vpc_sgs = [sg for sg in sgs if sg.get("VpcId") == vpc_id]
                    if vpc_sgs:
                        tree.append(f"{sub_prefix}│   │   ├── Security Groups ({len(vpc_sgs)})")
                        for sg in vpc_sgs:
                            sg_id = sg["GroupId"]
                            sg_name = sg.get("GroupName", "N/A")
                            # Node for Security Group
                            nodes.append({
                                "id": sg_id,
                                "type": "security_group",
                                "label": sg_name,
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            edges.append({
                                "source": sg_id,
                                "target": vpc_id,
                                "relationship": "IN_VPC"
                            })
                            tree.append(f"{sub_prefix}│   │   │   ├── {sg_id} ({sg_name})")

                    # Instances inside this VPC
                    vpc_instances = [i for i in instances if i.get("vpc_id") == vpc_id]
                    if vpc_instances:
                        tree.append(f"{sub_prefix}│   │   ├── EC2 Instances ({len(vpc_instances)})")
                        for inst in vpc_instances:
                            inst_id = inst["instance_id"]
                            # Node for Instance
                            nodes.append({
                                "id": inst_id,
                                "type": "ec2",
                                "label": inst["name"],
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            target_node = inst.get("subnet_id") if inst.get("subnet_id") else vpc_id
                            edges.append({
                                "source": inst_id,
                                "target": target_node,
                                "relationship": "IN_SUBNET" if inst.get("subnet_id") else "IN_VPC"
                            })
                            # EC2 -> Security Groups relationship
                            for sg in inst.get("security_groups", []):
                                edges.append({
                                    "source": inst_id,
                                    "target": sg["GroupId"],
                                    "relationship": "USES_SECURITY_GROUP"
                                })
                            tree.append(f"{sub_prefix}│   │   │   ├── {inst['name']} ({inst_id}) [{inst['state']}]")

                    # RDS inside this VPC
                    vpc_dbs = []
                    for db in databases:
                        db_vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                        if db_vpc_id == vpc_id:
                            vpc_dbs.append(db)

                    if vpc_dbs:
                        tree.append("")
                        tree.append(f"{sub_prefix}│   │   ├── RDS Instances ({len(vpc_dbs)})")
                        for db in vpc_dbs:
                            db_id = db["DBInstanceIdentifier"]
                            # Node for RDS
                            nodes.append({
                                "id": db_id,
                                "type": "rds",
                                "label": db_id,
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            edges.append({
                                "source": db_id,
                                "target": vpc_id,
                                "relationship": "IN_VPC"
                            })
                            # RDS -> Security Groups relationship
                            for sg in db.get("VpcSecurityGroups", []):
                                edges.append({
                                    "source": db_id,
                                    "target": sg["VpcSecurityGroupId"],
                                    "relationship": "USES_SECURITY_GROUP"
                                })
                            tree.append(f"{sub_prefix}│   │   │   ├── {db_id}")

                    # Internet Gateways
                    vpc_igws = []
                    for igw in igws:
                        for att in igw.get("Attachments", []):
                            if att.get("VpcId") == vpc_id:
                                vpc_igws.append(igw)
                                break
                    if vpc_igws:
                        tree.append(f"{sub_prefix}│   │   ├── Internet Gateways ({len(vpc_igws)})")
                        for igw in vpc_igws:
                            igw_id = igw["InternetGatewayId"]
                            nodes.append({
                                "id": igw_id,
                                "type": "internet_gateway",
                                "label": igw_id,
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            edges.append({
                                "source": igw_id,
                                "target": vpc_id,
                                "relationship": "ATTACHED_TO"
                            })
                            tree.append(f"{sub_prefix}│   │   │   ├── Internet Gateways ({len(vpc_igws)}) [{igw_id}]")

                    # NAT Gateways
                    vpc_nat_gws = [nat for nat in nat_gws if nat.get("VpcId") == vpc_id]
                    if vpc_nat_gws:
                        tree.append(f"{sub_prefix}│   │   ├── NAT Gateways ({len(vpc_nat_gws)})")
                        for nat in vpc_nat_gws:
                            nat_id = nat["NatGatewayId"]
                            nodes.append({
                                "id": nat_id,
                                "type": "nat_gateway",
                                "label": nat_id,
                                "region": region_name,
                                "vpc_id": vpc_id
                            })
                            edges.append({
                                "source": nat_id,
                                "target": vpc_id,
                                "relationship": "ATTACHED_TO"
                            })
                            tree.append(f"{sub_prefix}│   │   │   ├── NAT Gateways ({len(vpc_nat_gws)}) [{nat_id}]")

            # Load Balancers
            if lbs:
                tree.append(f"{sub_prefix}├── Load Balancers ({len(lbs)})")
                for lb in lbs:
                    lb_arn = lb.get("LoadBalancerArn", lb.get("LoadBalancerName"))
                    lb_name = lb["LoadBalancerName"]
                    lb_vpc_id = lb.get("VpcId")

                    # Node for Load Balancer
                    nodes.append({
                        "id": lb_arn,
                        "type": "load_balancer",
                        "label": lb_name,
                        "region": region_name,
                        "vpc_id": lb_vpc_id
                    })
                    target_parent = lb_vpc_id if lb_vpc_id else region_name
                    lb_rel = "IN_VPC" if lb_vpc_id else "IN_REGION"
                    edges.append({
                        "source": lb_arn,
                        "target": target_parent,
                        "relationship": lb_rel
                    })
                    tree.append(f"{sub_prefix}│   ├── LB: {lb_name}")

        # S3 Section
        try:

            s3 = boto3.client("s3")
            buckets = s3.list_buckets().get("Buckets", [])

            if buckets:

                tree.append("")
                tree.append("S3 BUCKETS")

                for idx, bucket in enumerate(buckets):

                    bucket_name = bucket["Name"]
                    bucket_prefix = "└──" if idx == len(buckets) - 1 else "├──"
                    tree.append(f"{bucket_prefix} {bucket_name}")

                    # Add S3 Node
                    nodes.append({
                        "id": f"s3_{bucket_name}",
                        "type": "s3",
                        "label": bucket_name
                    })
                    edges.append({
                        "source": f"s3_{bucket_name}",
                        "target": "aws_account",
                        "relationship": "PART_OF_ACCOUNT"
                    })

        except Exception:
            pass

        return {
            "architecture": "\n".join(tree),
            "nodes": nodes,
            "edges": edges
        }
