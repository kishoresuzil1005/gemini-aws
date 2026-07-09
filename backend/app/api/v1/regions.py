from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(
    prefix="/api/v1/regions",
    tags=["Regions"]
)

@router.get("")
def get_regions():

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT DISTINCT region
                FROM resources
                WHERE region IS NOT NULL
                ORDER BY region
            """)
        ).fetchall()

    return [
        row[0]
        for row in rows
    ]
