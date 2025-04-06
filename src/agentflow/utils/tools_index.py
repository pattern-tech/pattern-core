import os
import ast
import inspect
import importlib.util
import json
from typing import Callable, Optional, List, Dict, Any, Type, get_type_hints
from pydantic import BaseModel, create_model


def find_tool_functions(directory: str, file_name: Optional[str] = None) -> List[Callable]:
    """
    Scans the given directory or a specific file for Python files, identifies functions with the @tool decorator,
    and returns references to these functions.

    Args:
        directory (str): The directory to scan.
        file_name (Optional[str]): The specific Python file to scan within the directory.

    Returns:
        List[Callable]: A list of references to functions with the @tool decorator.
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


def get_all_tools(tools_path: str) -> List[Dict[str, Any]]:
    """
    Retrieves all tool functions from the specified directory and extracts their names, descriptions,
    input schemas, and output schemas.

    Args:
        tools_path (str): The specific tool file to retrieve functions from. If None, retrieves all tools from the 'providers' directory.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing function names, descriptions, input schemas, and output schemas.
    """
    tools_root_path = os.path.join(
        os.getcwd(), "src", "agentflow", "providers")
    functions = find_tool_functions(tools_root_path, f"{tools_path}.py")

    tools_info = []
    for func in functions:
        # Extract function name
        name = func.__name__

        # Extract function description from docstring
        description = ""
        if func.__doc__:
            description = inspect.cleandoc(func.__doc__).strip()

        # extract the input and output schema from function
        input_schema = None
        output_schema = None

        # Get type hints for the function
        type_hints = get_type_hints(func)

        # Extract input schema from function parameters
        for param_name, param_type in type_hints.items():
            if param_name != 'return' and hasattr(param_type, 'to_json_schema'):
                # Found a Pydantic model as input parameter
                input_schema = param_type.to_json_schema()
                break

        # Extract output schema from return type
        if 'return' in type_hints and hasattr(type_hints['return'], 'to_json_schema'):
            # Found a Pydantic model as return type
            output_schema = type_hints['return'].to_json_schema()

        tool_info = {
            "name": name,
            "description": description
        }

        if input_schema:
            tool_info["input_schema"] = input_schema

        if output_schema:
            tool_info["output_schema"] = output_schema

        tools_info.append(tool_info)

    return tools_info
