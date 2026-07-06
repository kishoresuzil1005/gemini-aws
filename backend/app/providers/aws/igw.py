import boto3

class IGWDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_internet_gateways()
            igws = []
            for igw in response.get('InternetGateways', []):
                igws.append({'resource_id': igw['InternetGatewayId'], 'resource_type': 'InternetGateway', 'region': region, 'status': 'available', 'provider': 'AWS', 'metadata': {}, 'dependencies': []})
            return igws
        except Exception:
            return []