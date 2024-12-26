import os
import ast
import importlib.util

from typing import Callable, Optional


def find_tool_functions(directory: str, file_name: Optional[str] = None):
    """
    Scans the given directory or a specific file for Python files, identifies functions with the @tool decorator,
    and returns references to these functions.

    Args:
        directory (str): The directory to scan.
        file_name (Optional[str]): The specific Python file to scan within the directory.

    Returns:
        List[function]: A list of references to functions with the @tool decorator.
    """
    tool_functions = []

    if file_name and file_name.endswith('.py'):
        files_to_scan = [file_name]
        directory = os.path.join(directory, os.path.dirname(file_name))
    else:
        files_to_scan = [file for root, _, files in os.walk(
            directory) for file in files if file.endswith('.py')]

    for file in files_to_scan:
        file_path = os.path.join(directory, file)

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


def get_all_tools(tools_path: str = None) -> list[Callable]:
    """
    Retrieves all tool functions from the specified directory.

    Args:
        tools_path (str, optional): The specific tool file to retrieve functions from. If None, retrieves all tools from the 'agentic' directory.

    Returns:
        list[Callable]: A list of callable tool function references.
    """
    if tools_path is not None:
        tools_root_path = os.path.join(os.getcwd(), "src", "agent", "tools", "all")
        functions = find_tool_functions(tools_root_path, f"{tools_path}.py")
        return functions
    else:
        tools_root_path = os.path.join(os.getcwd(), "src", "agent", "tools", "agentic")
        functions = find_tool_functions(tools_root_path)
    return functions