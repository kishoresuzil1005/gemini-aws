from typing import Dict, Any, List

class ContextCompressor:
    def __init__(self):
        pass

    def compress(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compresses large graphs into a summary.
        For instance, if there are 200 EC2 instances, it summarizes them 
        rather than listing all 200.
        """
        if not graph_data:
            return graph_data
            
        compressed = graph_data.copy()
        
        # Example compression logic:
        # If we have a list of relationships that is too large, summarize it.
        for key, value in compressed.items():
            if isinstance(value, list) and len(value) > 10:
                # Keep first 5 and last 5, or just summarize count
                compressed[key] = f"List of {len(value)} items (summarized). First item: {value[0]}"
                
        return compressed