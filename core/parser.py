"""AST-based parser for Python code."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys


@dataclass
class ParsedFile:
    """Result of parsing a single file."""
    file_path: str
    functions: List[Dict[str, any]]
    classes: List[Dict[str, any]]
    imports: List[Dict[str, any]]
    function_calls: List[Dict[str, any]]


class PythonParser:
    """Parse Python files using AST."""
    
    def __init__(self):
        self.parsed_files: Dict[str, ParsedFile] = {}
    
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        """Parse a single Python file."""
        try:
            path = Path(file_path)
            if not path.exists() or not path.suffix == '.py':
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            parsed = ParsedFile(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                function_calls=[]
            )
            
            # Visit the AST
            visitor = CodeVisitor(file_path, parsed)
            visitor.visit(tree)
            
            self.parsed_files[file_path] = parsed
            return parsed
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def parse_directory(self, directory: str, exclude_dirs: Optional[List[str]] = None, parallel: bool = True, max_workers: Optional[int] = None) -> Dict[str, ParsedFile]:
        """Parse all Python files in a directory recursively."""
        if exclude_dirs is None:
            exclude_dirs = ['venv', 'env', '.git', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build', '*.egg-info']
        
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return {}
        
        self.parsed_files.clear()
        
        # Collect all Python files
        py_files = []
        for py_file in path.rglob('*.py'):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in exclude_dirs):
                continue
            py_files.append(str(py_file))
        
        total_files = len(py_files)
        if total_files == 0:
            return self.parsed_files
        
        print(f"Parsing {total_files} Python files...")
        
        if parallel and total_files > 10:
            # Use multiprocessing for large codebases
            self._parse_parallel(py_files, max_workers)
        else:
            # Sequential parsing for small codebases
            self._parse_sequential(py_files)
        
        return self.parsed_files
    
    def _parse_sequential(self, py_files: List[str]) -> None:
        """Parse files sequentially with progress reporting."""
        for i, file_path in enumerate(py_files, 1):
            parsed = self.parse_file(file_path)
            if parsed:
                self.parsed_files[file_path] = parsed
            
            # Progress reporting every 100 files
            if i % 100 == 0:
                print(f"Progress: {i}/{len(py_files)} files parsed")
        
        print(f"Completed: {len(py_files)} files parsed")
    
    def _parse_parallel(self, py_files: List[str], max_workers: Optional[int]) -> None:
        """Parse files in parallel using multiprocessing."""
        if max_workers is None:
            max_workers = min(4, len(py_files))  # Use up to 4 workers
        
        completed = 0
        total = len(py_files)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all parsing tasks
            future_to_file = {executor.submit(self._parse_file_worker, file_path): file_path for file_path in py_files}
            
            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        self.parsed_files[file_path] = result
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
                
                completed += 1
                # Progress reporting every 100 files
                if completed % 100 == 0:
                    print(f"Progress: {completed}/{total} files parsed")
        
        print(f"Completed: {completed}/{total} files parsed")
    
    @staticmethod
    def _parse_file_worker(file_path: str) -> Optional[ParsedFile]:
        """Worker function for multiprocessing - parses a single file."""
        try:
            path = Path(file_path)
            if not path.exists() or not path.suffix == '.py':
                return None
            
            # Skip files larger than 1MB to avoid memory issues
            if path.stat().st_size > 1024 * 1024:  # 1MB
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            parsed = ParsedFile(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                function_calls=[]
            )
            
            visitor = CodeVisitor(file_path, parsed)
            visitor.visit(tree)
            
            return parsed
            
        except SyntaxError:
            return None
        except Exception:
            return None
    
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
    
    def get_all_function_calls(self) -> List[Dict[str, any]]:
        """Get all function calls from all parsed files."""
        calls = []
        for parsed in self.parsed_files.values():
            calls.extend(parsed.function_calls)
        return calls


class CodeVisitor(ast.NodeVisitor):
    """AST visitor to extract code structure."""
    
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
            # Extract the function name being called
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
