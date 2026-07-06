# Remediation Playbook: Apply Least Privilege to IAM Role

## Objective
The role `{{ resource_id }}` currently has overly broad permissions. We must restrict its access to exactly what is needed.

## Steps
1. **Identify Role**: Open the AWS IAM Console and search for `{{ resource_id }}`.
2. **Review Policies**: Click the "Permissions" tab and expand attached policies (like `AdministratorAccess` or `*`).
3. **Audit Usage**: Use IAM Access Analyzer to generate a policy based on the role's actual CloudTrail activity over the last 30 days.
4. **Create New Policy**: Create a new custom managed policy containing only the used permissions.
5. **Attach & Detach**: Attach the new strict policy to `{{ resource_id }}`. Then, safely detach the overly broad policy.
6. **Verify**: Ensure the workload relying on `{{ resource_id }}` is still functioning without `AccessDenied` errors.
