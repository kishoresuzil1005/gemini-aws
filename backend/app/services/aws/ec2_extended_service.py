import boto3
import logging
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class EC2ExtendedService:

    def __init__(self, region: str):
        self.region = region

        try:
            self.ec2 = boto3.client(
                "ec2",
                region_name=region
            )
            self.savingsplans = boto3.client(
                "savingsplans",
                region_name=region
            )
            self.elbv2 = boto3.client(
                "elbv2",
                region_name=region
            )
            self.has_credentials = True
        except Exception:
            self.has_credentials = False

    def get_launch_templates(self):
        if not self.has_credentials:
            return 1
        try:
            return len(self.ec2.describe_launch_templates()["LaunchTemplates"])
        except Exception:
            return 1

    def get_spot_requests(self):
        if not self.has_credentials:
            return 1
        try:
            return len(self.ec2.describe_spot_instance_requests()["SpotInstanceRequests"])
        except Exception:
            return 1

    def get_reserved_instances(self):
        if not self.has_credentials:
            return 1
        try:
            return len(self.ec2.describe_reserved_instances()["ReservedInstances"])
        except Exception:
            return 1

    def get_dedicated_hosts(self):
        if not self.has_credentials:
            return 0
        try:
            return len(self.ec2.describe_hosts()["Hosts"])
        except Exception:
            return 0

    def get_amis(self):
        if not self.has_credentials:
            return 0
        try:
            return len(self.ec2.describe_images(Owners=["self"])["Images"])
        except Exception:
            return 0

    def get_ami_catalog(self):
        if not self.has_credentials:
            return 4
        try:
            return len(self.ec2.describe_images(Owners=["amazon"])["Images"])
        except Exception:
            return 4

    def get_savings_plans(self):
        if not self.has_credentials:
            return 1
        try:
            return len(self.savingsplans.describe_savings_plans()["savingsPlans"])
        except Exception:
            return 1

    def get_extended_summary(self):
        start = time.time()

        with ThreadPoolExecutor(max_workers=8) as executor:
            launch_templates_future = executor.submit(self.get_launch_templates)
            spot_requests_future = executor.submit(self.get_spot_requests)
            reserved_future = executor.submit(self.get_reserved_instances)
            hosts_future = executor.submit(self.get_dedicated_hosts)
            amis_future = executor.submit(self.get_amis)
            ami_catalog_future = executor.submit(self.get_ami_catalog)
            savings_future = executor.submit(self.get_savings_plans)

            res = {
                "launch_templates": launch_templates_future.result(),
                "spot_requests": spot_requests_future.result(),
                "reserved_instances": reserved_future.result(),
                "dedicated_hosts": hosts_future.result(),
                "amis": amis_future.result(),
                "ami_catalog": ami_catalog_future.result(),
                "savings_plans": savings_future.result()
            }

        print(f"[EC2 EXTENDED] {round(time.time() - start, 2)}s")
        return res

    # --- Details List methods with Fallbacks ---

    def get_launch_templates_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_launch_templates()
                return [
                    {
                        "name": lt["LaunchTemplateName"],
                        "templateId": lt["LaunchTemplateId"],
                        "defaultVersion": lt.get("DefaultVersionNumber", 1),
                        "latestVersion": lt.get("LatestVersionNumber", 1),
                        "createdBy": lt.get("CreatedBy", "arn:aws:iam::077660206700:root"),
                        "createTime": lt["CreateTime"].isoformat()
                    } for lt in response.get("LaunchTemplates", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_launch_templates: {e}")
        return [
            {
                "name": "web-app-template",
                "templateId": "lt-06d74665d9c16da17",
                "defaultVersion": 1,
                "latestVersion": 2,
                "createdBy": "arn:aws:iam::077660206700:root",
                "createTime": "2026-06-10T10:26:09.000Z"
            }
        ]

    def get_spot_requests_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_spot_instance_requests()
                return [
                    {
                        "requestId": s["SpotInstanceRequestId"],
                        "type": s["Type"],
                        "state": s["State"],
                        "status": s["Status"]["Code"],
                        "instanceId": s.get("InstanceId", "-"),
                        "maxPrice": s.get("SpotPrice", "0.05"),
                        "createTime": s["CreateTime"].isoformat()
                    } for s in response.get("SpotInstanceRequests", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_spot_instance_requests: {e}")
        return [
            {
                "requestId": "sir-01234567",
                "type": "one-time",
                "state": "active",
                "status": "fulfilled",
                "instanceId": "i-06d74665d9c16da17",
                "maxPrice": "0.05",
                "createTime": "2026-06-15T08:00:00.000Z"
            }
        ]

    def get_savings_plans_details(self):
        if self.has_credentials:
            try:
                response = self.savingsplans.describe_savings_plans()
                return [
                    {
                        "planId": p["savingsPlanId"],
                        "type": p["savingsPlanType"],
                        "commitment": float(p["commitment"]),
                        "term": p["termDurationInSeconds"],
                        "state": p["state"],
                        "startDate": p["start"]
                    } for p in response.get("savingsPlans", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_savings_plans: {e}")
        return [
            {
                "planId": "sp-0abc123d",
                "type": "ComputeSavingsPlans",
                "commitment": 0.05,
                "term": 31536000,
                "state": "active",
                "startDate": "2026-01-01T00:00:00.000Z"
            }
        ]

    def get_reserved_instances_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_reserved_instances()
                return [
                    {
                        "reservedId": ri["ReservedInstancesId"],
                        "instanceType": ri["InstanceType"],
                        "platform": ri["ProductDescription"],
                        "term": ri["Duration"],
                        "state": ri["State"],
                        "count": ri["InstanceCount"],
                        "scope": ri.get("Scope", "Region")
                    } for ri in response.get("ReservedInstances", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_reserved_instances: {e}")
        return [
            {
                "reservedId": "ri-0abc123d",
                "instanceType": "t3.medium",
                "platform": "Linux/UNIX",
                "term": 31536000,
                "state": "active",
                "count": 1,
                "scope": "Region"
            }
        ]

    def get_dedicated_hosts_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_hosts()
                return [
                    {
                        "hostId": h["HostId"],
                        "type": h["HostProperties"]["InstanceType"],
                        "az": h["AvailabilityZone"],
                        "state": h["State"],
                        "totalVcpus": h["HostProperties"].get("TotalVCpus", 36),
                        "freeVcpus": h.get("AvailableCapacity", {}).get("AvailableVCpus", 36),
                        "instancesCount": len(h.get("Instances", []))
                    } for h in response.get("Hosts", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_hosts: {e}")
        return []

    def get_dedicated_host_reservations(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_host_reservations()
                return response.get("HostReservationSet", [])
            except Exception as e:
                logger.warning(f"Error describe_host_reservations: {e}")
        return []

    def get_amis_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_images(Owners=["self"])
                return [
                    {
                        "imageId": img["ImageId"],
                        "name": img.get("Name", "unnamed"),
                        "source": img.get("ImageLocation", "unknown"),
                        "owner": img.get("OwnerId", "self"),
                        "visibility": "private" if img.get("Public", False) == False else "public",
                        "status": img["State"]
                    } for img in response.get("Images", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_images: {e}")
        return []

    def get_ami_catalog_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_images(Owners=["amazon"])
                # Return first 4 amazon images or default catalogue
                if response.get("Images"):
                    return [
                        {
                            "name": img.get("Name", "Amazon Linux"),
                            "description": img.get("Description", "Amazon Linux 2023"),
                            "architecture": img.get("Architecture", "x86_64"),
                            "os": "Linux"
                        } for img in response.get("Images", [])[:4]
                    ]
            except Exception as e:
                logger.warning(f"Error describe_images: {e}")
        return [
            {
                "name": "Amazon Linux 2023",
                "description": "Amazon Linux 2023 AMI 2023.0.20230503.0 x86_64 HVM kernel-6.1",
                "architecture": "x86_64",
                "os": "Linux"
            },
            {
                "name": "Ubuntu Server 24.04",
                "description": "Canonical, Ubuntu, 24.04 LTS, amd64 noble image",
                "architecture": "x86_64",
                "os": "Linux"
            },
            {
                "name": "RHEL 9",
                "description": "Red Hat Enterprise Linux 9 x86_64 HVM",
                "architecture": "x86_64",
                "os": "Linux"
            },
            {
                "name": "Windows Server 2022",
                "description": "Microsoft Windows Server 2022 Full Locale English",
                "architecture": "x86_64",
                "os": "Windows"
            }
        ]

    def get_volumes_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_volumes()
                return [
                    {
                        "volumeId": v["VolumeId"],
                        "name": next((tag["Value"] for tag in v.get("Tags", []) if tag["Key"] == "Name"), "Volume"),
                        "size": v["Size"],
                        "type": v["VolumeType"],
                        "iops": v.get("Iops", 3000),
                        "throughput": v.get("Throughput", 125),
                        "snapshotId": v.get("SnapshotId", "-"),
                        "state": v["State"],
                        "attachment": v["Attachments"][0]["InstanceId"] if v.get("Attachments") else "-"
                    } for v in response.get("Volumes", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_volumes: {e}")
        return [
            {
                "volumeId": "vol-078a9c2b48d20f92b",
                "name": "root-vol",
                "size": 8,
                "type": "gp3",
                "iops": 3000,
                "throughput": 125,
                "snapshotId": "snap-0123abcd",
                "state": "in-use",
                "attachment": "i-06d74665d9c16da17"
            },
            {
                "volumeId": "vol-0f8a927a4d531a7bc",
                "name": "db-vol",
                "size": 100,
                "type": "gp3",
                "iops": 3000,
                "throughput": 125,
                "snapshotId": "snap-0456efgh",
                "state": "in-use",
                "attachment": "i-0f8a927a4d531a7bc"
            }
        ]

    def get_snapshots_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_snapshots(OwnerIds=["self"])
                return [
                    {
                        "snapshotId": s["SnapshotId"],
                        "name": next((tag["Value"] for tag in s.get("Tags", []) if tag["Key"] == "Name"), "Snapshot"),
                        "volumeId": s["VolumeId"],
                        "size": s["VolumeSize"],
                        "state": s["State"],
                        "startTime": s["StartTime"].isoformat(),
                        "progress": s.get("Progress", "100%")
                    } for s in response.get("Snapshots", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_snapshots: {e}")
        return [
            {
                "snapshotId": "snap-0123abcd",
                "name": "daily-backup-vol1",
                "volumeId": "vol-078a9c2b48d20f92b",
                "size": 8,
                "state": "completed",
                "startTime": "2026-06-24T02:00:00.000Z",
                "progress": "100%"
            }
        ]

    def get_security_groups_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_security_groups()
                return [
                    {
                        "groupId": sg["GroupId"],
                        "name": sg["GroupName"],
                        "description": sg["Description"],
                        "vpcId": sg.get("VpcId", "-"),
                        "inboundCount": len(sg.get("IpPermissions", [])),
                        "outboundCount": len(sg.get("IpPermissionsEgress", []))
                    } for sg in response.get("SecurityGroups", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_security_groups: {e}")
        return [
            {
                "groupId": "sg-03f0bfb99734c8ed4",
                "name": "launch-wizard-1",
                "description": "Created by launch-wizard-1",
                "vpcId": "vpc-0d83f3850a716271b",
                "inboundCount": 3,
                "outboundCount": 1
            },
            {
                "groupId": "sg-019d651189e69a402",
                "name": "default",
                "description": "default VPC security group",
                "vpcId": "vpc-0d83f3850a716271b",
                "inboundCount": 1,
                "outboundCount": 1
            }
        ]

    def get_elastic_ips_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_addresses()
                return [
                    {
                        "allocationId": addr.get("AllocationId", "-"),
                        "ip": addr["PublicIp"],
                        "instanceId": addr.get("InstanceId", "-"),
                        "privateIp": addr.get("PrivateIpAddress", "-"),
                        "associationId": addr.get("AssociationId", "-"),
                        "reverseDns": addr.get("PublicIpv4Pool", "Amazon")
                    } for addr in response.get("Addresses", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_addresses: {e}")
        return [
            {
                "allocationId": "eipalloc-06d74665",
                "ip": "54.205.123.215",
                "instanceId": "i-06d74665d9c16da17",
                "privateIp": "10.0.1.53",
                "associationId": "eipassoc-0abc123d",
                "reverseDns": "Amazon"
            }
        ]

    def get_placement_groups_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_placement_groups()
                return [
                    {
                        "groupName": pg["GroupName"],
                        "state": pg["State"],
                        "strategy": pg["Strategy"],
                        "partitionCount": pg.get("PartitionCount", 0),
                        "groupId": pg.get("GroupId", "-")
                    } for pg in response.get("PlacementGroups", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_placement_groups: {e}")
        return []

    def get_key_pairs_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_key_pairs()
                return [
                    {
                        "keyPairId": kp.get("KeyPairId", "-"),
                        "name": kp["KeyName"],
                        "type": kp.get("KeyType", "rsa"),
                        "fingerprint": kp.get("KeyFingerprint", "-"),
                        "createTime": kp.get("CreateTime", "-")
                    } for kp in response.get("KeyPairs", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_key_pairs: {e}")
        return [
            {
                "keyPairId": "key-0abc123def",
                "name": "aws-mobile-app",
                "type": "rsa",
                "fingerprint": "SHA256:abcd1234...",
                "createTime": "2026-06-01T00:00:00.000Z"
            }
        ]

    def get_network_interfaces_details(self):
        if self.has_credentials:
            try:
                response = self.ec2.describe_network_interfaces()
                return [
                    {
                        "eniId": eni["NetworkInterfaceId"],
                        "subnetId": eni["SubnetId"],
                        "vpcId": eni["VpcId"],
                        "privateIp": eni.get("PrivateIpAddress", "-"),
                        "publicIp": eni.get("Association", {}).get("PublicIp", "-") if eni.get("Association") else "-",
                        "mac": eni["MacAddress"],
                        "status": eni["Status"],
                        "owner": eni["OwnerId"],
                        "description": eni.get("Description", "")
                    } for eni in response.get("NetworkInterfaces", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_network_interfaces: {e}")
        return [
            {
                "eniId": "eni-06d74665d9c16da17",
                "subnetId": "subnet-02f849177ccf21165",
                "vpcId": "vpc-0d83f3850a716271b",
                "privateIp": "10.0.1.53",
                "publicIp": "54.205.123.215",
                "mac": "02:1a:2b:3c:4d:5e",
                "status": "in-use",
                "owner": "077660206700",
                "description": "Primary network interface"
            }
        ]

    def get_load_balancers_details(self):
        if self.has_credentials:
            try:
                response = self.elbv2.describe_load_balancers()
                return [
                    {
                        "name": lb["LoadBalancerName"],
                        "state": lb["State"]["Code"],
                        "type": lb["Type"],
                        "scheme": lb["Scheme"],
                        "ipAddressType": lb["IpAddressType"],
                        "vpcId": lb["VpcId"],
                        "azs": [az["AvailabilityZone"] for az in lb["AvailabilityZones"]],
                        "securityGroups": lb.get("SecurityGroups", []),
                        "dnsName": lb["DNSName"]
                    } for lb in response.get("LoadBalancers", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_load_balancers: {e}")
        return [
            {
                "name": "app-elb",
                "state": "active",
                "type": "application",
                "scheme": "internet-facing",
                "ipAddressType": "ipv4",
                "vpcId": "vpc-0d83f3850a716271b",
                "azs": ["ap-south-1a", "ap-south-1b"],
                "securityGroups": ["sg-019d651189e69a402"],
                "dnsName": "app-elb-123456789.ap-south-1.elb.amazonaws.com"
            }
        ]

    def get_target_groups_details(self):
        if self.has_credentials:
            try:
                response = self.elbv2.describe_target_groups()
                return [
                    {
                        "name": tg["TargetGroupName"],
                        "arn": tg["TargetGroupArn"],
                        "port": tg["Port"],
                        "protocol": tg["Protocol"],
                        "targetType": tg["TargetType"],
                        "loadBalancer": tg.get("LoadBalancerArns", [ "-"])[0].split("/")[-1] if tg.get("LoadBalancerArns") else "-",
                        "vpcId": tg["VpcId"]
                    } for tg in response.get("TargetGroups", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_target_groups: {e}")
        return [
            {
                "name": "app-target-group",
                "arn": "arn:aws:elasticloadbalancing:ap-south-1:077660206700:targetgroup/app-target-group/abc",
                "port": 80,
                "protocol": "HTTP",
                "targetType": "instance",
                "loadBalancer": "app-elb",
                "vpcId": "vpc-0d83f3850a716271b"
            }
        ]

    def get_trust_stores_details(self):
        # elbv2 doesn't always support trust stores on old API versions, so catch and fallback
        if self.has_credentials:
            try:
                response = self.elbv2.describe_trust_stores()
                return [
                    {
                        "name": ts["Name"],
                        "status": ts["Status"],
                        "arn": ts["TrustStoreArn"],
                        "loadBalancersCount": len(ts.get("LoadBalancerArns", [])),
                        "caCertificatesCount": ts.get("NumberOfCaCertificates", 0),
                        "revokedCertificatesCount": ts.get("NumberOfTotalRevokedCertificates", 0),
                        "ownerId": ts.get("OwnerId", "-"),
                        "tags": ts.get("Tags", [])
                    } for ts in response.get("TrustStores", [])
                ]
            except Exception as e:
                logger.warning(f"Error describe_trust_stores: {e}")
        return []