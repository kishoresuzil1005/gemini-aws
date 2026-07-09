import re

with open("backend/app/services/graph/aws_relationship_builder.py", "r") as f:
    text = f.read()

# Replace constants
text = text.replace('RUNS_TASK = "RUNS_TASK"', 'RUNS_TASK = "RUNS_TASK"\n    TARGETS_TASK = "TARGETS_TASK"\n    HAS_CONTAINER = "HAS_CONTAINER"\n    USES_CAPACITY_PROVIDER = "USES_CAPACITY_PROVIDER"')

# Replace ecs_service_to_task
old_svc_to_task = 'self.relationship(svc_arn, task_arn, self.RUNS_TASK, "ECSService", "ECSTask")'
text = text.replace(old_svc_to_task, 'self.relationship(svc_arn, task_arn, self.HAS_TASK, "ECSService", "ECSTask")')

# Remove target_group_to_ecs_service
start_tg_svc = text.find("def target_group_to_ecs_service")
if start_tg_svc != -1:
    end_tg_svc = text.find("    def ", start_tg_svc + 1)
    if end_tg_svc == -1: end_tg_svc = len(text)
    text = text[:start_tg_svc] + text[end_tg_svc:]

# Replace builders array registration
text = text.replace("self.target_group_to_ecs_service,", "self.target_group_to_task,\n            self.ecs_task_to_task_definition,\n            self.ecs_task_to_container,")

# Add new methods at the end
new_methods = """
    def target_group_to_task(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for svc_page in ecs.get_paginator("list_services").paginate(cluster=cluster_arn):
                        services = svc_page.get("serviceArns", [])
                        if services:
                            for i in range(0, len(services), 10):
                                chunk = services[i:i+10]
                                try:
                                    svc_resp = ecs.describe_services(cluster=cluster_arn, services=chunk)
                                    for svc in svc_resp.get("services", []):
                                        tgs = [lb.get("targetGroupArn") for lb in svc.get("loadBalancers", []) if lb.get("targetGroupArn")]
                                        if not tgs:
                                            continue
                                        svc_name = svc["serviceName"]
                                        for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn, serviceName=svc_name):
                                            for task_arn in task_page.get("taskArns", []):
                                                for tg_arn in tgs:
                                                    rels.append(self.relationship(tg_arn, task_arn, self.TARGETS_TASK, "TargetGroup", "ECSTask"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_task_definition(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
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
                                        td_arn = task.get("taskDefinitionArn")
                                        if td_arn:
                                            rels.append(self.relationship(task_arn, td_arn, self.USES_TASK_DEFINITION, "ECSTask", "ECSTaskDefinition"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_container(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
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
                                        for container in task.get("containers", []):
                                            c_arn = container.get("containerArn")
                                            if c_arn:
                                                rels.append(self.relationship(task_arn, c_arn, self.HAS_CONTAINER, "ECSTask", "ECSContainer"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)
"""
text = text + new_methods

with open("backend/app/services/graph/aws_relationship_builder.py", "w") as f:
    f.write(text)

print("Injected Phase 3 relationships")
