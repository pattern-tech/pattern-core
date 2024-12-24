import os
import ast
import inspect
import importlib.util

from typing import Callable, Optional


def find_tool_functions(directory: str):
    """
    Scans the given directory for Python files, identifies functions with the @tool decorator,
    and returns references to these functions.

    Args:
        directory (str): The directory to scan.

    Returns:
        List[function]: A list of references to functions with the @tool decorator.
    """
    tool_functions = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # Parse the Python file using the AST module
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source, filename=file_path)

                # Check for functions with @tool decorator
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'tool':
                                # Dynamically load the module and get a reference to the function
                                module_name = os.path.splitext(
                                    os.path.basename(file_path))[0]
                                spec = importlib.util.spec_from_file_location(
                                    module_name, file_path)
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)

                                # Add function reference to the list
                                function_ref = getattr(module, node.name, None)
                                if function_ref is not None:
                                    tool_functions.append(function_ref)

    return tool_functions


def get_all_tools() -> list[Callable]:
    """Get all tool functions."""
    tools_root_path = os.path.join(os.getcwd(), "src", "agent", "tools")
    functions = find_tool_functions(tools_root_path)
    return functions
