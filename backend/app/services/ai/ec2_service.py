from app.services.ai.inventory_ai import InventoryAIService


class EC2Service:

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        if "ec2" in message and (
            "how many" in message
            or "count" in message
        ):
            instances = (
                InventoryAIService
                .get_all_ec2_instances()
            )

            running = len([
                x for x in instances
                if x["state"] == "running"
            ])

            stopped = len([
                x for x in instances
                if x["state"] == "stopped"
            ])

            return {
                "success": True,
                "response":
                    f"You currently have "
                    f"{len(instances)} EC2 instances. "
                    f"{running} are running and "
                    f"{stopped} are stopped."
            }

        if (
            "running" in message
            and "instance" in message
        ):
            instances = (
                InventoryAIService
                .get_all_ec2_instances()
            )

            running = [
                i
                for i in instances
                if i["state"] == "running"
            ]

            return {
                "success": True,
                "total": len(running),
                "instances": running
            }

        if (
            "stopped" in message
            and "instance" in message
        ):
            instances = (
                InventoryAIService
                .get_all_ec2_instances()
            )

            stopped = [
                i
                for i in instances
                if i["state"] == "stopped"
            ]

            return {
                "success": True,
                "total": len(stopped),
                "instances": stopped
            }

        if (
            "list" in message
            and "ec2" in message
        ):
            instances = (
                InventoryAIService
                .get_all_ec2_instances()
            )

            return {
                "success": True,
                "total": len(instances),
                "instances": instances
            }

        if (
            "show" in message
            and "instance" in message
        ):
            instances = (
                InventoryAIService
                .get_all_ec2_instances()
            )

            return {
                "success": True,
                "instances": instances
            }

        return None
