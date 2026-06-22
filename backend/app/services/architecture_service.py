from app.services.ai.account_tree_service import AccountTreeService

class ArchitectureService:

    def __init__(self):
        self.tree_service = AccountTreeService()

    def build_graph(self):
        return self.tree_service.generate_tree()
