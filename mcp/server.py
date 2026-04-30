"""MCP (Model Context Protocol) server for Code Knowledge Graph Engine."""

import sys
import json
from typing import Any, Dict
from pathlib import Path

from core.graph_builder import GraphBuilder
from core.retriever import GraphRetriever


class MCPServer:
    """Stdio-based MCP server for AI agents."""
    
    def __init__(self, graph_path: str = "storage/graph.json"):
        self.graph_path = graph_path
        self.builder = None
        self.retriever = None
        self._load_graph()
    
    def _load_graph(self) -> None:
        """Load the knowledge graph."""
        self.builder = GraphBuilder(storage_path=self.graph_path)
        
        if not Path(self.graph_path).exists():
            print("Warning: Graph file not found. Run 'kg build' first.", file=sys.stderr)
            self.builder.graph = None
        else:
            self.builder.load_graph()
            self.retriever = GraphRetriever(self.builder.graph)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "dependencies":
            return self._handle_dependencies(params, request_id)
        elif method == "search":
            return self._handle_search(params, request_id)
        elif method == "stats":
            return self._handle_stats(request_id)
        elif method == "graph":
            return self._handle_graph(request_id)
        else:
            return self._error_response(request_id, f"Unknown method: {method}")
    
    def _handle_dependencies(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle dependencies request."""
        if not self.retriever:
            return self._error_response(request_id, "Graph not loaded")
        
        target = params.get("target")
        if not target:
            return self._error_response(request_id, "Missing 'target' parameter")
        
        depth = params.get("depth", 5)
        
        result = self.retriever.get_dependencies(target, max_depth=depth)
        
        if "error" in result:
            return self._error_response(request_id, result["error"])
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "target": target,
                "upstream": result["upstream"],
                "downstream": result["downstream"],
                "upstream_count": len(result["upstream"]),
                "downstream_count": len(result["downstream"])
            }
        }
    
    def _handle_search(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle search request."""
        if not self.retriever:
            return self._error_response(request_id, "Graph not loaded")
        
        query = params.get("query")
        if not query:
            return self._error_response(request_id, "Missing 'query' parameter")
        
        node_type = params.get("node_type")
        
        results = self.retriever.search_nodes(query, node_type)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "query": query,
                "count": len(results),
                "results": results
            }
        }
    
    def _handle_stats(self, request_id: Any) -> Dict[str, Any]:
        """Handle stats request."""
        if not self.builder or not self.builder.graph:
            return self._error_response(request_id, "Graph not loaded")
        
        stats = self.builder.get_stats()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": stats
        }
    
    def _handle_graph(self, request_id: Any) -> Dict[str, Any]:
        """Handle graph request."""
        if not self.builder or not self.builder.graph:
            return self._error_response(request_id, "Graph not loaded")
        
        graph_data = self.builder.graph.to_dict()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": graph_data
        }
    
    def _error_response(self, request_id: Any, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": message
            }
        }
    
    def run(self) -> None:
        """Run the MCP server (stdio-based)."""
        print("Knowledge Graph MCP Server running on stdio...", file=sys.stderr)
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


def main():
    """Main entry point for MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Knowledge Graph MCP Server")
    parser.add_argument(
        "--graph-path",
        default="storage/graph.json",
        help="Path to the graph file"
    )
    
    args = parser.parse_args()
    
    server = MCPServer(graph_path=args.graph_path)
    server.run()


if __name__ == "__main__":
    main()
