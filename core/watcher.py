"""File watcher for auto-updating the knowledge graph."""

import time
from pathlib import Path
from typing import Optional, List, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from core.graph_builder import GraphBuilder


class GraphFileHandler(FileSystemEventHandler):
    """Handle file system events for graph updates."""
    
    def __init__(self, graph_builder: GraphBuilder, callback: Optional[Callable] = None):
        self.graph_builder = graph_builder
        self.callback = callback
        self.debounce_seconds = 0.5
        self.last_update_time = {}
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        # Debounce rapid changes
        current_time = time.time()
        if event.src_path in self.last_update_time:
            if current_time - self.last_update_time[event.src_path] < self.debounce_seconds:
                return
        
        self.last_update_time[event.src_path] = current_time
        
        print(f"File modified: {event.src_path}")
        self.graph_builder.update_graph(event.src_path)
        self.graph_builder.save_graph()
        
        if self.callback:
            self.callback(event.src_path, "modified")
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        print(f"File created: {event.src_path}")
        self.graph_builder.update_graph(event.src_path)
        self.graph_builder.save_graph()
        
        if self.callback:
            self.callback(event.src_path, "created")
    
    def on_deleted(self, event):
        """Handle file deletion."""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        print(f"File deleted: {event.src_path}")
        # Remove nodes for deleted file
        file_node_id = f"file:{event.src_path}"
        
        # Remove file node
        if file_node_id in self.graph_builder.graph.nodes:
            del self.graph_builder.graph.nodes[file_node_id]
        
        # Remove all nodes defined in this file
        nodes_to_remove = [
            node_id for node_id, node in self.graph_builder.graph.nodes.items()
            if node.file_path == event.src_path
        ]
        for node_id in nodes_to_remove:
            del self.graph_builder.graph.nodes[node_id]
        
        # Remove all edges from/to these nodes
        self.graph_builder.graph.edges = [
            edge for edge in self.graph_builder.graph.edges
            if edge.source not in nodes_to_remove and edge.target not in nodes_to_remove
        ]
        
        self.graph_builder.save_graph()
        
        if self.callback:
            self.callback(event.src_path, "deleted")


class GraphWatcher:
    """Watch for file changes and auto-update the knowledge graph."""
    
    def __init__(self, graph_builder: GraphBuilder, callback: Optional[Callable] = None):
        self.graph_builder = graph_builder
        self.observer = Observer()
        self.handler = GraphFileHandler(graph_builder, callback)
        self.watching = False
    
    def start(self, directory: str, recursive: bool = True) -> None:
        """Start watching a directory."""
        if self.watching:
            print("Watcher is already running")
            return
        
        path = Path(directory)
        if not path.exists():
            print(f"Directory does not exist: {directory}")
            return
        
        self.observer.schedule(self.handler, str(path), recursive=recursive)
        self.observer.start()
        self.watching = True
        print(f"Watching directory: {directory}")
    
    def stop(self) -> None:
        """Stop watching."""
        if not self.watching:
            return
        
        self.observer.stop()
        self.observer.join()
        self.watching = False
        print("Watcher stopped")
    
    def is_watching(self) -> bool:
        """Check if watcher is running."""
        return self.watching
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
