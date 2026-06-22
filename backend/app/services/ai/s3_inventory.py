import boto3


class S3InventoryService:

    @staticmethod
    def get_all_buckets():

        s3 = boto3.client("s3")

        response = s3.list_buckets()

        buckets = []

        for bucket in response["Buckets"]:

            bucket_name = bucket["Name"]

            try:

                location = (
                    s3.get_bucket_location(
                        Bucket=bucket_name
                    )
                )

                region = (
                    location.get(
                        "LocationConstraint"
                    )
                    or "us-east-1"
                )

            except Exception:

                region = "unknown"

            buckets.append({

                "bucket_name":
                    bucket_name,

                "region":
                    region,

                "creation_date":
                    str(
                        bucket["CreationDate"]
                    )
            })

        return buckets
