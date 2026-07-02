from typing import Dict, List

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.resource import ResourceDB


class MetadataRetriever:

    def __init__(self):

        self.db: Session = SessionLocal()

    def close(self):

        self.db.close()

    def get_resource(
        self,
        resource_id: str
    ) -> Dict:

        resource = (
            self.db.query(ResourceDB)
            .filter(ResourceDB.resource_id == resource_id)
            .first()
        )

        if not resource:
            return {}

        return {
            "resource_id": resource.resource_id,
            "name": resource.name,
            "resource_type": resource.resource_type,
            "region": resource.region,
            "account_id": resource.account_id,
            "arn": resource.arn,
            "state": resource.state,
            "metadata": resource.metadata_json or {}
        }

    def get_resources_by_type(
        self,
        resource_type: str
    ) -> List[Dict]:

        resources = (
            self.db.query(ResourceDB)
            .filter(ResourceDB.resource_type == resource_type)
            .all()
        )

        return [
            {
                "resource_id": r.resource_id,
                "name": r.name,
                "region": r.region,
                "state": r.state,
                "metadata": r.metadata_json or {}
            }
            for r in resources
        ]

    def get_resources_by_region(
        self,
        region: str
    ) -> List[Dict]:

        resources = (
            self.db.query(ResourceDB)
            .filter(ResourceDB.region == region)
            .all()
        )

        return [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type,
                "name": r.name,
                "state": r.state
            }
            for r in resources
        ]

    def get_resources_by_account(
        self,
        account_id: str
    ) -> List[Dict]:

        resources = (
            self.db.query(ResourceDB)
            .filter(ResourceDB.account_id == account_id)
            .all()
        )

        return [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type,
                "name": r.name
            }
            for r in resources
        ]

    def find_by_tag(
        self,
        key: str,
        value: str
    ) -> List[Dict]:

        resources = self.db.query(ResourceDB).all()

        matches = []

        for r in resources:

            metadata = r.metadata_json or {}

            tags = metadata.get("Tags", [])

            for tag in tags:

                if (
                    tag.get("Key") == key
                    and tag.get("Value") == value
                ):
                    matches.append(
                        {
                            "resource_id": r.resource_id,
                            "resource_type": r.resource_type,
                            "name": r.name
                        }
                    )

        return matches
