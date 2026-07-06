# Remediation Playbook: Restrict SSH Access

## Objective
A security group attached to `{{ resource_id }}` allows SSH (Port 22) from `0.0.0.0/0`.

## Steps
1. **Locate Security Group**: Find the SG ID attached to `{{ resource_id }}`.
2. **AWS Console**: Navigate to EC2 -> Security Groups.
3. **Inbound Rules**: Edit inbound rules.
4. **Remove Rule**: Delete the rule allowing Port 22 from `0.0.0.0/0`.
5. **Add Safe Rule**: Add a new Port 22 rule scoped strictly to your VPN CIDR or Bastion host IP.
6. **Save**: Save rules.
