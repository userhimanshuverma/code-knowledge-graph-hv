"""Build knowledge graph from parsed code data."""

from pathlib import Path
from typing import Dict, List, Optional
import json

from core.models import KnowledgeGraph, Node, Edge, NodeType, EdgeType
from core.multi_parser import MultiLanguageParser, ParsedFile


class GraphBuilder:
    """Build knowledge graph from parsed code."""
    
    def __init__(self, storage_path: str = "storage/graph.json"):
        self.storage_path = storage_path
        self.graph = KnowledgeGraph()
        self.parser = MultiLanguageParser()
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists."""
        storage_dir = Path(self.storage_path).parent
        storage_dir.mkdir(parents=True, exist_ok=True)
    
    def build_from_directory(self, directory: str, exclude_dirs: Optional[List[str]] = None) -> KnowledgeGraph:
        """Build graph from all supported files in a directory."""
        # Parse all files
        parsed_files = self.parser.parse_directory(directory, exclude_dirs)
        
        # Build nodes and edges
        self._build_nodes(parsed_files)
        self._build_edges(parsed_files)
        
        return self.graph
    
    def _build_nodes(self, parsed_files: Dict[str, ParsedFile]) -> None:
        """Build nodes from parsed files."""
        for file_path, parsed in parsed_files.items():
            # Create file node
            file_node_id = f"file:{file_path}"
            file_node = Node(
                id=file_node_id,
                type=NodeType.FILE,
                name=Path(file_path).name,
                file_path=file_path,
                line_number=1,
                metadata={"path": file_path}
            )
            self.graph.add_node(file_node)
            
            # Create function nodes
            for func in parsed.functions:
                func_node_id = f"function:{func['name']}:{file_path}"
                func_node = Node(
                    id=func_node_id,
                    type=NodeType.FUNCTION,
                    name=func['name'],
                    file_path=file_path,
                    line_number=func['line_number'],
                    metadata={
                        "args": func['args'],
                        "is_method": func['is_method']
                    }
                )
                self.graph.add_node(func_node)
                
                # Create edge: file -> defines -> function
                edge = Edge(
                    source=file_node_id,
                    target=func_node_id,
                    type=EdgeType.DEFINES
                )
                self.graph.add_edge(edge)
            
            # Create class nodes
            for cls in parsed.classes:
                class_node_id = f"class:{cls['name']}:{file_path}"
                class_node = Node(
                    id=class_node_id,
                    type=NodeType.CLASS,
                    name=cls['name'],
                    file_path=file_path,
                    line_number=cls['line_number'],
                    metadata={"methods": cls['methods']}
                )
                self.graph.add_node(class_node)
                
                # Create edge: file -> defines -> class
                edge = Edge(
                    source=file_node_id,
                    target=class_node_id,
                    type=EdgeType.DEFINES
                )
                self.graph.add_edge(edge)
    
    def _build_edges(self, parsed_files: Dict[str, ParsedFile]) -> None:
        """Build edges from parsed files."""
        for file_path, parsed in parsed_files.items():
            file_node_id = f"file:{file_path}"
            
            # Create import edges
            for imp in parsed.imports:
                # Try to find the target file
                target_file = self._resolve_import(imp['name'], file_path)
                if target_file:
                    target_file_id = f"file:{target_file}"
                    edge = Edge(
                        source=file_node_id,
                        target=target_file_id,
                        type=EdgeType.IMPORTS,
                        metadata={"import_name": imp['name']}
                    )
                    self.graph.add_edge(edge)
            
            # Create function call edges
            for call in parsed.function_calls:
                caller_id = f"function:{call['caller']}:{file_path}"
                callee_id = self._find_function_node(call['callee'], file_path)
                if callee_id:
                    edge = Edge(
                        source=caller_id,
                        target=callee_id,
                        type=EdgeType.CALLS,
                        metadata={"line": call['line_number']}
                    )
                    self.graph.add_edge(edge)
    
    def _resolve_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Resolve import to actual file path."""
        # Simple heuristic: check if it's a local import
        current_dir = Path(current_file).parent
        current_ext = Path(current_file).suffix.lower()
        
        # Determine file extensions based on current file type
        if current_ext in ['.ts', '.tsx']:
            extensions = ['.ts', '.tsx']
        elif current_ext in ['.js', '.jsx']:
            extensions = ['.js', '.jsx']
        else:
            extensions = ['.py']
        
        # Handle relative imports
        if import_name.startswith('.'):
            parts = import_name.split('.')
            base_dir = current_dir
            for part in parts[:-1]:
                if part == '':
                    base_dir = base_dir.parent
                else:
                    base_dir = base_dir / part
            
            module_name = parts[-1] if parts[-1] else ''
            possible_paths = []
            
            for ext in extensions:
                possible_paths.extend([
                    base_dir / f"{module_name}{ext}",
                    base_dir / module_name / f"index{ext}",
                    base_dir / f"{module_name}.py",  # Fallback to Python
                    base_dir / module_name / "__init__.py"  # Fallback to Python
                ])
            
            for path in possible_paths:
                if path.exists():
                    return str(path)
        
        # Handle absolute imports (check if it's a local package)
        parts = import_name.split('.')
        module_name = parts[0]
        possible_paths = []
        
        for ext in extensions:
            possible_paths.extend([
                current_dir / f"{module_name}{ext}",
                current_dir / module_name / f"index{ext}",
                current_dir / f"{module_name}.py",
                current_dir / module_name / "__init__.py",
                current_dir.parent / f"{module_name}{ext}",
                current_dir.parent / module_name / f"index{ext}",
                current_dir.parent / f"{module_name}.py",
                current_dir.parent / module_name / "__init__.py"
            ])
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def _find_function_node(self, func_name: str, current_file: str) -> Optional[str]:
        """Find function node ID by name."""
        # First try to find in current file
        for node_id, node in self.graph.nodes.items():
            if node.type == NodeType.FUNCTION and node.name == func_name:
                return node_id
        
        # Try to find in any file
        for node_id, node in self.graph.nodes.items():
            if node.type == NodeType.FUNCTION:
                # Check if function name matches (strip class prefix if present)
                simple_name = node.name.split('.')[-1]
                if simple_name == func_name or node.name == func_name:
                    return node_id
        
        return None
    
    def save_graph(self) -> None:
        """Save graph to storage."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph.to_dict(), f, indent=2)
    
    def load_graph(self) -> KnowledgeGraph:
        """Load graph from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.graph = KnowledgeGraph.from_dict(data)
        except FileNotFoundError:
            self.graph = KnowledgeGraph()
        except Exception as e:
            print(f"Error loading graph: {e}")
            self.graph = KnowledgeGraph()
        
        return self.graph
    
    def update_graph(self, file_path: str) -> None:
        """Update graph for a single file."""
        # Remove existing nodes and edges for this file
        file_node_id = f"file:{file_path}"
        
        # Remove file node
        if file_node_id in self.graph.nodes:
            del self.graph.nodes[file_node_id]
        
        # Remove all nodes defined in this file
        nodes_to_remove = [
            node_id for node_id, node in self.graph.nodes.items()
            if node.file_path == file_path
        ]
        for node_id in nodes_to_remove:
            del self.graph.nodes[node_id]
        
        # Remove all edges from/to these nodes
        self.graph.edges = [
            edge for edge in self.graph.edges
            if edge.source not in nodes_to_remove and edge.target not in nodes_to_remove
        ]
        
        # Re-parse the file
        parsed = self.parser.parse_file(file_path)
        if parsed:
            self._build_nodes({file_path: parsed})
            self._build_edges({file_path: parsed})
    
    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        file_count = sum(1 for n in self.graph.nodes.values() if n.type == NodeType.FILE)
        function_count = sum(1 for n in self.graph.nodes.values() if n.type == NodeType.FUNCTION)
        class_count = sum(1 for n in self.graph.nodes.values() if n.type == NodeType.CLASS)
        edge_count = len(self.graph.edges)
        
        return {
            "files": file_count,
            "functions": function_count,
            "classes": class_count,
            "edges": edge_count
        }
