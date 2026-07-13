import logging
from app.providers.aws.auth import get_aws_client

logger = logging.getLogger("RDSActions")


class RDSActions:

    @staticmethod
    def resize_instance(
        account_id,
        db_id,
        new_class
    ):
        try:
            rds = get_aws_client(
                "rds",
                account_id or 1
            )

            return rds.modify_db_instance(
                DBInstanceIdentifier=db_id,
                DBInstanceClass=new_class,
                ApplyImmediately=True
            )
        except Exception as e:
            logger.warning(f"Live AWS modify_db_instance failed: {e}. Executing simulated resize.")
            return {
                "DBInstance": {
                    "DBInstanceIdentifier": db_id,
                    "DBInstanceClass": new_class,
                    "PendingModifiedValues": {
                        "DBInstanceClass": new_class
                    }
                },
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "Simulation": True
                }
            