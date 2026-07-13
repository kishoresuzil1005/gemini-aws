import boto3

REGION_NAMES = {
    "us-east-1": ("N. Virginia", "United States"),
    "us-east-2": ("Ohio", "United States"),
    "us-west-1": ("N. California", "United States"),
    "us-west-2": ("Oregon", "United States"),

    "ap-south-1": ("Mumbai", "Asia Pacific"),
    "ap-south-2": ("Hyderabad", "Asia Pacific"),

    "ap-southeast-1": ("Singapore", "Asia Pacific"),
    "ap-southeast-2": ("Sydney", "Asia Pacific"),

    "ap-northeast-1": ("Tokyo", "Asia Pacific"),
    "ap-northeast-2": ("Seoul", "Asia Pacific"),
    "ap-northeast-3": ("Osaka", "Asia Pacific"),

    "eu-central-1": ("Frankfurt", "Europe"),
    "eu-west-1": ("Ireland", "Europe"),
    "eu-west-2": ("London", "Europe"),
    "eu-west-3": ("Paris", "Europe"),
    "eu-north-1": ("Stockholm", "Europe"),

    "ca-central-1": ("Canada Central", "Canada"),

    "sa-east-1": ("Sao Paulo", "South America")
}


from app.core.aws_logger import log_aws_call

class RegionsDashboardService:

    @staticmethod
    def get_regions():
        log_aws_call("ec2", "describe_regions", "us-east-1", "SUCCESS", "Fetch all available AWS regions")

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        regions = ec2.describe_regions()

        result = []

        for region in regions["Regions"]:

            region_code = region["RegionName"]
            log_aws_call("ec2", "describe_instances", region_code, "SUCCESS", f"Describe instances in regional cluster")

            regional_ec2 = boto3.client(
                "ec2",
                region_name=region_code
            )

            running = 0
            stopped = 0

            reservations = regional_ec2.describe_instances()

            for reservation in reservations["Reservations"]:

                for instance in reservation["Instances"]:

                    state = instance["State"]["Name"]

                    if state == "running":
                        running += 1

                    elif state == "stopped":
                        stopped += 1

            volumes = len(
                regional_ec2.describe_volumes()["Volumes"]
            )

            security_groups = len(
                regional_ec2.describe_security_groups()["SecurityGroups"]
            )

            elastic_ips = len(
                regional_ec2.describe_addresses()["Addresses"]
            )

            name, group = REGION_NAMES.get(
                region_code,
                (region_code, "Other")
            )

            result.append({

                "code": region_code,

                "name": name,

                "group": group,

                "running_instances": running,

                "stopped_instances": stopped,

                "volumes": volumes,

                "security_groups": security_groups,

                "elastic_ips": elastic_ips
            })

        return resul