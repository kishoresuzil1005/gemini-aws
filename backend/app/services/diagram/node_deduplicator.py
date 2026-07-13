import logging

logger = logging.getLogger("NodeDeduplicator")


class NodeDeduplicator:

    @staticmethod
    def deduplicate(nodes):

        unique = {}

        for node in nodes:

            node_id = node["id"]

            if node_id not in unique:

                unique[node_id] = node

            else:

                # Merge any extra keys a later occurrence may carry
                unique[node_id].update(
                    {k: v for k, v in node.items() if k != "id"}
                )

        result = list(unique.values())

        logger.debug(f"Nodes before deduplication: {len(nodes)} | after: {len(result)}")

        print(f"[NodeDeduplicator] Nodes before: {len(nodes)} | after: {len(result)}")

        return resul