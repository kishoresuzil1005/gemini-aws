import json


class PromptBuilder:

    @staticmethod
    def build_context(
        inventory,
        costs,
        recommendations
    ):

        # Strip internal SQLAlchemy state attributes (__dict__) if present to prevent circular serializations
        formatted_inventory = []
        for item in inventory:
            if isinstance(item, dict):
                clean_item = {k: v for k, v in item.items() if k != "_sa_instance_state"}
                formatted_inventory.append(clean_item)
            else:
                formatted_inventory.append(str(item))

        return f"""
Cloud Inventory:

{json.dumps(formatted_inventory[:50], indent=2, default=str)}

Costs:

{json.dumps(costs, indent=2, default=str)}

Recommendations:

{json.dumps(recommendations, indent=2, default=str)}
"""
