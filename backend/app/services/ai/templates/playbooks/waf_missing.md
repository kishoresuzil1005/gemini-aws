# Remediation Playbook: Attach WAF

## Objective
The ALB `{{ resource_id }}` is internet-facing but has no WAF attached.

## Steps
1. **AWS Console**: Navigate to WAF & Shield -> Web ACLs.
2. **Create**: Create a new Web ACL (or select an existing one).
3. **Associate**: Go to Associated AWS resources, click Add AWS resources.
4. **Select ALB**: Choose Application Load Balancer and select `{{ resource_id }}`.
5. **Save**: Add and save.
