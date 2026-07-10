from pydantic import BaseModel
import uuid
from typing import Dict

class Workspace(BaseModel):
    workspace_id: str = str(uuid.uuid4())
    org_id: str
    name: str

class Project(BaseModel):
    project_id: str = str(uuid.uuid4())
    workspace_id: str
    name: str

class HierarchyManager:
    """
    Manages the organizational hierarchy (Org -> Workspace -> Project).
    """
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.projects: Dict[str, Project] = {}

    def create_workspace(self, org_id: str, name: str) -> Workspace:
        ws = Workspace(org_id=org_id, name=name)
        self.workspaces[ws.workspace_id] = ws
        return ws

    def create_project(self, workspace_id: str, name: str) -> Project:
        proj = Project(workspace_id=workspace_id, name=name)
        self.projects[proj.project_id] = proj
        return proj
