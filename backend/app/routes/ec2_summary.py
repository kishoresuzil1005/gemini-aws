from fastapi import APIRouter
from fastapi import HTTPException
import logging

from app.services.aws.ec2_summary_service import (
    EC2SummaryService
)

from app.services.cache.ec2_cache import (
    EC2Cache
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["EC2"]
)


@router.get("/api/ec2/summary")
def ec2_summary(
    region: str
):
    """
    EC2 Summary API

    Example:

    /api/ec2/summary?region=ap-south-1
    """

    try:

        cached = EC2Cache.get_summary(
            region
        )

        if cached:

            logger.info(
                f"[EC2 CACHE HIT] {region}"
            )

            return cached

        logger.info(
            f"[EC2 CACHE MISS] {region}"
        )

        service = EC2SummaryService(
            region
        )

        data = service.get_summary()

        EC2Cache.set_summary(
            region,
            data
        )

        return data

    except HTTPException:

        raise

    except Exception as e:

        logger.exception(
            f"EC2 Summary Error ({region})"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
