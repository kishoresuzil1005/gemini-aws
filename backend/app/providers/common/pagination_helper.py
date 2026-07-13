from typing import Callable, List, Dict, Any, Optional

class PaginationHelper:
    """Abstracts cloud API pagination loops (NextToken, next_page_token, etc.)."""
    @staticmethod
    def paginate(
        func: Callable, 
        items_key: str, 
        token_key: str = 'NextToken', 
        req_token_key: str = 'NextToken',
        **kwargs
    ) -> List[Dict[str, Any]]:
        results = []
        token: Optional[str] = None
        
        while True:
            if token:
                kwargs[req_token_key] = token
            response = func(**kwargs)
            
            items = response.get(items_key, [])
            results.extend(items)
            
            token = response.get(token_key)
            if not token:
                break
                
        return results
