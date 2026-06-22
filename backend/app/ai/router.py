from app.ai.intents import Intent


class IntentRouter:

    @staticmethod
    def classify(message: str):

        msg = message.lower()


        # PUBLIC EXPOSURE

        if any(
            x in msg
            for x in [
                "public instance",
                "public instances",
                "public ip",
                "internet facing",
                "publicly exposed instance",
                "publicly exposed instances",
                "internet facing server",
                "internet facing servers",
                "exposed workloads",
                "public workloads"
            ]
        ) or (
            "instance" in msg
            and (
                "public" in msg
                or "internet facing" in msg
                or "exposed" in msg
            )
        ):
            return Intent.PUBLIC_EXPOSURE


        # SECURITY AUDIT

        if any(
            x in msg
            for x in [
                "risky security group",
                "dangerous security group",
                "internet exposed",
                "security groups expose",
                "expose ssh",
                "expose mysql",
                "expose postgresql",
                "open ssh",
                "open mysql",
                "open postgresql",
                "public security groups",
                "security findings",
                "0.0.0.0/0",
                "publicly exposed",
                "open port"
            ]
        ):
            return Intent.SECURITY_AUDIT


        # SECURITY GROUP

        if any(
            x in msg
            for x in [
                "security group",
                "sg-",
                "network security"
            ]
        ):
            return Intent.SECURITY_GROUP


        # SUBNET

        if "subnet" in msg:
            return Intent.SUBNET


        # VPC

        if "vpc" in msg:
            return Intent.VPC


        # S3

        if (
            "bucket" in msg
            or "s3" in msg
        ):
            return Intent.S3


        # RDS

        if (
            "rds" in msg
            or "database" in msg
        ):
            return Intent.RDS


        # EC2

        if (
            "instance" in msg
            or "ec2" in msg
            or "server" in msg
        ):
            return Intent.EC2


        return Intent.UNKNOWN
