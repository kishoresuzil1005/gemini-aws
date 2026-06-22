from app.services.ai.subnet_inventory import SubnetInventoryService


class SubnetService:

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        # ----------------------------------
        # SUBNET COUNT
        # ----------------------------------

        if (
            "how many" in message
            and "subnet" in message
        ):
            subnets = (
                SubnetInventoryService
                .get_all_subnets()
            )

            return {
                "success": True,
                "response":
                    f"You currently have "
                    f"{len(subnets)} "
                    f"subnets."
            }

        # ----------------------------------
        # SUBNETS BY REGION
        # ----------------------------------

        if (
            "subnet" in message
            and "us-east-1" in message
        ):
            subnets = [
                s for s in
                SubnetInventoryService.get_all_subnets()
                if s["region"] == "us-east-1"
            ]

            return {
                "success": True,
                "region": "us-east-1",
                "total": len(subnets),
                "subnets": subnets
            }

        # ----------------------------------
        # LIST SUBNETS
        # ----------------------------------

        if (
            "list" in message
            and "subnet" in message
        ):
            subnets = (
                SubnetInventoryService
                .get_all_subnets()
            )

            return {
                "success": True,
                "total": len(subnets),
                "subnets": subnets
            }

        return None
