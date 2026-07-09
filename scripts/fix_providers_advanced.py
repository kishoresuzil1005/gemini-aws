import re
import os

def fix_file(filename, replacement_func):
    path = os.path.join("backend/app/providers/aws", filename)
    with open(path, "r") as f:
        src = f.read()
    src = replacement_func(src)
    with open(path, "w") as f:
        f.write(src)
    print(f"Fixed deps in {filename}")

def fix_ec2(src):
    # Dependencies for EC2 are VPC, Subnet, SecurityGroups, EBS, IAM
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': instance.get('VpcId')}] if instance.get('VpcId') else []) + ([{'type': 'Subnet', 'id': instance.get('SubnetId')}] if instance.get('SubnetId') else []) + [{'type': 'SecurityGroup', 'id': sg.get('GroupId')} for sg in instance.get('SecurityGroups', [])] + [{'type': 'EBS', 'id': v} for v in vols] + ([{'type': 'IAM', 'id': instance.get('IamInstanceProfile', {}).get('Arn')}] if instance.get('IamInstanceProfile', {}).get('Arn') else [])")

def fix_rds(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': db.get('DBSubnetGroup', {}).get('VpcId')}] if db.get('DBSubnetGroup', {}).get('VpcId') else [])")

def fix_lambda(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': fn.get('VpcConfig', {}).get('VpcId')}] if fn.get('VpcConfig', {}).get('VpcId') else [])")

def fix_apigw(src):
    return src.replace("'dependencies': []", "'dependencies': []")

fix_file("ec2.py", fix_ec2)
fix_file("rds.py", fix_rds)
fix_file("lambda_discovery.py", fix_lambda)
fix_file("apigateway.py", fix_apigw)

