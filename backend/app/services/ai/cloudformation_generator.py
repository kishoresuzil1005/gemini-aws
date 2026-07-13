import os

class CloudFormationGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates", "cloudformation")

    def generate(self, template_name: str, resource_id: str) -> str:
        file_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, "r") as f:
            content = f.read()
            
        return content.replace("{{ resource_id }}", resource_id).replace("{{ resource_arn }}", f"arn:aws:...:{resource_id}"