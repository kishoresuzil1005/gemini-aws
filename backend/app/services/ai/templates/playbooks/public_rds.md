# Remediation Playbook: Disable Public RDS

## Objective
The RDS database `{{ resource_id }}` is marked as publicly accessible.

## Steps
1. **AWS Console**: Navigate to RDS -> Databases -> select `{{ resource_id }}`.
2. **Modify**: Click "Modify".
3. **Connectivity**: Under Connectivity -> Additional configuration, set "Public access" to "Not publicly accessible".
4. **Apply**: Click Continue -> Apply immediately.
5. **Verify**: Test database connectivity from an internal EC2 instance to ensure application health.
