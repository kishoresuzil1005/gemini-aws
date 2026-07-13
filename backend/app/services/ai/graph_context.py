
class GraphContextBuilder:
    def get_context(self, resource_id: str):
        return {"resource": resource_id, "dependencies": []}
