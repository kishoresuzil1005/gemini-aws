from app.database import (
    RemediationRequestDB
)


class ApprovalService:

    @staticmethod
    def approve(
        db,
        request_id
    ):

        request = (
            db.query(
                RemediationRequestDB
            )
            .filter(
                RemediationRequestDB.id ==
                request_id
            )
            .first()
        )

        if not request:
            return None

        request.status = "APPROVED"

        db.commit()

        return request
