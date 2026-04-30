# Code Knowledge Graph Engine

[![PyPI version](https://badge.fury.io/py/code-knowledge-graph-hv.svg)](https://badge.fury.io/py/code-knowledge-graph-hv)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight, production-grade knowledge graph engine for codebases. Build and maintain an always-updated graph of code relationships (functions, classes, imports, calls) and query it via CLI, API, or MCP (Model Context Protocol) for AI-assisted development.

## 🎯 Goals

- **Reduce LLM token usage**: Retrieve only relevant code relationships instead of entire files (10-100x token reduction)
- **Always-updated graph**: Auto-update on file changes with built-in watcher
- **Plug-and-play**: Easy integration into any project with a single command
- **Multiple interfaces**: CLI, REST API, and MCP server for AI agents
- **Extensible**: Simple architecture for enterprise customization
- **Performance optimized**: Multiprocessing support for large codebases (5000+ files in ~1 minute)

## 🏗️ Architecture

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
│                   │  Python Parser    │                      │
│                   │    (AST-based)    │                      │
│                   └─────────┬─────────┘                      │
│                             │                                 │
│                   ┌─────────▼─────────┐                      │
│                   │  File Watcher     │                      │
│                   │   (watchdog)      │                      │
│                   └───────────────────┘                      │
│                             │                                 │
│                    ┌────────▼────────┐                       │
│                    │  Python Files   │                       │
│                    └─────────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Install from PyPI (Recommended)

```bash
pip install code-knowledge-graph-hv
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/code-knowledge-graph.git
cd code-knowledge-graph

# Install with pip
pip install .
```

### Development installation

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

## ⚙️ Setup Guide

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

## 🚀 Quick Start

### 1. Build the knowledge graph

```bash
# Build graph for current directory
kg build

# Build graph for specific directory
kg build /path/to/project

# Exclude certain directories
kg build . --exclude "venv,node_modules,.git"
```

### 2. Query dependencies

```bash
# Query dependencies for a function
kg query my_function

# Query with custom depth
kg query my_function --depth 3

# Save output to file
kg query my_function --output deps.json
```

### 3. Start the watcher (auto-update)

```bash
# Watch current directory
kg watch

# Watch specific directory
kg watch /path/to/project
```

### 4. Check status

```bash
kg status
```

### 5. Search nodes

```bash
# Search for nodes
kg search "user"

# Filter by type
kg search "user" --node-type function
```

## 🌐 API Server

### Start the server

```bash
kg serve --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Dependencies
```bash
GET /dependencies?target=function_name&depth=5
```

#### Get Full Graph
```bash
GET /graph
```

#### Get Statistics
```bash
GET /stats
```

#### Search Nodes
```bash
GET /search?query=search_term&node_type=function
```

#### Get Function Calls
```bash
GET /functions/{function_name}/calls
```

#### Get File Imports
```bash
GET /files/{file_path}/imports
```

### Example using curl

```bash
# Get dependencies
curl "http://localhost:8000/dependencies?target=my_function"

# Get stats
curl http://localhost:8000/stats

# Search
curl "http://localhost:8000/search?query=user"
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get dependencies for a function
response = requests.get(f"{BASE_URL}/dependencies", 
                       params={"target": "authenticate_user", "depth": 3})
deps = response.json()
print(f"Upstream: {len(deps['upstream'])} dependencies")
print(f"Downstream: {len(deps['downstream'])} dependents")

# Search for nodes
response = requests.get(f"{BASE_URL}/search", 
                       params={"query": "user", "node_type": "function"})
results = response.json()
for node in results['results']:
    print(f"Found: {node['name']} in {node['file']}")

# Get graph statistics
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()
print(f"Total files: {stats['stats']['files']}")
print(f"Total functions: {stats['stats']['functions']}")
```

## 🔌 MCP Server (Model Context Protocol)

The MCP server allows AI agents (like Windsurf, Claude Desktop) to query the knowledge graph directly.

### Start MCP server

```bash
kg-mcp --graph-path storage/graph.json
```

### MCP Methods

#### `dependencies`
Get upstream and downstream dependencies for a target.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "dependencies",
  "params": {
    "target": "my_function",
    "depth": 5
  }
}
```

#### `search`
Search for nodes in the graph.

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "search",
  "params": {
    "query": "user",
    "node_type": "function"
  }
}
```

#### `stats`
Get graph statistics.

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "stats"
}
```

#### `graph`
Get the complete graph.

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "graph"
}
```

### Integration with AI Tools

#### Windsurf Configuration

Add to your Windsurf config (usually `.windsurf/config.json`):

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

#### Claude Desktop Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

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

#### Cursor Configuration

Add to your Cursor settings:

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

## 🤖 LLM Integration Guide

### How LLMs Use the Knowledge Graph

The knowledge graph provides LLMs with structured, relevant code context instead of loading entire files, resulting in **10-100x token reduction**.

### LLM Workflow Examples

#### 1. Code Understanding

**LLM Request:** "How does the authentication system work?"

**Without Knowledge Graph:**
- LLM loads entire auth-related files (thousands of tokens)
- Parses through irrelevant code
- Wastes context window

**With Knowledge Graph:**
```json
// LLM calls MCP server
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "search",
  "params": {"query": "auth"}
}

// Server returns relevant functions and relationships
{
  "result": {
    "results": [
      {"name": "authenticate_user", "type": "function", "file": "auth.py"},
      {"name": "verify_token", "type": "function", "file": "auth.py"}
    ]
  }
}

// LLM queries dependencies
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "dependencies",
  "params": {"target": "authenticate_user", "depth": 3}
}

// Gets complete call chain in < 100 tokens
```

#### 2. Refactoring Assistance

**LLM Request:** "I need to refactor the payment processing function"

**With Knowledge Graph:**
```json
// LLM first checks impact
{
  "method": "dependencies",
  "params": {
    "target": "process_payment",
    "depth": 10
  }
}

// Server returns downstream dependents
{
  "result": {
    "downstream": [
      {"name": "checkout", "type": "function"},
      {"name": "subscription_renewal", "type": "function"},
      {"name": "refund_handler", "type": "function"}
    ]
  }
}

// LLM understands impact before making changes
```

#### 3. Debugging Support

**LLM Request:** "Why is this error happening in the data pipeline?"

**With Knowledge Graph:**
```json
// LLM traces the call chain
{
  "method": "dependencies",
  "params": {
    "target": "process_data",
    "depth": 5
  }
}

// Gets upstream dependencies
{
  "result": {
    "upstream": [
      {"name": "validate_input", "type": "function"},
      {"name": "transform_data", "type": "function"},
      {"name": "load_config", "type": "function"}
    ]
  }
}

// LLM can trace error source efficiently
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

# LLM makes HTTP request
response = requests.get(
    "http://localhost:8000/dependencies",
    params={"target": "authenticate_user", "depth": 3}
)

# Gets structured JSON response
data = response.json()
print(f"Upstream: {data['upstream']}")
print(f"Downstream: {data['downstream']}")
```

## 📊 Graph Schema

### Node Types

- **file**: Represents a Python source file
- **function**: Represents a function or method
- **class**: Represents a class

### Edge Types

- **calls**: Function A calls Function B
- **imports**: File A imports File B
- **defines**: File defines Function/Class

### Example Graph

```json
{
  "nodes": {
    "file:main.py": {
      "id": "file:main.py",
      "type": "file",
      "name": "main.py",
      "file_path": "main.py",
      "line_number": 1
    },
    "function:process_data:main.py": {
      "id": "function:process_data:main.py",
      "type": "function",
      "name": "process_data",
      "file_path": "main.py",
      "line_number": 10
    }
  },
  "edges": [
    {
      "source": "file:main.py",
      "target": "function:process_data:main.py",
      "type": "defines"
    }
  ]
}
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=core --cov=api --cov=cli --cov=mcp
```

## 🔧 Configuration

### Storage

The graph is stored in JSON format at `storage/graph.json` by default. You can customize this path:

```bash
kg build . --output /custom/path/graph.json
kg query my_function --graph-path /custom/path/graph.json
```

### Exclude Directories

When building the graph, certain directories are excluded by default:
- `venv`, `env`, `.git`, `__pycache__`, `.pytest_cache`, `node_modules`

You can customize this:

```bash
kg build . --exclude "custom_dir,another_dir"
```

## 🎨 Use Cases

### 1. Code Navigation

Quickly find what functions a specific function calls, or what functions call it.

```bash
kg query authenticate_user
```

**Output:**
```
=== Dependencies for 'authenticate_user' ===

Upstream (5):
  - validate_credentials (function) @ auth.py:45
  - check_rate_limit (function) @ auth.py:120
  - load_user_session (function) @ auth.py:200

Downstream (12):
  - login_handler (function) @ routes.py:50
  - api_authenticate (function) @ api.py:100
  - refresh_token (function) @ auth.py:350
```

### 2. Impact Analysis

Before refactoring, understand the downstream impact of changing a function.

```bash
kg query process_payment --depth 10
```

**Use case:** Before changing `process_payment`, check which functions depend on it to ensure no breaking changes.

### 3. Code Review

Understand the relationships in a new codebase.

```bash
kg build /path/to/new/project
kg status
kg search "main"
```

**Use case:** Quickly understand the structure of a new codebase by finding main entry points and their dependencies.

### 4. AI-Assisted Development

Provide AI agents with structured context about code relationships instead of raw files.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "dependencies",
  "params": {"target": "main"}
}
```

**Benefit:** LLMs get precise context in < 100 tokens instead of loading entire files (thousands of tokens).

### 5. Dependency Visualization

Find the most connected components in your codebase.

```bash
kg status
```

**Output:**
```
=== Most Connected Nodes ===
1. main.py (file) - 48 connections
2. auth_service.py (file) - 32 connections
3. database.py (file) - 28 connections
```

**Use case:** Identify central components that might need extra attention or refactoring.

### 6. Import Chain Analysis

Track how modules import each other.

```bash
kg query "module_name" --node-type file
```

**Use case:** Understand module dependencies and identify circular imports.

## 🔧 Advanced Configuration

### Custom Storage Location

```bash
kg build . --output /custom/path/graph.json
kg query my_function --graph-path /custom/path/graph.json
```

### Custom Exclude Patterns

```bash
kg build . --exclude "venv,node_modules,.git,temp,cache,logs"
```

### Adjusting Multiprocessing Workers

For very large codebases, you can adjust the number of parallel workers by modifying the parser settings in `core/parser.py`:

```python
# In parse_directory method
max_workers=8  # Use 8 workers instead of default 4
```

### File Size Limit

By default, files larger than 1MB are skipped. To adjust this:

```python
# In _parse_file_worker method
if path.stat().st_size > 2 * 1024 * 1024:  # 2MB limit
    return None
```

## ⚡ Performance Optimization

### Built-in Optimizations

The tool includes several performance optimizations:

1. **Multiprocessing**: Parallel file parsing with up to 4 workers
2. **Progress Reporting**: Shows parsing progress every 100 files
3. **File Size Limits**: Skips files > 1MB to avoid memory issues
4. **Smart Exclusions**: Automatically excludes common directories
5. **Efficient AST**: Uses Python's built-in AST parser

### Performance Benchmarks

| Project Size | Files | Functions | Build Time |
|-------------|-------|-----------|------------|
| Small | < 100 | < 500 | < 10s |
| Medium | 100-1000 | 500-5000 | 10-30s |
| Large | 1000-5000 | 5000-25000 | 30-60s |
| Very Large | 5000+ | 25000+ | 1-2min |

### Tips for Large Codebases

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

## 🐛 Troubleshooting

### Common Issues

#### Issue: "kg command not found"

**Solution:** Use Python module invocation instead:
```bash
python -m cli.main build
```

Or add Python Scripts to your PATH and reinstall:
```bash
pip install --force-reinstall code-knowledge-graph-hv
```

#### Issue: Build taking too long

**Solution:** Add more exclusions:
```bash
kg build . --exclude "venv,node_modules,.git,__pycache__,.pytest_cache,dist,build,*.egg-info,tests,docs"
```

#### Issue: "Graph file not found"

**Solution:** Build the graph first:
```bash
kg build
```

#### Issue: "Syntax error in file"

**Solution:** The parser skips files with syntax errors. Check the file for syntax issues or exclude it:
```bash
kg build . --exclude "problematic_directory"
```

#### Issue: MCP server not responding

**Solution:** Ensure the graph file exists:
```bash
kg build
kg-mcp --graph-path storage/graph.json
```

#### Issue: API server not starting

**Solution:** Check if port 8000 is already in use:
```bash
kg serve --port 8001  # Use different port
```

### Debug Mode

For debugging, you can add verbose output:

```bash
python -m cli.main build --verbose
```

## 📈 Performance Monitoring

### Check Build Performance

```bash
# Time the build command
time kg build
```

### Monitor Graph Size

```bash
kg status
# Check the number of nodes and edges
```

### Optimize for Your Use Case

- **For CI/CD**: Build once, cache the graph file
- **For Development**: Use the watcher for auto-updates
- **For Large Projects**: Use exclusions to reduce scope

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Build Knowledge Graph

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install code-knowledge-graph-hv
      - name: Build graph
        run: kg build --exclude "tests,docs"
      - name: Upload graph artifact
        uses: actions/upload-artifact@v2
        with:
          name: knowledge-graph
          path: storage/graph.json
```

### Pre-commit Hook

Add a pre-commit hook to keep the graph updated:

```bash
# .git/hooks/pre-commit
#!/bin/bash
kg build
git add storage/graph.json
```

## 🤝 Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/code-knowledge-graph.git
cd code-knowledge-graph

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

### Bug Reports

When reporting bugs, please include:
- Python version
- Package version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

## ❓ FAQ

### Q: Does this work with languages other than Python?

A: Currently, only Python is supported. The parser uses Python's AST module. Support for other languages can be added by implementing new parsers.

### Q: Can I use this with monorepos?

A: Yes! Build the graph for each package separately or build the entire monorepo with appropriate exclusions.

### Q: How much disk space does the graph use?

A: Typically 1-10MB for most projects, depending on the number of files and relationships.

### Q: Is the graph secure?

A: Yes. The graph stores file paths and code structure (function names, line numbers), not actual code content. No external network calls are made.

### Q: Can I extend the parser to extract more information?

A: Yes! The parser is modular. You can extend the `CodeVisitor` class in `core/parser.py` to extract additional information.

### Q: How do I update the graph after code changes?

A: Either rebuild with `kg build` or use the watcher for auto-updates: `kg watch`

### Q: Can I query the graph programmatically?

A: Yes! Use the API server or import the modules directly:
```python
from core.graph_builder import GraphBuilder
from core.retriever import GraphRetriever

builder = GraphBuilder()
graph = builder.load_graph()
retriever = GraphRetriever(graph)
deps = retriever.get_dependencies("my_function")
```

## 🔒 Security

- The graph stores file paths and code structure, not actual code content
- No external network calls
- All operations are local
- No code content is transmitted to external services

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with Python AST for reliable parsing
- Uses watchdog for file system monitoring
- FastAPI for the REST API
- Typer for the CLI
- MCP protocol for AI agent integration

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub at:
https://github.com/yourusername/code-knowledge-graph/issues

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for developers and AI agents**
