import json

from app.ai.prompt.system_prompt import SYSTEM_PROMPT

from app.ai.prompt.templates import (
    DIAGNOSIS_TEMPLATE,
    MIGRATION_TEMPLATE,
)


class PromptBuilder:

    def build(
        self,
        context: dict
    ) -> dict:

        intent = context.get("intent", "general")

        resources_json = json.dumps(
            context.get("resources", []),
            indent=2,
            default=str
        )

        graph_json = json.dumps(
            context.get("graph", []),
            indent=2,
            default=str
        )

        metadata_json = json.dumps(
            context.get("metadata", []),
            indent=2,
            default=str
        )

        docs_json = json.dumps(
            context.get("documents", []),
            indent=2,
            default=str
        )

        if intent == "migration":

            user_prompt = MIGRATION_TEMPLATE.format(
                question=context["question"],
                resources=resources_json
            )

        else:

            user_prompt = DIAGNOSIS_TEMPLATE.format(
                question=context["question"],
                intent=intent,
                resources=resources_json,
                relationships=graph_json,
                metadata=metadata_json,
                documents=docs_json
            )

        return {
            "system": SYSTEM_PROMPT,
            "user": user_prompt
        }
