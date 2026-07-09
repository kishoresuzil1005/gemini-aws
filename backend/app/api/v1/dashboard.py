from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(region: str | None = None):

    params = {}

    if region:
        filter_sql = "WHERE region = :region"
        params["region"] = region
    else:
        filter_sql = ""

    with engine.connect() as conn:

        # Total Resources
        total_resources = conn.execute(
            text(f"""
                SELECT COUNT(*)
                FROM resources
                {filter_sql}
            """),
            params
        ).scalar() or 0

        # Service Breakdown
        service_rows = conn.execute(
            text(f"""
                SELECT
                    resource_type,
                    COUNT(*) as total
                FROM resources
                {filter_sql}
                GROUP BY resource_type
            """),
            params
        ).fetchall()

        services = {}

        for row in service_rows:
            services[row[0]] = row[1]

        # Running Resources
        running_resources = conn.execute(
            text(f"""
                SELECT COUNT(*)
                FROM resources
                {filter_sql}
                {"AND" if region else "WHERE"}
                status IN (
                    'running',
                    'active',
                    'available'
                )
            """),
            params
        ).scalar() or 0

        # Stopped Resources
        stopped_resources = conn.execute(
            text(f"""
                SELECT COUNT(*)
                FROM resources
                {filter_sql}
                {"AND" if region else "WHERE"}
                status IN (
                    'stopped',
                    'terminated'
                )
            """),
            params
        ).scalar() or 0

        # Regions Count
        region_count = conn.execute(
            text("""
                SELECT COUNT(
                    DISTINCT region
                )
                FROM resources
                WHERE region IS NOT NULL
            """)
        ).scalar() or 0

        # Providers Count
        provider_count = conn.execute(
            text("""
                SELECT COUNT(
                    DISTINCT provider
                )
                FROM resources
            """)
        ).scalar() or 0

    return {
        "region": region,
        "total_resources": total_resources,
        "running_resources": running_resources,
        "stopped_resources": stopped_resources,
        "region_count": region_count,
        "provider_count": provider_count,

        "ec2": services.get("EC2", 0),
        "s3": services.get("S3", 0),
        "rds": services.get("RDS", 0),
        "lambda": services.get("Lambda", 0),
        "vpc": services.get("VPC", 0),
        "iam": services.get("IAM", 0),
        "ebs": services.get("EBS", 0),

        "service_breakdown": services
    }
