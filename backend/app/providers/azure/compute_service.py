from typing import List, Dict, Any
from .azure_client import AzureClientManager

class AzureComputeService:
    def __init__(self, client_manager: AzureClientManager):
        self.client = client_manager.get_compute_client()

    def list_virtual_machines(self) -> List[Dict[str, Any]]:
        print("[AzureComputeService] Discovering Virtual Machines...")
        vms = []
        try:
            for vm in self.client.virtual_machines.list_all():
                vms.append({"id": vm.id, "name": vm.name, "location": vm.location, "type": "Azure::Compute::VirtualMachine"})
        except Exception as e:
            print(f"[AzureComputeService] Skipping real API call, mock returning empty list due to: {e}")
        return vms

    def start_vm(self, resource_group: str, vm_name: str):
        return self.client.virtual_machines.begin_start(resource_group, vm_name)

    def stop_vm(self, resource_group: str, vm_name: str):
        return self.client.virtual_machines.begin_power_off(resource_group, vm_name)
