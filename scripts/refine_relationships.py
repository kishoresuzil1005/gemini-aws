import re

with open("backend/app/services/graph/aws_relationship_builder.py", "r") as f:
    text = f.read()

# Replace the target_group_to_task method
start_idx = text.find("    def target_group_to_task")
end_idx = text.find("    def ecs_task_to_task_definition", start_idx)

new_method = """    def target_group_to_task(self) -> list[dict]:
        def collect(ecs, region):
            import boto3
            rels = []
            try:
                elbv2 = boto3.client("elbv2", region_name=region)
                ip_to_task = {}
                for cluster_page in ecs.get_paginator("list_clusters").paginate():
                    for cluster_arn in cluster_page.get("clusterArns", []):
                        for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                            tasks = task_page.get("taskArns", [])
                            if tasks:
                                for i in range(0, len(tasks), 100):
                                    chunk = tasks[i:i+100]
                                    try:
                                        task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                        for task in task_resp.get("tasks", []):
                                            task_arn = task["taskArn"]
                                            for att in task.get("attachments", []):
                                                if att.get("type") == "ElasticNetworkInterface":
                                                    for kv in att.get("details", []):
                                                        if kv.get("name") == "privateIPv4Address":
                                                            ip_to_task[kv.get("value")] = task_arn
                                    except Exception:
                                        pass

                for tg_page in elbv2.get_paginator("describe_target_groups").paginate():
                    for tg in tg_page.get("TargetGroups", []):
                        tg_arn = tg["TargetGroupArn"]
                        try:
                            health_resp = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                            for th in health_resp.get("TargetHealthDescriptions", []):
                                target_id = th["Target"]["Id"]
                                if target_id in ip_to_task:
                                    rels.append(self.relationship(tg_arn, ip_to_task[target_id], self.TARGETS_TASK, "TargetGroup", "ECSTask"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("ecs", collect)

"""

text = text[:start_idx] + new_method + text[end_idx:]

with open("backend/app/services/graph/aws_relationship_builder.py", "w") as f:
    f.write(text)

print("Relationships refined")
