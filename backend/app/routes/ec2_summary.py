from fastapi import APIRouter
from fastapi import HTTPException
import logging
<<<<<<< HEAD
from pydantic import BaseModel
=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc

from app.services.aws.ec2_summary_service import (
    EC2SummaryService
)

from app.services.aws.ec2_instances_service import (
    EC2InstancesService
)

from app.services.cache.ec2_cache import (
    EC2Cache
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["EC2"]
)


<<<<<<< HEAD
class InstanceTypeAdviceRequest(BaseModel):
    workloadType: str
    useCase: str
    priority: str
    cpuManufacturer: str


=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
@router.get("/api/ec2/summary")
def ec2_summary(
    region: str
):
<<<<<<< HEAD
    try:
=======
    """
    EC2 Summary API

    Example:

    /api/ec2/summary?region=ap-south-1
    """

    try:

>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
        cached = EC2Cache.get_summary(
            region
        )

        if cached:
<<<<<<< HEAD
            logger.info(
                f"[EC2 CACHE HIT] {region}"
            )
=======

            logger.info(
                f"[EC2 CACHE HIT] {region}"
            )

>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
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
<<<<<<< HEAD
        raise
    except Exception as e:
        logger.exception(
            f"EC2 Summary Error ({region})"
        )
=======

        raise

    except Exception as e:

        logger.exception(
            f"EC2 Summary Error ({region})"
        )

>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/api/ec2/instances")
def ec2_instances(
    region: str
):
<<<<<<< HEAD
    try:
        service = EC2InstancesService(
            region
        )
        return service.get_instances()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"EC2 Instances Error ({region})"
        )
=======

    try:

        service = EC2InstancesService(
            region
        )

        return service.get_instances()

    except HTTPException:

        raise

    except Exception as e:

        logger.exception(
            f"EC2 Instances Error ({region})"
        )

>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

<<<<<<< HEAD

@router.get("/api/ec2/instance_types")
def ec2_instance_types(
    region: str = "ap-south-1"
):
    try:
        service = EC2SummaryService(region)
        return service.get_instance_types()
    except Exception as e:
        logger.exception("Error fetching instance types")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/api/ec2/instance_types/advice")
def ec2_instance_types_advice(
    payload: InstanceTypeAdviceRequest,
    region: str = "ap-south-1"
):
    try:
        service = EC2SummaryService(region)
        return service.get_instance_type_advice(
            workload_type=payload.workloadType,
            use_case=payload.useCase,
            priority=payload.priority,
            cpu_manufacturer=payload.cpuManufacturer
        )
    except Exception as e:
        logger.exception("Error generating instance type advice")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
