# Code Knowledge Graph Engine

[![PyPI version](https://badge.fury.io/py/code-knowledge-graph-hv.svg)](https://badge.fury.io/py/code-knowledge-graph-hv)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/code-knowledge-graph-hv.svg)](https://pypi.org/project/code-knowledge-graph-hv/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A production-grade, multi-language knowledge graph engine for codebases.** Build and maintain an always-updated graph of code relationships (functions, classes, imports, calls) and query it via CLI, REST API, or MCP (Model Context Protocol) for AI-assisted development.

---

## Table of Contents

- [What is it?](#what-is-it)
- [Why use it?](#why-use-it)
- [Key Features](#key-features)
- [Supported Languages](#supported-languages)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [CLI](#cli)
  - [REST API](#rest-api)
  - [MCP Server](#mcp-server)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Performance](#performance)
- [Use Cases](#use-cases)
- [LLM Integration](#llm-integration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Changelog](#changelog)
- [Roadmap](#roadmap)
- [Support](#support)

---

## What is it?

The Code Knowledge Graph Engine is a lightweight, production-grade tool that builds and maintains a knowledge graph of your codebase. It extracts code structure (functions, classes, imports, function calls) and stores relationships as a graph, enabling efficient querying and analysis.

**Key capabilities:**
- **Multi-language support**: Python, TypeScript, JavaScript, JSX, TSX
- **AST-based parsing**: Accurate code structure extraction
- **Real-time updates**: Auto-update on file changes with built-in watcher
- **Multiple interfaces**: CLI, REST API, MCP server
- **AI-ready**: Optimized for LLM integration with 10-100x token reduction
- **Enterprise-ready**: Multiprocessing, progress reporting, error handling

---

## Why use it?

### For LLM/AI Development
- **10-100x token reduction**: Query relationships instead of loading entire files
- **Context awareness**: Understand code structure, not just syntax
- **Scalability**: Works on huge codebases without context overflow
- **Consistency**: Same graph ensures consistent understanding across sessions

### For Development Teams
- **Impact analysis**: Understand dependencies before refactoring
- **Code navigation**: Quickly find relationships between components
- **Architecture insights**: Visualize code structure and dependencies
- **Onboarding**: Understand new codebases faster

### For Enterprise
- **Production-ready**: Multiprocessing, error handling, logging
- **Extensible**: Simple architecture for customization
- **Secure**: No external network calls, local processing only
- **Performant**: 5000+ files parsed in ~1 minute

## Key Features

### Core Functionality
- **Multi-language parsing**: Support for Python, TypeScript, JavaScript, JSX, TSX using tree-sitter
- **AST-based analysis**: Accurate extraction of functions, classes, imports, and call relationships
- **Graph-based storage**: Efficient JSON storage of nodes and edges
- **Real-time updates**: Watchdog-based file watching for automatic graph updates
- **Multiprocessing**: Parallel file parsing for large codebases (5000+ files in ~1 minute)

### Interfaces
- **CLI**: Command-line interface with typer for easy operation
- **REST API**: FastAPI-based HTTP server with comprehensive endpoints
- **MCP Server**: Model Context Protocol server for AI agent integration

### Performance
- **Progress reporting**: Real-time progress updates during parsing
- **File size limits**: Configurable limits to avoid memory issues
- **Smart exclusions**: Automatic exclusion of common directories (node_modules, venv, etc.)
- **Caching**: Efficient graph storage and retrieval

### Enterprise Features
- **Error handling**: Robust error handling and logging
- **Configuration**: Flexible configuration options
- **Extensibility**: Simple architecture for custom parsers and analyzers
- **Security**: No external network calls, local processing only

---

## Supported Languages

| Language | Extensions | Parser | Status |
|----------|-----------|--------|--------|
| Python | `.py` | AST | ✅ Fully Supported |
| TypeScript | `.ts`, `.tsx` | tree-sitter | ✅ Fully Supported |
| JavaScript | `.js`, `.jsx` | tree-sitter | ✅ Fully Supported |

**Planned Support:**
- Java
- Go
- Rust
- C/C++
- Ruby
- PHP

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from PyPI (Recommended)

```bash
pip install code-knowledge-graph-hv
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/userhimanshuverma/code-knowledge-graph-hv.git
cd code-knowledge-graph-hv

# Install with pip
pip install .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# This includes: pytest, pytest-cov, black, ruff
```

### Verify Installation

```bash
# Check CLI is available
kg --help

# Or use Python module
python -m cli.main --help
```

### Dependencies

The package includes the following dependencies:
- `typer>=0.9.0` - CLI framework
- `fastapi>=0.100.0` - REST API framework
- `watchdog>=3.0.0` - File system watching
- `uvicorn[standard]>=0.23.0` - ASGI server
- `tree-sitter>=0.20.0` - Parser for multiple languages
- `tree-sitter-typescript>=0.20.0` - TypeScript parser
- `tree-sitter-python>=0.20.0` - Python parser
- `tree-sitter-javascript>=0.20.0` - JavaScript parser

---

## Quick Start

### For New Projects

1. **Navigate to your project directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Build the knowledge graph**
   ```bash
   kg build
   ```

3. **Verify the graph was created**
   ```bash
   kg status
   ```

### For Existing Projects

1. **Install the package**
   ```bash
   pip install code-knowledge-graph-hv
   ```

2. **Build the graph with exclusions**
   ```bash
   kg build . --exclude "venv,node_modules,.git,dist,build"
   ```

3. **Check the results**
   ```bash
   kg status
   ```

### For Large Codebases (5000+ files)

The tool is optimized for large codebases with multiprocessing:

```bash
# Build with default settings (auto-uses multiprocessing)
kg build

# Or specify custom exclusions
kg build . --exclude "venv,node_modules,.git,__pycache__,.pytest_cache,dist,build,*.egg-info"
```

**Expected performance:**
- Small projects (<100 files): < 10 seconds
- Medium projects (100-1000 files): 10-30 seconds
- Large projects (1000-5000 files): 30-60 seconds
- Very large projects (5000+ files): 1-2 minutes

## Usage

### CLI

The CLI provides commands for building, querying, and managing the knowledge graph.

#### Build Graph

```bash
# Build graph for current directory
kg build

# Build graph for specific directory
kg build /path/to/project

# Build with custom exclusions
kg build . --exclude "venv,node_modules,.git"

# Build with custom output path
kg build . --output /custom/path/graph.json
```

#### Query Dependencies

```bash
# Query dependencies for a function
kg query my_function

# Query with depth limit
kg query my_function --depth 10

# Query a class
kg query MyClass
```

#### Search

```bash
# Search for nodes
kg search "auth"

# Search by node type
kg search "user" --node-type function

# Search for classes
kg search "Service" --node-type class
```

#### Status

```bash
# Get graph statistics
kg status

# Output:
# === Knowledge Graph Status ===
# Files: 6
# Functions: 64
# Classes: 29
# Total Edges: 143
# Graph File: storage/graph.json
```

#### Watch Mode

```bash
# Watch for file changes and auto-update graph
kg watch

# Watch with custom graph path
kg watch --graph-path /custom/path/graph.json
```

#### API Server

```bash
# Start REST API server
kg serve

# Start on custom port
kg serve --port 8080

# Start with custom graph path
kg serve --graph-path /custom/path/graph.json
```

### REST API

Start the API server:

```bash
kg serve
```

The API will be available at `http://localhost:8000`

#### Endpoints

**GET /health**
```bash
curl http://localhost:8000/health
```

**GET /dependencies?target={name}&depth={depth}**
```bash
curl "http://localhost:8000/dependencies?target=my_function&depth=5"
```

**GET /search?query={text}&node_type={type}**
```bash
curl "http://localhost:8000/search?query=auth&node_type=function"
```

**GET /stats**
```bash
curl http://localhost:8000/stats
```

**GET /graph**
```bash
curl http://localhost:8000/graph
```

#### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get dependencies
response = requests.get(f"{BASE_URL}/dependencies", 
                       params={"target": "authenticate_user", "depth": 3})
deps = response.json()

# Search for nodes
response = requests.get(f"{BASE_URL}/search", 
                       params={"query": "user", "node_type": "function"})
results = response.json()

# Get statistics
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()
```

### MCP Server

The MCP server allows AI agents (like Kiro, Windsurf, Claude Desktop) to query the knowledge graph directly.

#### Start MCP Server

```bash
kg-mcp --graph-path storage/graph.json
```

Or using Python module:

```bash
python -m mcp.server --graph-path storage/graph.json
```

#### Configuration

Add to your IDE's MCP configuration:

**Kiro (Workspace Config):**
```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "python",
      "args": [
        "-m",
        "mcp.server",
        "--graph-path",
        "C:\\Users\\Himanshu_Verma\\DELL\\ADM\\storage\\graph.json"
      ],
      "cwd": "C:\\Users\\Himanshu_Verma\\DELL\\ADM"
    }
  }
}
```

**Windsurf:**
```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "kg-mcp",
      "args": ["--graph-path", "storage/graph.json"]
    }
  }
}
```

**Claude Desktop:**
```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "kg-mcp",
      "args": ["--graph-path", "storage/graph.json"]
    }
  }
}
```

#### MCP Methods

The MCP server exposes the following methods:

- `dependencies` - Get upstream/downstream dependencies
- `search` - Search for nodes in the graph
- `stats` - Get graph statistics
- `graph` - Get the complete graph

---

## Configuration

### Graph Storage

By default, the graph is stored in `storage/graph.json`. Customize the location:

```bash
kg build . --output /custom/path/graph.json
kg query my_function --graph-path /custom/path/graph.json
```

### File Exclusions

Exclude directories from parsing:

```bash
kg build . --exclude "venv,node_modules,.git,temp,cache,logs"
```

Default exclusions: `venv`, `env`, `.git`, `__pycache__`, `.pytest_cache`, `node_modules`, `dist`, `build`, `*.egg-info`

### Performance Tuning

#### Multiprocessing Workers

For very large codebases, adjust the number of parallel workers by modifying `core/multi_parser.py`:

```python
# In parse_directory method
max_workers=8  # Use 8 workers instead of default 4
```

#### File Size Limit

By default, files larger than 1MB are skipped. Adjust in `core/multi_parser.py`:

```python
# In _parse_file_worker method
if path.stat().st_size > 2 * 1024 * 1024:  # 2MB limit
    return None
```

### Watchdog Configuration

The watcher can be configured for debounce time and callback functions. See `core/watcher.py` for details.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Code Knowledge Graph                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │     CLI     │    │  FastAPI    │    │  MCP Server │      │
│  │  (typer)    │    │   Server    │    │  (stdio)    │      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │   Graph Retriever  │                      │
│                   │   (query engine)   │                      │
│                   └─────────┬─────────┘                      │
│                             │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │  Knowledge Graph   │                      │
│                   │  (nodes + edges)   │                      │
│                   └─────────┬─────────┘                      │
│                             │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │  Graph Builder    │                      │
│                   └─────────┬─────────┘                      │
│                             │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │ Multi-Language    │                      │
│                   │     Parser        │                      │
│                   │  (tree-sitter)    │                      │
│                   └─────────┬─────────┘                      │
│                             │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │  Python Files     │                      │
│                   │  TypeScript Files │                      │
│                   │  JavaScript Files │                      │
│                   └───────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Graph Schema

**Node Types:**
- `file` - Represents a source file
- `function` - Represents a function or method
- `class` - Represents a class

**Edge Types:**
- `defines` - File defines a function/class
- `imports` - File imports another file
- `calls` - Function calls another function

### Data Flow

1. **Parsing**: Multi-language parser extracts code structure
2. **Graph Building**: Graph builder creates nodes and edges
3. **Storage**: Graph serialized to JSON
4. **Querying**: Retriever queries the graph for relationships
5. **Serving**: CLI, API, and MCP server expose functionality

---

## Performance

### Benchmarks

| Project Size | Files | Functions | Classes | Build Time |
|-------------|-------|-----------|---------|------------|
| Small | < 100 | < 500 | < 100 | < 10s |
| Medium | 100-1000 | 500-5000 | 100-1000 | 10-30s |
| Large | 1000-5000 | 5000-25000 | 1000-5000 | 30-60s |
| Very Large | 5000+ | 25000+ | 5000+ | 1-2min |

### Optimization Features

- **Multiprocessing**: Parallel file parsing with up to 4 workers
- **Progress Reporting**: Shows parsing progress every 100 files
- **File Size Limits**: Skips files > 1MB to avoid memory issues
- **Smart Exclusions**: Automatically excludes common directories
- **Efficient Storage**: JSON-based graph storage for fast loading

### Performance Tips

1. **Use exclusions**: Exclude directories you don't need
   ```bash
   kg build . --exclude "tests,docs,examples"
   ```

2. **Build incrementally**: Build only the directories you're working on
   ```bash
   kg build src/  # Only build src directory
   ```

3. **Use the watcher**: Let the watcher update the graph as you work
   ```bash
   kg watch  # Auto-updates on file changes
   ```

---

## Use Cases

### 1. Code Navigation

Quickly find what functions a specific function calls, or what functions call it.

```bash
kg query authenticate_user
```

**Use case:** Understand code flow and dependencies quickly.

### 2. Impact Analysis

Before refactoring, understand the downstream impact of changing a function.

```bash
kg query process_payment --depth 10
```

**Use case:** Assess refactoring risk and identify affected components.

### 3. Code Review

Understand the relationships in a new codebase.

```bash
kg build /path/to/new/project
kg status
kg search "main"
```

**Use case:** Quickly understand structure of new codebases.

### 4. AI-Assisted Development

Provide AI agents with structured context about code relationships.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "dependencies",
  "params": {"target": "main"}
}
```

**Use case:** LLMs get precise context in < 100 tokens instead of loading entire files.

### 5. Dependency Visualization

Find the most connected components in your codebase.

```bash
kg status
```

**Use case:** Identify central components that need attention.

### 6. Import Chain Analysis

Track how modules import each other.

```bash
kg query "module_name" --node-type file
```

**Use case:** Understand module dependencies and identify circular imports.

---

## LLM Integration

### How LLMs Use the Knowledge Graph

The knowledge graph provides LLMs with structured, relevant code context instead of loading entire files, resulting in **10-100x token reduction**.

### LLM Workflow Examples

#### Code Understanding

**LLM Request:** "How does the authentication system work?"

**With Knowledge Graph:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "search",
  "params": {"query": "auth"}
}
```

**Response:**
```json
{
  "result": {
    "results": [
      {"name": "authenticate_user", "type": "function", "file": "auth.py"},
      {"name": "verify_token", "type": "function", "file": "auth.py"}
    ]
  }
}
```

#### Refactoring Assistance

**LLM Request:** "I need to refactor the payment processing function"

**With Knowledge Graph:**
```json
{
  "method": "dependencies",
  "params": {
    "target": "process_payment",
    "depth": 10
  }
}
```

**Response:**
```json
{
  "result": {
    "downstream": [
      {"name": "checkout", "type": "function"},
      {"name": "subscription_renewal", "type": "function"},
      {"name": "refund_handler", "type": "function"}
    ]
  }
}
```

#### Debugging Support

**LLM Request:** "Why is this error happening in the data pipeline?"

**With Knowledge Graph:**
```json
{
  "method": "dependencies",
  "params": {
    "target": "process_data",
    "depth": 5
  }
}
```

**Response:**
```json
{
  "result": {
    "upstream": [
      {"name": "validate_input", "type": "function"},
      {"name": "transform_data", "type": "function"},
      {"name": "load_config", "type": "function"}
    ]
  }
}
```

### Benefits for LLMs

1. **Context Awareness**: Understands code relationships, not just syntax
2. **Precision**: Gets exactly what's needed, not everything
3. **Speed**: Graph queries are milliseconds vs. parsing files
4. **Scalability**: Works on huge codebases without context overflow
5. **Consistency**: Same graph ensures consistent understanding across sessions

### API Integration for LLMs

LLMs can also call the REST API directly:

```python
import requests

response = requests.get(
    "http://localhost:8000/dependencies",
    params={"target": "authenticate_user", "depth": 3}
)

data = response.json()
print(f"Upstream: {data['upstream']}")
print(f"Downstream: {data['downstream']}")
```

---

## API Reference

### REST API Endpoints

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET /dependencies

Get upstream and downstream dependencies for a target.

**Parameters:**
- `target` (required): Name of the function/class to query
- `depth` (optional): Depth of dependency traversal (default: 5)

**Response:**
```json
{
  "target": "my_function",
  "upstream": [
    {"name": "dependency1", "type": "function", "file": "file1.py"}
  ],
  "downstream": [
    {"name": "caller1", "type": "function", "file": "file2.py"}
  ],
  "upstream_count": 1,
  "downstream_count": 1
}
```

#### GET /search

Search for nodes in the knowledge graph.

**Parameters:**
- `query` (required): Search query string
- `node_type` (optional): Filter by node type (file, function, class)

**Response:**
```json
{
  "query": "auth",
  "count": 5,
  "results": [
    {"name": "authenticate", "type": "function", "file": "auth.py"}
  ]
}
```

#### GET /stats

Get graph statistics.

**Response:**
```json
{
  "stats": {
    "files": 10,
    "functions": 50,
    "classes": 20,
    "edges": 100
  }
}
```

#### GET /graph

Get the complete knowledge graph.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

### MCP Server Methods

#### dependencies

Get upstream and downstream dependencies.

**Parameters:**
- `target` (required): Target name
- `depth` (optional): Depth of traversal (default: 5)

#### search

Search for nodes in the graph.

**Parameters:**
- `query` (required): Search query
- `node_type` (optional): Filter by node type

#### stats

Get graph statistics.

**Parameters:** None

#### graph

Get the complete graph.

**Parameters:** None

---

## Contributing

We welcome contributions! Please follow these guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/userhimanshuverma/code-knowledge-graph-hv.git
cd code-knowledge-graph-hv

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=core --cov=api --cov=cli --cov=mcp
```

### Code Style

We use `black` for formatting and `ruff` for linting:

```bash
black .
ruff check .
```

### Adding New Features

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Adding Language Support

To add support for a new language:

1. Add the tree-sitter language dependency to `pyproject.toml`
2. Add the file extension to `LANGUAGE_PARSERS` in `core/multi_parser.py`
3. Implement the parser method in `MultiLanguageParser`
4. Add tests for the new language
5. Update documentation

### Bug Reports

When reporting bugs, please include:
- Python version
- Package version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

---

## Security

### Data Privacy

- The graph stores file paths and code structure (function names, line numbers), not actual code content
- No external network calls are made
- All operations are local to your machine
- No code content is transmitted to external services

### Best Practices

- Don't commit the `storage/graph.json` file to public repositories (it contains file paths)
- Use `.gitignore` to exclude graph files
- Review the graph file before sharing to ensure no sensitive file paths are included

### Vulnerability Reporting

If you discover a security vulnerability, please report it privately to the maintainers.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Changelog

### Version 2.0.0 (2026-05-01)

**Major Release - Multi-language Support**

- ✨ Added multi-language support (Python, TypeScript, JavaScript, JSX, TSX)
- ✨ Implemented tree-sitter-based parsing for non-Python languages
- ✨ Added MultiLanguageParser with parallel processing
- ✨ Updated import resolution for TypeScript/JavaScript
- 🐛 Fixed MCP protocol implementation (tools/list, resources/list)
- 📚 Updated documentation with multi-language examples

### Version 1.0.3 (2026-05-01)

**Bug Fixes**

- 🐛 Fixed MCP server to implement proper protocol handshake
- ✨ Added tools/list, resources/list, resources/templates/list methods
- 📚 Added Kiro IDE configuration to README

### Version 1.0.2 (2026-05-01)

**Performance Improvements**

- ⚡ Added multiprocessing support for parallel file parsing
- ⚡ Implemented progress reporting during parsing
- ⚡ Added file size limits to avoid memory issues
- ⚡ Improved exclusions for common directories

### Version 1.0.1 (2026-05-01)

**Initial Release**

- ✨ Initial release with Python AST parsing
- ✨ CLI, REST API, and MCP server
- ✨ Graph builder and retriever
- ✨ File watching with watchdog
- ✨ Comprehensive documentation

---

## Roadmap

### Planned Features

- [ ] Additional language support (Java, Go, Rust, C/C++, Ruby, PHP)
- [ ] Graph visualization (export to Graphviz, Mermaid)
- [ ] Web UI for graph exploration
- [ ] Advanced query language (GraphQL-like)
- [ ] Code smell detection
- [ ] Dependency cycle detection
- [ ] Integration with popular IDEs (VS Code, JetBrains)
- [ ] Cloud storage support (S3, GCS)
- [ ] Collaboration features (shared graphs)
- [ ] Performance analytics dashboard

### Community Requests

If you have feature requests, please open an issue on GitHub.

---

## Support

### Documentation

- [README](https://github.com/userhimanshuverma/code-knowledge-graph-hv) - This file
- [API Documentation](https://github.com/userhimanshuverma/code-knowledge-graph-hv) - API reference
- [Examples](https://github.com/userhimanshuverma/code-knowledge-graph-hv) - Usage examples

### Issues

For bug reports and feature requests, please open an issue on GitHub:
https://github.com/userhimanshuverma/code-knowledge-graph-hv/issues

### Discussions

For questions and discussions, use GitHub Discussions:
https://github.com/userhimanshuverma/code-knowledge-graph-hv/discussions

### PyPI

Package information and downloads:
https://pypi.org/project/code-knowledge-graph-hv/

---

## Acknowledgments

- Built with Python AST for reliable Python parsing
- Uses [tree-sitter](https://tree-sitter.github.io/) for multi-language parsing
- Uses [watchdog](https://python-watchdog.readthedocs.io/) for file system monitoring
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- Uses [Typer](https://typer.tiangolo.com/) for the CLI
- Uses [MCP](https://modelcontextprotocol.io/) protocol for AI agent integration

---

**Made with ❤️ for developers and AI agents**

**Star us on GitHub:** ⭐ https://github.com/userhimanshuverma/code-knowledge-graph-hv
