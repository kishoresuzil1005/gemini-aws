from app.services.ai.rds_inventory import RDSInventoryService


class RDSService:

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        if (
            "rds" in message
            and "how many" in message
        ):
            databases = (
                RDSInventoryService
                .get_all_rds()
            )

            return {
                "success": True,
                "response":
                    f"You currently have "
                    f"{len(databases)} "
                    f"RDS databases."
            }

        if (
            "list" in message
            and "rds" in message
        ):
            databases = (
                RDSInventoryService
                .get_all_rds()
            )

            return {
                "success": True,
                "total": len(databases),
                "databases": databases
            }

        if "postgres" in message:
            databases = (
                RDSInventoryService
                .get_all_rds()
            )

            postgres = [
                db
                for db in databases
                if "postgres" in db["engine"]
            ]

            return {
                "success": True,
                "total": len(postgres),
                "databases": postgres
            }

        if "mysql" in message:
            databases = (
                RDSInventoryService
                .get_all_rds()
            )

            mysql = [
                db
                for db in databases
                if "mysql" in db["engine"]
            ]

            return {
                "success": True,
                "total": len(mysql),
                "databases": mysql
            }

        return None
