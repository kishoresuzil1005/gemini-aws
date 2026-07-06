# Remediation Playbook: Attach Lambda to VPC

## Objective
The Lambda `{{ resource_id }}` is not connected to a VPC.

## Steps
1. **AWS Console**: Navigate to Lambda -> Functions -> select `{{ resource_id }}`.
2. **Configuration**: Go to Configuration -> VPC.
3. **Edit**: Click Edit, select the target VPC, private subnets, and a security group.
4. **Save**: Click Save. Note that this may affect cold start times and internet outbound routing.
