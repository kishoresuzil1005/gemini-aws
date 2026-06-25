import boto3

class IAMDiscovery:
    @staticmethod
    def discover():
        try:
            client = boto3.client("iam")
            response = client.list_users()
            users = []
            for u in response.get("Users", []):
                users.append({
                    "resource_id": u["UserName"],
                    "resource_type": "IAM_USER",
                    "created": str(u.get("CreateDate")),
                    "user_id": u.get("UserId")
                })
            return users
        except Exception:
            return []
