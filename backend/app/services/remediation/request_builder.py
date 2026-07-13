from app.models import (
    RemediationRequestDB
)


class RequestBuilder:

    @staticmethod
    def create_ec2_stop(
        db,
        resource_id
    ):

        req = (
            RemediationRequestDB(

                resource_id=
                resource_id,

                resource_type=
                "EC2",

                action=
                "STOP_EC2"
            )
        )

        db.add(req)

        db.commit()

        return re