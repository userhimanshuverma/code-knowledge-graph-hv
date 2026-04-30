"""Multi-language parser using tree-sitter for code analysis."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

try:
    import tree_sitter
    import tree_sitter_python
    import tree_sitter_typescript
    import tree_sitter_javascript
except ImportError:
    tree_sitter = None


@dataclass
class ParsedFile:
    """Result of parsing a single file."""
    file_path: str
    language: str
    functions: List[Dict[str, any]]
    classes: List[Dict[str, any]]
    imports: List[Dict[str, any]]
    function_calls: List[Dict[str, any]]


class MultiLanguageParser:
    """Parse files from multiple programming languages."""
    
    LANGUAGE_PARSERS = {
        '.py': 'python',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.js': 'javascript',
        '.jsx': 'jsx',
    }
    
    def __init__(self):
        self.parsed_files: Dict[str, ParsedFile] = {}
        self._init_tree_sitter()
    
    def _init_tree_sitter(self):
        """Initialize tree-sitter parsers."""
        if tree_sitter is None:
            print("Warning: tree-sitter not installed. Only Python files will be parsed.", file=sys.stderr)
            self.ts_parser = None
            self.js_parser = None
            self.py_tree_parser = None
            return
        
        try:
            self.ts_parser = tree_sitter.Parser()
            self.ts_parser.set_language(tree_sitter_typescript.language())
            
            self.js_parser = tree_sitter.Parser()
            self.js_parser.set_language(tree_sitter_javascript.language())
            
            self.py_tree_parser = tree_sitter.Parser()
            self.py_tree_parser.set_language(tree_sitter_python.language())
        except Exception as e:
            print(f"Warning: Failed to initialize tree-sitter parsers: {e}", file=sys.stderr)
            self.ts_parser = None
            self.js_parser = None
            self.py_tree_parser = None
    
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        """Parse a single file based on its extension."""
        path = Path(file_path)
        if not path.exists():
            return None
        
        ext = path.suffix.lower()
        if ext not in self.LANGUAGE_PARSERS:
            return None
        
        language = self.LANGUAGE_PARSERS[ext]
        
        if language == 'python':
            return self._parse_python_file(file_path)
        elif language in ['typescript', 'tsx']:
            return self._parse_typescript_file(file_path, language)
        elif language in ['javascript', 'jsx']:
            return self._parse_javascript_file(file_path, language)
        
        return None
    
    def _parse_python_file(self, file_path: str) -> Optional[ParsedFile]:
        """Parse a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            parsed = ParsedFile(
                file_path=file_path,
                language='python',
                functions=[],
                classes=[],
                imports=[],
                function_calls=[]
            )
            
            visitor = PythonCodeVisitor(file_path, parsed)
            visitor.visit(tree)
            
            return parsed
            
        except SyntaxError as e:
            return None
        except Exception as e:
            return None
    
    def _parse_typescript_file(self, file_path: str, language: str) -> Optional[ParsedFile]:
        """Parse a TypeScript/TSX file using tree-sitter."""
        if self.ts_parser is None:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = self.ts_parser.parse(content.encode('utf-8'))
            
            parsed = ParsedFile(
                file_path=file_path,
                language=language,
                functions=[],
                classes=[],
                imports=[],
                function_calls=[]
            )
            
            self._traverse_tree(tree.root_node, parsed, file_path)
            
            return parsed
            
        except Exception as e:
            return None
    
    def _parse_javascript_file(self, file_path: str, language: str) -> Optional[ParsedFile]:
        """Parse a JavaScript/JSX file using tree-sitter."""
        if self.js_parser is None:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = self.js_parser.parse(content.encode('utf-8'))
            
            parsed = ParsedFile(
                file_path=file_path,
                language=language,
                functions=[],
                classes=[],
                imports=[],
                function_calls=[]
            )
            
            self._traverse_tree(tree.root_node, parsed, file_path)
            
            return parsed
            
        except Exception as e:
            return None
    
    def _traverse_tree(self, node, parsed: ParsedFile, file_path: str, current_class: Optional[str] = None, current_function: Optional[str] = None):
        """Traverse tree-sitter tree to extract code structure."""
        if node.type in ['function_declaration', 'function_definition', 'method_definition']:
            func_name = self._extract_name(node)
            if func_name:
                name = f"{current_class}.{func_name}" if current_class else func_name
                parsed.functions.append({
                    'name': name,
                    'line_number': node.start_point[0] + 1,
                    'file_path': file_path,
                    'args': [],
                    'is_method': current_class is not None
                })
                current_function = name
        
        elif node.type == 'class_declaration':
            class_name = self._extract_name(node)
            if class_name:
                parsed.classes.append({
                    'name': class_name,
                    'line_number': node.start_point[0] + 1,
                    'file_path': file_path,
                    'methods': []
                })
                current_class = class_name
        
        elif node.type == 'import_statement':
            self._extract_import(node, parsed, file_path)
        
        elif node.type == 'call_expression':
            if current_function:
                call_name = self._extract_call_name(node)
                if call_name:
                    parsed.function_calls.append({
                        'caller': current_function,
                        'callee': call_name,
                        'line_number': node.start_point[0] + 1,
                        'file_path': file_path
                    })
        
        # Recursively traverse children
        for child in node.children:
            self._traverse_tree(child, parsed, file_path, current_class, current_function)
    
    def _extract_name(self, node) -> Optional[str]:
        """Extract name from a tree-sitter node."""
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf-8')
        return None
    
    def _extract_call_name(self, node) -> Optional[str]:
        """Extract function name from a call expression."""
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf-8')
            elif child.type == 'member_expression':
                return self._extract_member_expression(child)
        return None
    
    def _extract_member_expression(self, node) -> Optional[str]:
        """Extract member expression (e.g., obj.method)."""
        parts = []
        for child in node.children:
            if child.type == 'identifier':
                parts.append(child.text.decode('utf-8'))
            elif child.type == 'member_expression':
                parts.append(self._extract_member_expression(child))
        return '.'.join(reversed(parts)) if parts else None
    
    def _extract_import(self, node, parsed: ParsedFile, file_path: str):
        """Extract import statement."""
        import_name = None
        for child in node.children:
            if child.type in ['string', 'identifier']:
                import_name = child.text.decode('utf-8').strip('"\'')
                break
        
        if import_name:
            parsed.imports.append({
                'name': import_name,
                'alias': None,
                'line_number': node.start_point[0] + 1,
                'file_path': file_path,
                'from_import': False
            })
    
    def parse_directory(self, directory: str, exclude_dirs: Optional[List[str]] = None, parallel: bool = True, max_workers: Optional[int] = None) -> Dict[str, ParsedFile]:
        """Parse all supported files in a directory recursively."""
        if exclude_dirs is None:
            exclude_dirs = ['venv', 'env', '.git', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build', '*.egg-info']
        
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return {}
        
        self.parsed_files.clear()
        
        # Collect all supported files
        supported_files = []
        for ext in self.LANGUAGE_PARSERS.keys():
            for file_path in path.rglob(f'*{ext}'):
                # Skip excluded directories
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue
                supported_files.append(str(file_path))
        
        total_files = len(supported_files)
        if total_files == 0:
            return self.parsed_files
        
        print(f"Parsing {total_files} files ({self._count_by_language(supported_files)})...")
        
        if parallel and total_files > 10:
            self._parse_parallel(supported_files, max_workers)
        else:
            self._parse_sequential(supported_files)
        
        return self.parsed_files
    
    def _count_by_language(self, files: List[str]) -> Dict[str, int]:
        """Count files by language."""
        counts = {}
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            lang = self.LANGUAGE_PARSERS.get(ext, 'unknown')
            counts[lang] = counts.get(lang, 0) + 1
        return counts
    
    def _parse_sequential(self, files: List[str]) -> None:
        """Parse files sequentially."""
        for i, file_path in enumerate(files, 1):
            parsed = self.parse_file(file_path)
            if parsed:
                self.parsed_files[file_path] = parsed
            
            if i % 100 == 0:
                print(f"Progress: {i}/{len(files)} files parsed")
        
        print(f"Completed: {len(files)} files parsed")
    
    def _parse_parallel(self, files: List[str], max_workers: Optional[int]) -> None:
        """Parse files in parallel."""
        if max_workers is None:
            max_workers = min(4, len(files))
        
        completed = 0
        total = len(files)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self._parse_file_worker, file_path): file_path for file_path in files}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        self.parsed_files[file_path] = result
                except Exception as e:
                    pass
                
                completed += 1
                if completed % 100 == 0:
                    print(f"Progress: {completed}/{total} files parsed")
        
        print(f"Completed: {completed}/{total} files parsed")
    
    @staticmethod
    def _parse_file_worker(file_path: str) -> Optional[ParsedFile]:
        """Worker function for multiprocessing."""
        parser = MultiLanguageParser()
        return parser.parse_file(file_path)
    
    def get_all_functions(self) -> List[Dict[str, any]]:
        """Get all functions from all parsed files."""
        functions = []
        for parsed in self.parsed_files.values():
            functions.extend(parsed.functions)
        return functions
    
    def get_all_classes(self) -> List[Dict[str, any]]:
        """Get all classes from all parsed files."""
        classes = []
        for parsed in self.parsed_files.values():
            classes.extend(parsed.classes)
        return classes
    
    def get_all_imports(self) -> List[Dict[str, any]]:
        """Get all imports from all parsed files."""
        imports = []
        for parsed in self.parsed_files.values():
            imports.extend(parsed.imports)
        return imports


class PythonCodeVisitor(ast.NodeVisitor):
    """AST visitor for Python code (used for backward compatibility)."""
    
    def __init__(self, file_path: str, parsed: ParsedFile):
        self.file_path = file_path
        self.parsed = parsed
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        func_name = node.name
        if self.current_class:
            func_name = f"{self.current_class}.{func_name}"
        
        self.parsed.functions.append({
            'name': func_name,
            'line_number': node.lineno,
            'file_path': self.file_path,
            'args': [arg.arg for arg in node.args.args],
            'is_method': self.current_class is not None
        })
        
        old_function = self.current_function
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        class_name = node.name
        
        self.parsed.classes.append({
            'name': class_name,
            'line_number': node.lineno,
            'file_path': self.file_path,
            'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        })
        
        old_class = self.current_class
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            self.parsed.imports.append({
                'name': alias.name,
                'alias': alias.asname,
                'line_number': node.lineno,
                'file_path': self.file_path,
                'from_import': False
            })
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from import statement."""
        module = node.module if node.module else ''
        for alias in node.names:
            self.parsed.imports.append({
                'name': f"{module}.{alias.name}" if module else alias.name,
                'alias': alias.asname,
                'line_number': node.lineno,
                'file_path': self.file_path,
                'from_import': True
            })
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call."""
        if self.current_function:
            func_name = self._extract_call_name(node)
            if func_name:
                self.parsed.function_calls.append({
                    'caller': self.current_function,
                    'callee': func_name,
                    'line_number': node.lineno,
                    'file_path': self.file_path
                })
        
        self.generic_visit(node)
    
    def _extract_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract the name of the function being called."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return self._extract_attribute_name(node.func)
        return None
    
    def _extract_attribute_name(self, node: ast.Attribute) -> str:
        """Extract full attribute name (e.g., obj.method)."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._extract_attribute_name(node.value)}.{node.attr}"
        return node.attr
