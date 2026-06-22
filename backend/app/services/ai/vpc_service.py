from app.services.ai.vpc_inventory import VPCInventoryService


class VPCService:

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        if (
            "how many" in message
            and "vpc" in message
        ):
            vpcs = (
                VPCInventoryService
                .get_all_vpcs()
            )

            return {
                "success": True,
                "response":
                    f"You currently have "
                    f"{len(vpcs)} VPCs."
            }

        if (
            "list" in message
            and "vpc" in message
        ):
            vpcs = (
                VPCInventoryService
                .get_all_vpcs()
            )

            return {
                "success": True,
                "total": len(vpcs),
                "vpcs": vpcs
            }

        return None
