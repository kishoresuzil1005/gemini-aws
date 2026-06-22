from app.services.ai.s3_inventory import S3InventoryService


class S3Service:

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        if (
            "how many" in message
            and "bucket" in message
        ):
            buckets = (
                S3InventoryService
                .get_all_buckets()
            )

            return {
                "success": True,
                "response":
                    f"You currently have "
                    f"{len(buckets)} "
                    f"S3 buckets."
            }

        if (
            "list" in message
            and "bucket" in message
        ):
            buckets = (
                S3InventoryService
                .get_all_buckets()
            )

            return {
                "success": True,
                "total": len(buckets),
                "buckets": buckets
            }

        return None
