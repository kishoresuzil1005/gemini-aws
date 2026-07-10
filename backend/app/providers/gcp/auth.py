import google.auth
from google.auth.credentials import Credentials

class GCPAuth:
    """Manages GCP authentication credentials."""
    
    def __init__(self):
        # google.auth.default() inherently supports:
        # - Application Default Credentials (ADC)
        # - Service Accounts (via GOOGLE_APPLICATION_CREDENTIALS)
        # - Workload Identity
        # - gcloud auth application-default login
        self._credentials, self._project_id = google.auth.default()
        
    @property
    def credentials(self) -> Credentials:
        return self._credentials
        
    @property
    def default_project_id(self) -> str:
        return self._project_id
