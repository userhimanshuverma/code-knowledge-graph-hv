"""Query and retrieve subgraphs from the knowledge graph."""

from typing import Dict, List, Optional, Set
from collections import deque

from core.models import KnowledgeGraph, Node, Edge, EdgeType


class GraphRetriever:
    """Retrieve dependencies and subgraphs from the knowledge graph."""
    
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
    
    def find_node_by_name(self, name: str, node_type: Optional[str] = None) -> Optional[Node]:
        """Find a node by name (supports partial matching)."""
        for node in self.graph.nodes.values():
            if node_type and node.type.value != node_type:
                continue
            
            # Exact match
            if node.name == name:
                return node
            
            # Partial match (e.g., "ClassName.method" matches just "method")
            if name in node.name or node.name in name:
                return node
        
        return None
    
    def get_dependencies(self, target: str, max_depth: int = 5) -> Dict[str, List[Dict]]:
        """
        Get upstream and downstream dependencies for a target.
        
        Args:
            target: Function or class name to query
            max_depth: Maximum depth of traversal
            
        Returns:
            Dict with 'upstream' and 'downstream' lists
        """
        node = self.find_node_by_name(target)
        if not node:
            return {"upstream": [], "downstream": [], "error": f"Node '{target}' not found"}
        
        upstream = self._get_upstream_dependencies(node.id, max_depth)
        downstream = self._get_downstream_dependencies(node.id, max_depth)
        
        return {
            "upstream": upstream,
            "downstream": downstream
        }
    
    def _get_upstream_dependencies(self, node_id: str, max_depth: int) -> List[Dict]:
        """Get upstream dependencies (what this node depends on)."""
        visited = set()
        result = []
        queue = deque([(node_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth >= max_depth:
                continue
            
            visited.add(current_id)
            
            # Get incoming edges (things that point to this node)
            incoming = self.graph.get_incoming_edges(current_id)
            
            for edge in incoming:
                source_node = self.graph.get_node(edge.source)
                if source_node and source_node.id not in visited:
                    result.append({
                        "name": source_node.name,
                        "type": source_node.type.value,
                        "file": source_node.file_path,
                        "line": source_node.line_number,
                        "relationship": edge.type.value,
                        "depth": depth + 1
                    })
                    queue.append((source_node.id, depth + 1))
        
        return result
    
    def _get_downstream_dependencies(self, node_id: str, max_depth: int) -> List[Dict]:
        """Get downstream dependencies (what depends on this node)."""
        visited = set()
        result = []
        queue = deque([(node_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth >= max_depth:
                continue
            
            visited.add(current_id)
            
            # Get outgoing edges (things this node points to)
            outgoing = self.graph.get_edges_for_node(current_id)
            
            for edge in outgoing:
                target_node = self.graph.get_node(edge.target)
                if target_node and target_node.id not in visited:
                    result.append({
                        "name": target_node.name,
                        "type": target_node.type.value,
                        "file": target_node.file_path,
                        "line": target_node.line_number,
                        "relationship": edge.type.value,
                        "depth": depth + 1
                    })
                    queue.append((target_node.id, depth + 1))
        
        return result
    
    def get_function_call_chain(self, function_name: str) -> List[Dict]:
        """Get the chain of function calls for a specific function."""
        node = self.find_node_by_name(function_name, "function")
        if not node:
            return []
        
        # Get all calls edges from this function
        call_edges = self.graph.get_edges_for_node(node.id, EdgeType.CALLS)
        
        result = []
        for edge in call_edges:
            target_node = self.graph.get_node(edge.target)
            if target_node:
                result.append({
                    "caller": node.name,
                    "callee": target_node.name,
                    "callee_file": target_node.file_path,
                    "line": edge.metadata.get("line", "unknown")
                })
        
        return result
    
    def get_import_chain(self, file_path: str) -> List[Dict]:
        """Get the import chain for a specific file."""
        node = self.find_node_by_name(file_path, "file")
        if not node:
            # Try to find by file path directly
            for n in self.graph.nodes.values():
                if n.type.value == "file" and file_path in n.file_path:
                    node = n
                    break
        
        if not node:
            return []
        
        # Get all import edges from this file
        import_edges = self.graph.get_edges_for_node(node.id, EdgeType.IMPORTS)
        
        result = []
        for edge in import_edges:
            target_node = self.graph.get_node(edge.target)
            if target_node:
                result.append({
                    "importer": node.file_path,
                    "imported": target_node.file_path,
                    "import_name": edge.metadata.get("import_name", "unknown")
                })
        
        return result
    
    def get_most_connected_nodes(self, limit: int = 10) -> List[Dict]:
        """Get the most connected nodes in the graph."""
        connection_counts = {}
        
        for node_id, node in self.graph.nodes.items():
            # Count incoming and outgoing edges
            incoming = len(self.graph.get_incoming_edges(node_id))
            outgoing = len(self.graph.get_edges_for_node(node_id))
            total = incoming + outgoing
            
            connection_counts[node_id] = {
                "name": node.name,
                "type": node.type.value,
                "file": node.file_path,
                "incoming": incoming,
                "outgoing": outgoing,
                "total": total
            }
        
        # Sort by total connections
        sorted_nodes = sorted(
            connection_counts.values(),
            key=lambda x: x["total"],
            reverse=True
        )
        
        return sorted_nodes[:limit]
    
    def search_nodes(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        """Search for nodes by name (fuzzy search)."""
        query = query.lower()
        results = []
        
        for node in self.graph.nodes.values():
            if node_type and node.type.value != node_type:
                continue
            
            if query in node.name.lower():
                results.append({
                    "id": node.id,
                    "name": node.name,
                    "type": node.type.value,
                    "file": node.file_path,
                    "line": node.line_number
                })
        
        return results
    
    def get_subgraph(self, node_ids: List[str]) -> Dict:
        """Get a subgraph containing only the specified nodes and their edges."""
        subgraph_nodes = {
            node_id: self.graph.nodes[node_id].to_dict()
            for node_id in node_ids
            if node_id in self.graph.nodes
        }
        
        subgraph_edges = [
            edge.to_dict()
            for edge in self.graph.edges
            if edge.source in node_ids and edge.target in node_ids
        ]
        
        return {
            "nodes": subgraph_nodes,
            "edges": subgraph_edges
        }
