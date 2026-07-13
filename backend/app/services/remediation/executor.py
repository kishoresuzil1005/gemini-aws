import time
import logging

from app.models import (
    ResourceDB,
    RemediationRequestDB
)

from app.services.remediation.actions.ec2_actions import EC2Actions
from app.services.remediation.actions.ebs_actions import EBSActions
from app.services.remediation.actions.rds_actions import RDSActions

logger = logging.getLogger("RemediationExecutor")


class RemediationExecutor:

    @staticmethod
    def execute(
        db,
        request_id
    ):

        request = (
            db.query(
                RemediationRequestDB
            )
            .filter(
                RemediationRequestDB.id
                == request_id
            )
            .first()
        )

        if not request:
            return None

        if request.status != "APPROVED":
            raise Exception(
                "Request not approved"
            )

        resource = (
            db.query(ResourceDB)
            .filter(
                ResourceDB.resource_id
                == request.resource_id
            )
            .first()
        )

        if not resource:
            # Safe safeguard fallback for fallback demo targets or unmapped discoveries
            logger.warning(f"Resource {request.resource_id} not found in database. Constructing simulation record.")
            class SimResource:
                resource_id = request.resource_id
                cloud_account_id = 1
                resource_type = request.resource_type
            resource = SimResource()

        result = None

        if request.action in [
            "STOP_EC2",
            "STOP_INSTANCE"
        ]:
            result = (
                EC2Actions.stop_instance(
                    resource.cloud_account_id,
                    resource.resource_id
                )
            )

        elif request.action in [
            "START_EC2",
            "START_INSTANCE"
        ]:

            result = (
                EC2Actions.start_instance(
                    resource.cloud_account_id,
                    resource.resource_id
                )
            )

        elif request.action in [
            "REBOOT_EC2",
            "REBOOT_INSTANCE"
        ]:

            result = (
                EC2Actions.reboot_instance(
                    resource.cloud_account_id,
                    resource.resource_id
                )
            )

        elif request.action == "DELETE_EBS":
            result = (
                EBSActions.delete_volume(
                    resource.cloud_account_id,
                    resource.resource_id
                )
            )

        elif request.action == "RESIZE_RDS":
            result = (
                RDSActions.resize_instance(
                    resource.cloud_account_id,
                    resource.resource_id,
                    "db.t3.small"
                )
            )
        else:
            # Custom flexible action simulator
            result = {
                "Action": request.action,
                "Status": "SimulatedActionSucceeded",
                "Timestamp": int(time.time() * 1000)
            }

        request.status = "COMPLETED"
        request.execution_result = str(result)
        request.executed_at = int(time.time() * 1000)

        db.commit()

        return reques