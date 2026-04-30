"""CLI entrypoint for Code Knowledge Graph Engine."""

import typer
from pathlib import Path
import json
import sys

from core.graph_builder import GraphBuilder
from core.retriever import GraphRetriever
from core.watcher import GraphWatcher

app = typer.Typer(help="Code Knowledge Graph Engine - Build and query code relationships")


@app.command()
def build(
    directory: str = typer.Argument(".", help="Directory to scan"),
    output: str = typer.Option("storage/graph.json", help="Output graph file path"),
    exclude: str = typer.Option("", help="Comma-separated directories to exclude")
):
    """Build knowledge graph from a directory."""
    typer.echo(f"Building knowledge graph for: {directory}")
    
    exclude_dirs = [d.strip() for d in exclude.split(",")] if exclude else None
    builder = GraphBuilder(storage_path=output)
    
    graph = builder.build_from_directory(directory, exclude_dirs)
    builder.save_graph()
    
    stats = builder.get_stats()
    typer.echo(f"✓ Graph built successfully!")
    typer.echo(f"  Files: {stats['files']}")
    typer.echo(f"  Functions: {stats['functions']}")
    typer.echo(f"  Classes: {stats['classes']}")
    typer.echo(f"  Edges: {stats['edges']}")
    typer.echo(f"  Saved to: {output}")


@app.command()
def query(
    target: str = typer.Argument(..., help="Function or class name to query"),
    graph_path: str = typer.Option("storage/graph.json", help="Graph file path"),
    depth: int = typer.Option(5, help="Max traversal depth"),
    output: str = typer.Option("", help="Output to file (optional)")
):
    """Query dependencies for a target."""
    if not Path(graph_path).exists():
        typer.echo(f"Error: Graph file not found at {graph_path}")
        typer.echo("Run 'kg build' first to create the graph.")
        raise typer.Exit(1)
    
    builder = GraphBuilder(storage_path=graph_path)
    graph = builder.load_graph()
    retriever = GraphRetriever(graph)
    
    result = retriever.get_dependencies(target, max_depth=depth)
    
    if "error" in result:
        typer.echo(f"Error: {result['error']}")
        raise typer.Exit(1)
    
    output_data = {
        "target": target,
        "upstream_count": len(result["upstream"]),
        "downstream_count": len(result["downstream"]),
        "upstream": result["upstream"],
        "downstream": result["downstream"]
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        typer.echo(f"Results saved to: {output}")
    else:
        typer.echo(f"\n=== Dependencies for '{target}' ===")
        typer.echo(f"\nUpstream ({len(result['upstream'])}):")
        for dep in result["upstream"]:
            typer.echo(f"  - {dep['name']} ({dep['type']}) @ {dep['file']}:{dep['line']}")
        
        typer.echo(f"\nDownstream ({len(result['downstream'])}):")
        for dep in result["downstream"]:
            typer.echo(f"  - {dep['name']} ({dep['type']}) @ {dep['file']}:{dep['line']}")


@app.command()
def watch(
    directory: str = typer.Argument(".", help="Directory to watch"),
    graph_path: str = typer.Option("storage/graph.json", help="Graph file path")
):
    """Watch directory for changes and auto-update graph."""
    typer.echo(f"Starting watcher for: {directory}")
    typer.echo("Press Ctrl+C to stop...")
    
    builder = GraphBuilder(storage_path=graph_path)
    
    # Build initial graph if it doesn't exist
    if not Path(graph_path).exists():
        typer.echo("Building initial graph...")
        builder.build_from_directory(directory)
        builder.save_graph()
    else:
        builder.load_graph()
    
    def callback(file_path: str, event_type: str):
        typer.echo(f"Graph updated due to {event_type}: {file_path}")
    
    watcher = GraphWatcher(builder, callback=callback)
    
    try:
        watcher.start(directory)
        while watcher.is_watching():
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        typer.echo("\nStopping watcher...")
        watcher.stop()


@app.command()
def status(
    graph_path: str = typer.Option("storage/graph.json", help="Graph file path")
):
    """Show graph statistics."""
    if not Path(graph_path).exists():
        typer.echo(f"Error: Graph file not found at {graph_path}")
        typer.echo("Run 'kg build' first to create the graph.")
        raise typer.Exit(1)
    
    builder = GraphBuilder(storage_path=graph_path)
    graph = builder.load_graph()
    stats = builder.get_stats()
    
    typer.echo("=== Knowledge Graph Status ===")
    typer.echo(f"Files: {stats['files']}")
    typer.echo(f"Functions: {stats['functions']}")
    typer.echo(f"Classes: {stats['classes']}")
    typer.echo(f"Total Edges: {stats['edges']}")
    typer.echo(f"Graph File: {graph_path}")
    
    # Show most connected nodes
    retriever = GraphRetriever(graph)
    top_nodes = retriever.get_most_connected_nodes(limit=5)
    
    typer.echo("\n=== Most Connected Nodes ===")
    for i, node in enumerate(top_nodes, 1):
        typer.echo(f"{i}. {node['name']} ({node['type']}) - {node['total']} connections")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    node_type: str = typer.Option("", help="Filter by node type (file/function/class)"),
    graph_path: str = typer.Option("storage/graph.json", help="Graph file path")
):
    """Search for nodes in the graph."""
    if not Path(graph_path).exists():
        typer.echo(f"Error: Graph file not found at {graph_path}")
        typer.echo("Run 'kg build' first to create the graph.")
        raise typer.Exit(1)
    
    builder = GraphBuilder(storage_path=graph_path)
    graph = builder.load_graph()
    retriever = GraphRetriever(graph)
    
    results = retriever.search_nodes(query, node_type if node_type else None)
    
    typer.echo(f"\n=== Search Results for '{query}' ({len(results)} found) ===")
    for result in results:
        typer.echo(f"  - {result['name']} ({result['type']})")
        typer.echo(f"    File: {result['file']}:{result['line']}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    graph_path: str = typer.Option("storage/graph.json", help="Graph file path")
):
    """Start the API server."""
    try:
        import uvicorn
        from api.server import app as api_app, set_graph_path
        
        set_graph_path(graph_path)
        typer.echo(f"Starting API server on http://{host}:{port}")
        uvicorn.run(api_app, host=host, port=port)
    except ImportError:
        typer.echo("Error: uvicorn is required to run the server")
        typer.echo("Install with: pip install uvicorn")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
