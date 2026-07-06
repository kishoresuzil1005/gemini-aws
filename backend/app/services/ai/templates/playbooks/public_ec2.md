# Remediation Playbook: Move EC2 to Private Subnet

## Objective
The instance `{{ resource_id }}` is currently exposed to the internet. We need to isolate it into a private subnet.

## Steps
1. **Identify Target VPC**: Find the VPC where `{{ resource_id }}` resides.
2. **Create Private Subnet**: In the AWS Console, navigate to VPC -> Subnets -> Create Subnet. Ensure it does NOT have an internet gateway route.
3. **Take a Snapshot**: Go to EC2 -> Instances, select `{{ resource_id }}`, Actions -> Image -> Create Image.
4. **Relaunch**: Launch a new instance from the new AMI, explicitly selecting the private subnet created in step 2.
5. **Verify**: Ensure the new instance is healthy and reachable via a Bastion host or VPN.
6. **Terminate Old Instance**: Terminate the original public instance `{{ resource_id }}`.
