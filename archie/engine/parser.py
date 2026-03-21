"""AST parser using tree-sitter for Python and JavaScript/TypeScript."""
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Dict, List, Optional


class CodeParser:
    """Parse code files into structured AST data."""
    
    def __init__(self):
        self.py_lang = Language(tspython.language())
        self.js_lang = Language(tsjavascript.language())
        self.parser = Parser()
    
    def parse_file(self, file_path: str) -> Optional[Dict]:
        """Parse a file and extract structure."""
        path = Path(file_path)
        if not path.exists():
            return None
        
        suffix = path.suffix
        if suffix == ".py":
            return self._parse_python(file_path)
        elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
            return self._parse_javascript(file_path)
        return None
    
    def _parse_python(self, file_path: str) -> Dict:
        """Parse Python file."""
        self.parser.language = self.py_lang
        with open(file_path, "rb") as f:
            code = f.read()
        
        tree = self.parser.parse(code)
        root = tree.root_node
        
        result = {
            "file_path": file_path,
            "language": "python",
            "functions": [],
            "classes": [],
            "imports": [],
            "calls": []
        }
        
        # Extract functions
        for node in self._query_nodes(root, "function_definition"):
            func_name = self._get_node_text(node.child_by_field_name("name"), code)
            params = self._extract_params(node, code)
            result["functions"].append({
                "name": func_name,
                "line_start": node.start_point[0] + 1,
                "line_end": node.end_point[0] + 1,
                "params": params
            })
        
        # Extract classes
        for node in self._query_nodes(root, "class_definition"):
            class_name = self._get_node_text(node.child_by_field_name("name"), code)
            methods = []
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "function_definition":
                        method_name = self._get_node_text(child.child_by_field_name("name"), code)
                        methods.append(method_name)
            result["classes"].append({
                "name": class_name,
                "methods": methods
            })
        
        # Extract imports
        for node in self._query_nodes(root, "import_statement"):
            result["imports"].extend(self._extract_import(node, code))
        for node in self._query_nodes(root, "import_from_statement"):
            result["imports"].extend(self._extract_import_from(node, code))
        
        # Extract function calls
        result["calls"] = self._extract_calls(root, code, result["functions"])
        
        return result

    def _parse_javascript(self, file_path: str) -> Dict:
        """Parse JavaScript/TypeScript file."""
        self.parser.language = self.js_lang
        with open(file_path, "rb") as f:
            code = f.read()
        
        tree = self.parser.parse(code)
        root = tree.root_node
        
        result = {
            "file_path": file_path,
            "language": "javascript",
            "functions": [],
            "classes": [],
            "imports": [],
            "calls": []
        }
        
        # Extract function declarations
        for node in self._query_nodes(root, "function_declaration"):
            func_name = self._get_node_text(node.child_by_field_name("name"), code)
            params = self._extract_js_params(node, code)
            result["functions"].append({
                "name": func_name,
                "line_start": node.start_point[0] + 1,
                "line_end": node.end_point[0] + 1,
                "params": params
            })
        
        # Extract arrow functions and method definitions
        for node in self._query_nodes(root, "method_definition"):
            method_name = self._get_node_text(node.child_by_field_name("name"), code)
            params = self._extract_js_params(node, code)
            result["functions"].append({
                "name": method_name,
                "line_start": node.start_point[0] + 1,
                "line_end": node.end_point[0] + 1,
                "params": params
            })
        
        # Extract classes
        for node in self._query_nodes(root, "class_declaration"):
            class_name = self._get_node_text(node.child_by_field_name("name"), code)
            methods = []
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "method_definition":
                        method_name = self._get_node_text(child.child_by_field_name("name"), code)
                        methods.append(method_name)
            result["classes"].append({
                "name": class_name,
                "methods": methods
            })
        
        # Extract imports
        for node in self._query_nodes(root, "import_statement"):
            result["imports"].extend(self._extract_js_import(node, code))
        
        # Extract calls
        result["calls"] = self._extract_calls(root, code, result["functions"])
        
        return result
    
    def _query_nodes(self, root, node_type: str) -> List:
        """Recursively find all nodes of a given type."""
        nodes = []
        if root.type == node_type:
            nodes.append(root)
        for child in root.children:
            nodes.extend(self._query_nodes(child, node_type))
        return nodes
    
    def _get_node_text(self, node, code: bytes) -> str:
        """Extract text from a node."""
        if node is None:
            return ""
        return code[node.start_byte:node.end_byte].decode("utf-8")

    def _extract_params(self, func_node, code: bytes) -> List[str]:
        """Extract parameter names from Python function."""
        params = []
        params_node = func_node.child_by_field_name("parameters")
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    params.append(self._get_node_text(child, code))
        return params
    
    def _extract_js_params(self, func_node, code: bytes) -> List[str]:
        """Extract parameter names from JS function."""
        params = []
        params_node = func_node.child_by_field_name("parameters")
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    params.append(self._get_node_text(child, code))
        return params
    
    def _extract_import(self, node, code: bytes) -> List[Dict]:
        """Extract Python import statement."""
        imports = []
        for child in node.children:
            if child.type == "dotted_name":
                module = self._get_node_text(child, code)
                imports.append({"module": module, "names": []})
        return imports
    
    def _extract_import_from(self, node, code: bytes) -> List[Dict]:
        """Extract Python from...import statement."""
        module = ""
        names = []
        for child in node.children:
            if child.type == "dotted_name":
                module = self._get_node_text(child, code)
            elif child.type == "import_prefix":
                module = self._get_node_text(child, code)
            elif child.type == "aliased_import" or child.type == "dotted_name":
                name = self._get_node_text(child, code).split(" as ")[0]
                names.append(name)
        return [{"module": module, "names": names}] if module else []
    
    def _extract_js_import(self, node, code: bytes) -> List[Dict]:
        """Extract JavaScript import statement."""
        imports = []
        source = ""
        names = []
        for child in node.children:
            if child.type == "string":
                source = self._get_node_text(child, code).strip("'\"")
            elif child.type == "import_clause":
                for subchild in child.children:
                    if subchild.type == "identifier":
                        names.append(self._get_node_text(subchild, code))
        if source:
            imports.append({"module": source, "names": names})
        return imports
    
    def _extract_calls(self, root, code: bytes, functions: List[Dict]) -> List[Dict]:
        """Extract function calls."""
        calls = []
        call_nodes = self._query_nodes(root, "call")
        func_names = {f["name"] for f in functions}
        
        for call_node in call_nodes:
            func = call_node.child_by_field_name("function")
            if func:
                callee = self._get_node_text(func, code)
                # Find which function this call is inside
                caller = self._find_containing_function(call_node, code, functions)
                if caller and callee:
                    calls.append({
                        "caller": caller,
                        "callee": callee,
                        "line": call_node.start_point[0] + 1
                    })
        return calls

    def _find_containing_function(self, node, code: bytes, functions: List[Dict]) -> Optional[str]:
        """Find which function contains this node."""
        line = node.start_point[0] + 1
        for func in functions:
            if func["line_start"] <= line <= func["line_end"]:
                return func["name"]
        return None
