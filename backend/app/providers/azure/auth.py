from azure.identity import DefaultAzureCredential
from azure.core.credentials import TokenCredential

class AzureAuth:
    """Manages Azure authentication credentials."""
    
    def __init__(self):
        # We currently use DefaultAzureCredential which supports:
        # - Environment variables (Service Principal)
        # - Managed Identity
        # - Azure CLI
        # - Visual Studio Code
        self._credential = DefaultAzureCredential()
        
    @property
    def credential(self) -> TokenCredential:
        return self._credential
