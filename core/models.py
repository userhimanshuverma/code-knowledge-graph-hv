"""Graph schema models for the knowledge graph."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"


class EdgeType(Enum):
    """Types of edges in the knowledge graph."""
    CALLS = "calls"
    IMPORTS = "imports"
    DEFINES = "defines"


@dataclass
class Node:
    """Represents a node in the knowledge graph."""
    id: str
    type: NodeType
    name: str
    file_path: str
    line_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            name=data["name"],
            file_path=data["file_path"],
            line_number=data["line_number"],
            metadata=data.get("metadata", {})
        )


@dataclass
class Edge:
    """Represents an edge in the knowledge graph."""
    source: str
    target: str
    type: EdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """Create edge from dictionary."""
        return cls(
            source=data["source"],
            target=data["target"],
            type=EdgeType(data["type"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class KnowledgeGraph:
    """Represents the complete knowledge graph."""
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edges_for_node(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[Edge]:
        """Get all edges for a specific node."""
        if edge_type:
            return [e for e in self.edges if e.source == node_id and e.type == edge_type]
        return [e for e in self.edges if e.source == node_id]
    
    def get_incoming_edges(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[Edge]:
        """Get all incoming edges for a specific node."""
        if edge_type:
            return [e for e in self.edges if e.target == node_id and e.type == edge_type]
        return [e for e in self.edges if e.target == node_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for JSON serialization."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """Create graph from dictionary."""
        graph = cls()
        for node_id, node_data in data.get("nodes", {}).items():
            graph.add_node(Node.from_dict(node_data))
        for edge_data in data.get("edges", []):
            graph.add_edge(Edge.from_dict(edge_data))
        return graph
