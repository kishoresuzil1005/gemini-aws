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

def fix_subnet(src):
    return src.replace("'dependencies': []", "'dependencies': [{'type': 'VPC', 'id': subnet.get('VpcId')}] if subnet.get('VpcId') else []")

def fix_sg(src):
    return src.replace("'dependencies': []", "'dependencies': [{'type': 'VPC', 'id': sg.get('VpcId')}] if sg.get('VpcId') else []")

def fix_rt(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': rt.get('VpcId')}] if rt.get('VpcId') else []) + [{'type': 'Subnet', 'id': s} for s in associations] + [{'type': 'InternetGateway', 'id': g} for g in gateways] + [{'type': 'NatGateway', 'id': n} for n in nat_gateways]")

def fix_nat(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': nat.get('VpcId')}] if nat.get('VpcId') else []) + ([{'type': 'Subnet', 'id': nat.get('SubnetId')}] if nat.get('SubnetId') else [])")

def fix_eni(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': eni.get('VpcId')}] if eni.get('VpcId') else []) + ([{'type': 'Subnet', 'id': eni.get('SubnetId')}] if eni.get('SubnetId') else []) + [{'type': 'SecurityGroup', 'id': g.get('GroupId')} for g in eni.get('Groups', []) if g.get('GroupId')]")

def fix_eip(src):
    return src.replace("'dependencies': []", "'dependencies': [{'type': 'NetworkInterface', 'id': eip.get('NetworkInterfaceId')}] if eip.get('NetworkInterfaceId') else []")

def fix_alb(src):
    return src.replace("'dependencies': []", " 'dependencies': ([{'type': 'VPC', 'id': lb.get('VpcId')}] if lb.get('VpcId') else []) + [{'type': 'Subnet', 'id': az.get('SubnetId')} for az in lb.get('AvailabilityZones', []) if az.get('SubnetId')] + [{'type': 'SecurityGroup', 'id': sg} for sg in lb.get('SecurityGroups', [])]")

def fix_tg(src):
    return src.replace("'dependencies': []", "'dependencies': ([{'type': 'VPC', 'id': tg.get('VpcId')}] if tg.get('VpcId') else []) + [{'type': 'ALB', 'id': lb} for lb in load_balancers]")

def fix_cf(src):
    return src.replace("'dependencies': []", "'dependencies': [{'type': 'WAF', 'id': dist.get('WebACLId')}] if dist.get('WebACLId') else []")

fix_file("subnet.py", fix_subnet)
fix_file("security_group.py", fix_sg)
fix_file("route_table.py", fix_rt)
fix_file("nat_gateway.py", fix_nat)
fix_file("network_interface.py", fix_eni)
fix_file("elastic_ip.py", fix_eip)
fix_file("alb.py", fix_alb)
fix_file("target_group.py", fix_tg)
fix_file("cloudfront.py", fix_cf)
