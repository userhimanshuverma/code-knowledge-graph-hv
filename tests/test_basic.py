"""Basic tests for Code Knowledge Graph Engine."""

import pytest
import tempfile
import os
from pathlib import Path

from core.models import KnowledgeGraph, Node, Edge, NodeType, EdgeType
from core.parser import PythonParser
from core.graph_builder import GraphBuilder
from core.retriever import GraphRetriever


class TestModels:
    """Test graph models."""
    
    def test_node_creation(self):
        """Test creating a node."""
        node = Node(
            id="test_node",
            type=NodeType.FUNCTION,
            name="test_func",
            file_path="test.py",
            line_number=10
        )
        assert node.id == "test_node"
        assert node.type == NodeType.FUNCTION
        assert node.name == "test_func"
    
    def test_node_serialization(self):
        """Test node to_dict and from_dict."""
        node = Node(
            id="test_node",
            type=NodeType.CLASS,
            name="TestClass",
            file_path="test.py",
            line_number=5,
            metadata={"methods": ["method1"]}
        )
        
        data = node.to_dict()
        restored = Node.from_dict(data)
        
        assert restored.id == node.id
        assert restored.type == node.type
        assert restored.name == node.name
        assert restored.metadata == node.metadata
    
    def test_edge_creation(self):
        """Test creating an edge."""
        edge = Edge(
            source="node1",
            target="node2",
            type=EdgeType.CALLS
        )
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.type == EdgeType.CALLS
    
    def test_graph_operations(self):
        """Test graph add operations."""
        graph = KnowledgeGraph()
        
        node1 = Node(
            id="node1",
            type=NodeType.FUNCTION,
            name="func1",
            file_path="test.py",
            line_number=1
        )
        node2 = Node(
            id="node2",
            type=NodeType.FUNCTION,
            name="func2",
            file_path="test.py",
            line_number=10
        )
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge = Edge(source="node1", target="node2", type=EdgeType.CALLS)
        graph.add_edge(edge)
        
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.get_node("node1") == node1


class TestParser:
    """Test Python parser."""
    
    def test_parse_simple_function(self):
        """Test parsing a simple function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello_world():
    print("Hello, World!")
""")
            f.flush()
            temp_path = f.name
        
        try:
            parser = PythonParser()
            parsed = parser.parse_file(temp_path)
            
            assert parsed is not None
            assert len(parsed.functions) == 1
            assert parsed.functions[0]['name'] == 'hello_world'
            assert parsed.functions[0]['line_number'] == 2
        finally:
            os.unlink(temp_path)
    
    def test_parse_class(self):
        """Test parsing a class."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
""")
            f.flush()
            temp_path = f.name
        
        try:
            parser = PythonParser()
            parsed = parser.parse_file(temp_path)
            
            assert parsed is not None
            assert len(parsed.classes) == 1
            assert parsed.classes[0]['name'] == 'MyClass'
            assert len(parsed.functions) == 2
        finally:
            os.unlink(temp_path)
    
    def test_parse_imports(self):
        """Test parsing imports."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
import sys as system
from typing import List
""")
            f.flush()
            temp_path = f.name
        
        try:
            parser = PythonParser()
            parsed = parser.parse_file(temp_path)
            
            assert parsed is not None
            assert len(parsed.imports) == 3
        finally:
            os.unlink(temp_path)


class TestGraphBuilder:
    """Test graph builder."""
    
    def test_build_graph(self):
        """Test building a graph from parsed data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def func_a():
    func_b()

def func_b():
    pass
""")
            
            builder = GraphBuilder(storage_path=str(Path(tmpdir) / "graph.json"))
            graph = builder.build_from_directory(tmpdir)
            
            assert len(graph.nodes) > 0
            assert len(graph.edges) > 0
    
    def test_graph_persistence(self):
        """Test saving and loading graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "graph.json"
            builder = GraphBuilder(storage_path=str(graph_path))
            
            # Create a simple graph
            node = Node(
                id="test",
                type=NodeType.FUNCTION,
                name="test",
                file_path="test.py",
                line_number=1
            )
            builder.graph.add_node(node)
            builder.save_graph()
            
            # Load the graph
            builder2 = GraphBuilder(storage_path=str(graph_path))
            loaded_graph = builder2.load_graph()
            
            assert "test" in loaded_graph.nodes
            assert loaded_graph.nodes["test"].name == "test"


class TestGraphRetriever:
    """Test graph retriever."""
    
    def test_find_node_by_name(self):
        """Test finding a node by name."""
        graph = KnowledgeGraph()
        node = Node(
            id="func1",
            type=NodeType.FUNCTION,
            name="my_function",
            file_path="test.py",
            line_number=1
        )
        graph.add_node(node)
        
        retriever = GraphRetriever(graph)
        found = retriever.find_node_by_name("my_function")
        
        assert found is not None
        assert found.name == "my_function"
    
    def test_search_nodes(self):
        """Test searching nodes."""
        graph = KnowledgeGraph()
        
        graph.add_node(Node(
            id="func1",
            type=NodeType.FUNCTION,
            name="user_auth",
            file_path="auth.py",
            line_number=1
        ))
        graph.add_node(Node(
            id="func2",
            type=NodeType.FUNCTION,
            name="user_logout",
            file_path="auth.py",
            line_number=10
        ))
        
        retriever = GraphRetriever(graph)
        results = retriever.search_nodes("user")
        
        assert len(results) == 2
    
    def test_get_dependencies(self):
        """Test getting dependencies."""
        graph = KnowledgeGraph()
        
        # Create nodes
        func_a = Node(
            id="func_a",
            type=NodeType.FUNCTION,
            name="func_a",
            file_path="test.py",
            line_number=1
        )
        func_b = Node(
            id="func_b",
            type=NodeType.FUNCTION,
            name="func_b",
            file_path="test.py",
            line_number=10
        )
        
        graph.add_node(func_a)
        graph.add_node(func_b)
        
        # Create edge
        edge = Edge(source="func_a", target="func_b", type=EdgeType.CALLS)
        graph.add_edge(edge)
        
        retriever = GraphRetriever(graph)
        deps = retriever.get_dependencies("func_a")
        
        assert "upstream" in deps
        assert "downstream" in deps
        assert len(deps["downstream"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
