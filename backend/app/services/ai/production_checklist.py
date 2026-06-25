from typing import Dict, Any, List

class ProductionChecklist:
    def __init__(self):
        pass

    def generate(self, inventory: Dict[str, Any], findings: Dict[str, List[str]], scoring: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a comprehensive PASS/FAIL production deployment checklist
        and an implementation roadmap based on discovered infrastructure.
        """
        
        passed = 0
        failed = 0
        warnings = 0
        
        categories = {
            "security": [],
            "networking": [],
            "database": [],
            "monitoring": [],
            "compute": [],
            "backup": []
        }
        
        critical_items = []
        implementation_order = []
        
        # Helper to add items
        def add_item(cat: str, item_name: str, status: str, priority: str, desc: str, resource: str):
            nonlocal passed, failed, warnings
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
                if priority in ["CRITICAL", "HIGH"]:
                    critical_items.append(desc)
                    implementation_order.append(desc)
            elif status == "WARNING":
                warnings += 1
                
            categories[cat].append({
                "category": cat.capitalize(),
                "item": item_name,
                "status": status,
                "priority": priority,
                "description": desc,
                "resource": resource
            })

        # Security
        sec_findings = findings.get("security_findings", [])
        if any("CloudTrail" in f for f in sec_findings):
            add_item("security", "CloudTrail Enabled", "FAIL", "CRITICAL", "CloudTrail is not enabled.", "CloudTrail")
        else:
            add_item("security", "CloudTrail Enabled", "PASS", "CRITICAL", "Audit logging enabled globally.", "CloudTrail")
            
        if any("S3" in f for f in sec_findings):
            add_item("security", "S3 Default Encryption", "FAIL", "HIGH", "S3 buckets lack encryption.", "S3")
        else:
            add_item("security", "S3 Default Encryption", "PASS", "HIGH", "S3 buckets are encrypted.", "S3")

        # Database
        if inventory.get("rds", 0) > 0:
            if not inventory.get("multi_az_rds", False):
                add_item("database", "Multi-AZ RDS", "FAIL", "CRITICAL", "RDS Multi-AZ is not configured.", "RDS")
            else:
                add_item("database", "Multi-AZ RDS", "PASS", "CRITICAL", "RDS is deployed across Multi-AZ.", "RDS")
        
        # Compute
        if inventory.get("ec2", 0) > 0:
            if inventory.get("auto_scaling", 0) == 0:
                add_item("compute", "Auto Scaling", "FAIL", "HIGH", "Auto Scaling Group is missing.", "EC2")
            else:
                add_item("compute", "Auto Scaling", "PASS", "HIGH", "Workloads are managed by ASG.", "EC2")
                
        # Backup
        rel_findings = findings.get("reliability_findings", [])
        if inventory.get("backup_plans", 0) == 0:
            add_item("backup", "AWS Backup", "FAIL", "CRITICAL", "AWS Backup is missing.", "AWS Backup")
        else:
            add_item("backup", "AWS Backup", "PASS", "CRITICAL", "AWS Backup plans exist.", "AWS Backup")

        # Monitoring
        mon_findings = findings.get("monitoring_findings", [])
        if any("CloudWatch" in f for f in mon_findings):
            add_item("monitoring", "CloudWatch Alarms", "WARNING", "MEDIUM", "CloudWatch Alarms missing.", "CloudWatch")
            implementation_order.append("Configure CloudWatch Alarms")
        else:
            add_item("monitoring", "CloudWatch Alarms", "PASS", "MEDIUM", "CloudWatch Alarms configured.", "CloudWatch")

        total_checks = passed + failed + warnings
        score = int((passed / total_checks) * 100) if total_checks > 0 else 0
        
        if score >= 90:
            grade = "A"
            production_ready = True
        elif score >= 80:
            grade = "B"
            production_ready = False
        elif score >= 60:
            grade = "C"
            production_ready = False
        else:
            grade = "D"
            production_ready = False

        return {
            "environment": "Production",
            "production_ready": production_ready,
            "overall_score": score,
            "grade": grade,
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total_checks": total_checks
            },
            "categories": categories,
            "critical_items": critical_items,
            "implementation_order": implementation_order
        }
