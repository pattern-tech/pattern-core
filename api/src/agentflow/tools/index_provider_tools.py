#!/usr/bin/env python3
"""
Script to index all tools with @tool decorator from the providers folder into Qdrant database.
"""

import os
import ast
import inspect
import importlib.util
from typing import List, Dict, Any, Optional, Callable
import json

from src.agentflow.tools.indexing import FunctionIndexer, FunctionSchema
from src.share.logging import Logging

_logger = Logging().get_logger()


def find_tool_functions(directory: str) -> List[Dict[str, Any]]:
    """
    Scans the given directory for Python files, identifies functions with the @tool decorator,
    and returns information about these functions.

    Args:
        directory (str): The directory to scan.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about each tool function.
    """
    tool_functions_info = []

    # Get all Python files in the directory
    files_to_scan = [os.path.join(root, file) for root, _, files in os.walk(directory)
                     for file in files if file.endswith('.py')]

    for file_path in files_to_scan:
        try:
            # Parse the Python file using the AST module
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)

            # Get the module name from the file path
            module_name = os.path.splitext(os.path.basename(file_path))[0]

            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(
                module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for functions with @tool decorator
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_tool_decorator = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'tool':
                            has_tool_decorator = True
                            break

                    if has_tool_decorator:
                        # Get function reference
                        function_ref = getattr(module, node.name, None)
                        if function_ref is not None:
                            # Extract function information
                            function_info = extract_function_info(
                                function_ref, module_name)
                            tool_functions_info.append(function_info)
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

    return tool_functions_info


def extract_function_info(function: Callable, provider_name: str) -> Dict[str, Any]:
    """
    Extracts information about a function, including its name, description, parameters, and output schema.

    Args:
        function (Callable): The function to extract information from.
        provider_name (str): The name of the provider module.

    Returns:
        Dict[str, Any]: A dictionary containing information about the function.
    """
    # Get function name
    function_name = function.__name__

    # Get function docstring and parse it
    docstring = inspect.getdoc(function) or ""

    # Get function signature
    signature = inspect.signature(function)

    # Extract parameters
    parameters = {}
    for param_name, param in signature.parameters.items():
        if param_name == 'self':
            continue

        param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
        param_type_str = str(param_type) if param_type else "Any"

        # Clean up the type string
        param_type_str = param_type_str.replace(
            "<class '", "").replace("'>", "")
        if "typing." in param_type_str:
            param_type_str = param_type_str.replace("typing.", "")

        parameters[param_name] = {
            "type": param_type_str,
            "description": extract_param_description(docstring, param_name)
        }

        # Add default value if available
        if param.default != inspect.Parameter.empty:
            parameters[param_name]["default"] = param.default

    # Extract return type and description
    return_type = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None
    return_type_str = str(return_type) if return_type else "Any"
    return_type_str = return_type_str.replace("<class '", "").replace("'>", "")
    if "typing." in return_type_str:
        return_type_str = return_type_str.replace("typing.", "")

    output_schema = {
        "type": return_type_str,
        "description": extract_return_description(docstring)
    }

    # Extract description from docstring (first paragraph)
    description = extract_description(docstring)

    # Create tags based on provider name
    tags = [provider_name, "tool"]

    return {
        "function_name": function_name,
        "description": description,
        "parameters": parameters,
        "output_schema": output_schema,
        "tags": tags,
        "provider": provider_name
    }


def extract_description(docstring: str) -> str:
    """
    Extracts the main description from a docstring.

    Args:
        docstring (str): The function docstring.

    Returns:
        str: The main description.
    """
    if not docstring:
        return ""

    # Get the first paragraph (everything before the first blank line or Args/Returns section)
    lines = docstring.split("\n")
    description_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("Args:") or line.startswith("Returns:"):
            break
        description_lines.append(line)

    return " ".join(description_lines)


def extract_param_description(docstring: str, param_name: str) -> str:
    """
    Extracts the description of a parameter from a docstring.

    Args:
        docstring (str): The function docstring.
        param_name (str): The name of the parameter.

    Returns:
        str: The parameter description.
    """
    if not docstring:
        return ""

    # Find the Args section
    args_section = docstring.split("Args:", 1)
    if len(args_section) < 2:
        return ""

    args_text = args_section[1].split("Returns:", 1)[0]

    # Find the parameter in the Args section
    param_pattern = f"{param_name} "
    param_sections = args_text.split(param_pattern)

    if len(param_sections) < 2:
        return ""

    # Extract the parameter description (until the next parameter or end of Args section)
    param_desc = param_sections[1].strip()
    lines = param_desc.split("\n")

    description_lines = []
    for line in lines:
        line = line.strip()
        if not line or ":" in line and line.split(":", 1)[0].strip() in param_sections[0]:
            break
        description_lines.append(line)

    return " ".join(description_lines)


def extract_return_description(docstring: str) -> str:
    """
    Extracts the description of the return value from a docstring.

    Args:
        docstring (str): The function docstring.

    Returns:
        str: The return value description.
    """
    if not docstring:
        return ""

    # Find the Returns section
    returns_section = docstring.split("Returns:", 1)
    if len(returns_section) < 2:
        return ""

    returns_text = returns_section[1].split("Raises:", 1)[0].strip()

    # Extract the return description
    lines = returns_text.split("\n")

    description_lines = []
    for line in lines:
        line = line.strip()
        description_lines.append(line)

    return " ".join(description_lines)


def index_provider_tools():
    """
    Main function to index all tools with @tool decorator from the providers folder into Qdrant database.
    """
    # Get the providers directory path
    providers_dir = os.path.join("src", "agentflow", "providers")

    # Find all tool functions
    print(f"Scanning directory: {providers_dir}")
    tool_functions_info = find_tool_functions(providers_dir)
    print(f"Found {len(tool_functions_info)} tool functions")

    # Initialize the function indexer
    indexer = FunctionIndexer(collection_name="provider_tools")

    # Index each function
    for func_info in tool_functions_info:
        try:
            # Create a FunctionSchema object
            schema = FunctionSchema(
                function_name=func_info["function_name"],
                description=func_info["description"],
                parameters=func_info["parameters"],
                output_schema=func_info["output_schema"],
                tags=func_info["tags"]
            )

            # Index the function
            result = indexer.index_function(schema)
            print(result)
        except Exception as e:
            print(
                f"Error indexing function {func_info['function_name']}: {str(e)}")

    print("Tool indexing completed")
