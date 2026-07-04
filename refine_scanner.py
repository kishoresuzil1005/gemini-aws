import re

with open("backend/app/aws_scanner.py", "r") as f:
    text = f.read()

# Replace Task block
old_task = """                                    task_arn = task["taskArn"]
                                    if task.get("taskDefinitionArn"): task_definition_arns.add(task["taskDefinitionArn"])
                                    resources.append({
                                        "id": task_arn, "provider": "AWS", "type": "ECSTask",
                                        "name": task_arn.split("/")[-1],
                                        "configurationHint": f"LaunchType: {task.get('launchType', 'UNKNOWN')} | Status: {task.get('lastStatus')}",
                                        "costEstimate": 0.0, "dependenciesString": ""
                                    })
                                    # Containers
                                    for container in task.get("containers", []):
                                        c_name = container.get("name")
                                        c_arn = container.get("containerArn")
                                        if c_arn:
                                            resources.append({
                                                "id": c_arn, "provider": "AWS", "type": "ECSContainer",
                                                "name": c_name,
                                                "configurationHint": f"Image: {container.get('image')} | Status: {container.get('lastStatus')}",
                                                "costEstimate": 0.0, "dependenciesString": ""
                                            })"""

new_task = """                                    task_arn = task["taskArn"]
                                    if task.get("taskDefinitionArn"): task_definition_arns.add(task["taskDefinitionArn"])
                                    resources.append({
                                        "id": task_arn, "provider": "AWS", "type": "ECSTask",
                                        "name": task_arn.split("/")[-1],
                                        "launch_type": task.get("launchType", "UNKNOWN"),
                                        "status": task.get("lastStatus"),
                                        "desired_status": task.get("desiredStatus"),
                                        "health_status": task.get("healthStatus"),
                                        "started_at": str(task.get("startedAt", "")),
                                        "stopped_at": str(task.get("stoppedAt", "")),
                                        "stopped_reason": task.get("stoppedReason", ""),
                                        "availability_zone": task.get("availabilityZone", ""),
                                        "configurationHint": f"LaunchType: {task.get('launchType', 'UNKNOWN')} | Status: {task.get('lastStatus')}",
                                        "costEstimate": 0.0, "dependenciesString": ""
                                    })
                                    # Containers
                                    for container in task.get("containers", []):
                                        c_name = container.get("name")
                                        c_arn = container.get("containerArn")
                                        if c_arn:
                                            resources.append({
                                                "id": c_arn, "provider": "AWS", "type": "ECSContainer",
                                                "name": c_name,
                                                "image": container.get("image", ""),
                                                "image_digest": container.get("imageDigest", ""),
                                                "status": container.get("lastStatus", ""),
                                                "health_status": container.get("healthStatus", "UNKNOWN"),
                                                "cpu": container.get("cpu", "N/A"),
                                                "memory": container.get("memory", "N/A"),
                                                "configurationHint": f"Image: {container.get('image')} | Status: {container.get('lastStatus')}",
                                                "costEstimate": 0.0, "dependenciesString": ""
                                            })"""

text = text.replace(old_task, new_task)

with open("backend/app/aws_scanner.py", "w") as f:
    f.write(text)

print("Scanner refined")
