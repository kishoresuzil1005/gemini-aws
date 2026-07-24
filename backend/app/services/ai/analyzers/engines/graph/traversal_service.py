"""
Traversal Service.
Contains generic, iterative graph traversal algorithms.
Completely decoupled from the Graph object itself.
"""
from typing import List, Set, Generator
from collections import deque
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex

class TraversalService:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @staticmethod
    def bfs(index: GraphIndex, start_node: str, max_depth: int = 10, reverse: bool = False) -> Generator[str, None, None]:
        """
        Iterative BFS to prevent RecursionError on large graphs.
        Yields nodes up to max_depth.
        """
        adjacency = index.reverse_adjacency if reverse else index.adjacency
        
        visited = set([start_node])
        queue = deque([(start_node, 0)])
        
        while queue:
            current, depth = queue.popleft()
            if current != start_node:
                yield current
                
            if depth >= max_depth:
                continue
                
            neighbors = adjacency.get(current, set())
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    
    @staticmethod
    def dfs(index: GraphIndex, start_node: str, max_depth: int = 10, reverse: bool = False) -> Generator[str, None, None]:
        """
        Iterative DFS.
        """
        adjacency = index.reverse_adjacency if reverse else index.adjacency
        
        visited = set([start_node])
        stack = [(start_node, 0)]
        
        while stack:
            current, depth = stack.pop()
            if current != start_node:
                yield current
                
            if depth >= max_depth:
                continue
                
            neighbors = adjacency.get(current, set())
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, depth + 1))

    @staticmethod
    def shortest_path(index: GraphIndex, start_node: str, target_node: str) -> List[str]:
        """Finds the shortest path between two nodes using BFS (optimized with parent pointers)."""
        if start_node == target_node:
            return [start_node]
            
        queue = deque([start_node])
        visited = set([start_node])
        parents = {start_node: None}
        
        while queue:
            current = queue.popleft()
            if current == target_node:
                # Reconstruct path
                path = []
                curr = current
                while curr is not None:
                    path.append(curr)
                    curr = parents[curr]
                return path[::-1]
                
            neighbors = index.adjacency.get(current, set())
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parents[neighbor] = current
                    queue.append(neighbor)
        return []

    @staticmethod
    def topological_sort(index: GraphIndex) -> List[str]:
        """
        Iterative Topological Sort using Kahn's algorithm.
        Returns a valid ordering of nodes. Discards nodes in cycles.
        """
        in_degree = {node: 0 for node in index.adjacency.keys()}
        for node in index.reverse_adjacency.keys():
            if node not in in_degree:
                in_degree[node] = 0
                
        for node, neighbors in index.adjacency.items():
            for neighbor in neighbors:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
                
        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        topo_order = []
        
        while queue:
            current = queue.popleft()
            topo_order.append(current)
            for neighbor in index.adjacency.get(current, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        return topo_order

    @staticmethod
    def longest_path(index: GraphIndex, start_node: str, reverse: bool = False) -> List[str]:
        """
        Computes the longest path from start_node (useful for true critical path).
        Works effectively on DAGs. If cycles exist, this approximates using BFS depth tracking.
        """
        adjacency = index.reverse_adjacency if reverse else index.adjacency
        queue = deque([(start_node, [start_node])])
        longest = []
        
        while queue:
            current, path = queue.popleft()
            if len(path) > len(longest):
                longest = path
                
            if len(path) > 20: # Sanity limit for enterprise graphs to avoid infinite loop on cycles
                continue
                
            for neighbor in adjacency.get(current, set()):
                if neighbor not in path: # Prevents simple cycles
                    queue.append((neighbor, path + [neighbor]))
                    
        return longest

    @staticmethod
    def tarjan_scc(index: GraphIndex) -> List[List[str]]:
        """
        Iterative Tarjan's Strongly Connected Components algorithm.
        Returns a list of components (cycles if len > 1).
        """
        ids = {}
        low = {}
        on_stack = set()
        stack = []
        result = []
        current_id = 0
        
        def iter_dfs(start_node):
            nonlocal current_id
            call_stack = [(start_node, 0)]
            
            while call_stack:
                u, nxt_idx = call_stack.pop()
                
                if nxt_idx == 0:
                    ids[u] = current_id
                    low[u] = current_id
                    current_id += 1
                    on_stack.add(u)
                    stack.append(u)
                    
                neighbors = list(index.adjacency.get(u, set()))
                
                if nxt_idx < len(neighbors):
                    v = neighbors[nxt_idx]
                    call_stack.append((u, nxt_idx + 1))
                    if v not in ids:
                        call_stack.append((v, 0))
                    elif v in on_stack:
                        low[u] = min(low[u], ids[v])
                else:
                    if ids[u] == low[u]:
                        scc = []
                        while True:
                            w = stack.pop()
                            on_stack.remove(w)
                            scc.append(w)
                            if w == u:
                                break
                        result.append(scc)
                    
                    if call_stack:
                        parent, _ = call_stack[-1]
                        low[parent] = min(low[parent], low[u])

        for node in index.adjacency.keys():
            if node not in ids:
                iter_dfs(node)
                
        return result
