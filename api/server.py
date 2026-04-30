"""FastAPI server for Code Knowledge Graph Engine."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path

from core.graph_builder import GraphBuilder
from core.retriever import GraphRetriever

app = FastAPI(
    title="Code Knowledge Graph API",
    description="API for querying code relationships and dependencies",
    version="1.0.0"
)

# Global graph path (set by CLI)
_graph_path = "storage/graph.json"


def set_graph_path(path: str) -> None:
    """Set the graph file path."""
    global _graph_path
    _graph_path = path


def get_graph():
    """Get the current knowledge graph."""
    builder = GraphBuilder(storage_path=_graph_path)
    
    if not Path(_graph_path).exists():
        raise HTTPException(status_code=404, detail="Graph not found. Run 'kg build' first.")
    
    graph = builder.load_graph()
    return graph


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "graph_path": _graph_path}


@app.get("/dependencies")
def get_dependencies(
    target: str = Query(..., description="Function or class name to query"),
    depth: int = Query(5, description="Max traversal depth")
):
    """Get upstream and downstream dependencies for a target."""
    graph = get_graph()
    retriever = GraphRetriever(graph)
    
    result = retriever.get_dependencies(target, max_depth=depth)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "target": target,
        "upstream_count": len(result["upstream"]),
        "downstream_count": len(result["downstream"]),
        "upstream": result["upstream"],
        "downstream": result["downstream"]
    }


@app.get("/graph")
def get_graph_data():
    """Get the complete graph data."""
    graph = get_graph()
    return graph.to_dict()


@app.get("/stats")
def get_stats():
    """Get graph statistics."""
    graph = get_graph()
    builder = GraphBuilder(storage_path=_graph_path)
    builder.graph = graph
    stats = builder.get_stats()
    
    retriever = GraphRetriever(graph)
    top_nodes = retriever.get_most_connected_nodes(limit=10)
    
    return {
        "stats": stats,
        "most_connected": top_nodes
    }


@app.get("/search")
def search_nodes(
    query: str = Query(..., description="Search query"),
    node_type: Optional[str] = Query(None, description="Filter by node type (file/function/class)")
):
    """Search for nodes in the graph."""
    graph = get_graph()
    retriever = GraphRetriever(graph)
    
    results = retriever.search_nodes(query, node_type)
    
    return {
        "query": query,
        "count": len(results),
        "results": results
    }


@app.get("/functions/{function_name}/calls")
def get_function_calls(function_name: str):
    """Get function call chain for a specific function."""
    graph = get_graph()
    retriever = GraphRetriever(graph)
    
    calls = retriever.get_function_call_chain(function_name)
    
    return {
        "function": function_name,
        "calls": calls
    }


@app.get("/files/{file_path}/imports")
def get_file_imports(file_path: str):
    """Get import chain for a specific file."""
    graph = get_graph()
    retriever = GraphRetriever(graph)
    
    imports = retriever.get_import_chain(file_path)
    
    return {
        "file": file_path,
        "imports": imports
    }


@app.get("/nodes/{node_id}")
def get_node(node_id: str):
    """Get a specific node by ID."""
    graph = get_graph()
    node = graph.get_node(node_id)
    
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    return node.to_dict()


@app.get("/nodes/{node_id}/edges")
def get_node_edges(
    node_id: str,
    edge_type: Optional[str] = Query(None, description="Filter by edge type")
):
    """Get edges for a specific node."""
    graph = get_graph()
    
    from core.models import EdgeType
    
    edge_type_enum = EdgeType(edge_type) if edge_type else None
    
    outgoing = graph.get_edges_for_node(node_id, edge_type_enum)
    incoming = graph.get_incoming_edges(node_id, edge_type_enum)
    
    return {
        "node_id": node_id,
        "outgoing": [e.to_dict() for e in outgoing],
        "incoming": [e.to_dict() for e in incoming]
    }
