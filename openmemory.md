# Code Knowledge Graph Engine - Project Overview

## Project Description
A lightweight, production-grade knowledge graph engine for codebases that builds and maintains an always-updated graph of code relationships (functions, classes, imports, calls). Exposes functionality via CLI, REST API, and MCP (Model Context Protocol) for AI-assisted development tools.

## Architecture
- **Core**: AST-based Python parser, graph builder, retriever, file watcher
- **CLI**: Typer-based command-line interface (build, query, watch, status, search, serve)
- **API**: FastAPI server with REST endpoints for graph queries
- **MCP**: Stdio-based MCP server for AI agent integration

## Key Components
- `core/models.py`: Graph schema (Node, Edge, KnowledgeGraph) with JSON serialization
- `core/parser.py`: Python AST parser extracting functions, classes, imports, function calls
- `core/graph_builder.py`: Builds knowledge graph from parsed data with deduplication
- `core/retriever.py`: Query engine for dependencies, search, subgraph retrieval
- `core/watcher.py`: File system watcher using watchdog for auto-updates
- `cli/main.py`: CLI entrypoint with kg command
- `api/server.py`: FastAPI server with /health, /dependencies, /graph, /stats, /search endpoints
- `mcp/server.py`: MCP stdio server supporting dependencies, search, stats, graph methods

## Graph Schema
**Node Types**: file, function, class
**Edge Types**: calls, imports, defines
**Storage**: JSON file at storage/graph.json

## Installation
```bash
pip install .
```

## Entry Points
- `kg`: CLI command (cli.main:main)
- `kg-mcp`: MCP server (mcp.server:main)

## Testing
```bash
pytest tests/test_basic.py
```

## User Defined Namespaces
- [Leave blank - user populates]
