from google.cloud import monitoring_v3
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.exceptions import map_gcp_exception

class MonitorService:
    def __init__(self, auth: GCPAuth):
        self.auth = auth
        self.metric_client = monitoring_v3.MetricServiceClient(credentials=auth.credentials)
        self.alert_client = monitoring_v3.AlertPolicyServiceClient(credentials=auth.credentials)

    def execute(self, method_name: str, **kwargs):
        try:
            if "alert" in method_name:
                method = getattr(self.alert_client, method_name)
            else:
                method = getattr(self.metric_client, method_name)
            return method(**kwargs)
        except Exception as e:
            raise map_gcp_exception(e)
