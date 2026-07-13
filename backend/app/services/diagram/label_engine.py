from app.services.diagram.typography_engine import TypographyEngine


class LabelEngine:
    """
    Produces display labels for diagram nodes.
    """

    @staticmethod
    def title(node):
        return TypographyEngine.truncate(
            node.get("display_name", "")
        )

    @staticmethod
    def metadata(node):

        resource_type = node.get("type", "")

        status = node.get("status")

        if status:
            return f"{resource_type} • {status}"

        return resource_type

    @staticmethod
    def tooltip(node):

        return (
            f"Name: {node.get('display_name','')}\n"
            f"Type: {node.get('type','')}\n"
            f"ID: {node.get('id','')}"
        )