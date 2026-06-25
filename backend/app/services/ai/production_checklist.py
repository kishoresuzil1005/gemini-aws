from app.services.ai.production_review import ProductionReviewService


class ProductionChecklistService:

    def __init__(self):
        self.review_service = ProductionReviewService()

    def checklist(self):

        review = self.review_service.review()

        checklist = [

            {
                "category": "Networking",
                "item": "VPC Configured",
                "status": True
            },

            {
                "category": "Networking",
                "item": "Private Subnets",
                "status": True
            },

            {
                "category": "High Availability",
                "item": "Multi-AZ Deployment",
                "status": False
            },

            {
                "category": "Security",
                "item": "IAM Least Privilege",
                "status": True
            },

            {
                "category": "Security",
                "item": "Security Groups Reviewed",
                "status": True
            },

            {
                "category": "Security",
                "item": "CloudTrail Enabled",
                "status": True
            },

            {
                "category": "Monitoring",
                "item": "CloudWatch Monitoring",
                "status": True
            },

            {
                "category": "Backup",
                "item": "Automated Backups",
                "status": False
            },

            {
                "category": "Disaster Recovery",
                "item": "Recovery Plan",
                "status": False
            },

            {
                "category": "Cost",
                "item": "Compute Optimizer Reviewed",
                "status": False
            }

        ]

        passed = sum(1 for item in checklist if item["status"])
        failed = len(checklist) - passed

        return {

            "overall_status": review["overall_status"],

            "passed": passed,

            "failed": failed,

            "checklist": checklist

        }
