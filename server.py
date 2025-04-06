import os
from typing import Any
from mcp.server.fastmcp import FastMCP
import idapro


# Initialize FastMCP server
mcp = FastMCP("IDAPython")

IDAPYTHON_PATH = os.path.join(os.getenv("IDADIR"), "python")
FUNCS = []

def grep_in_file(file_path: str, pattern: str) -> list[str]:
    """Grep in a file for a pattern."""
    with open(file_path, "r") as f:
        return [line for line in f if pattern in line]

def grep_in_directory(directory: str, pattern: str) -> list[str]:
    """Find which file in directory contains the pattern."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if grep_in_file(os.path.join(root, file), pattern):
                return file
    return None


@mcp.tool("idapython_functions_list")
def idapython_functions() -> list[str]:
    """Get all IDAPython functions."""
    global FUNCS
    if FUNCS:
        return FUNCS
    
    file_list = [f.replace(".py", "") for f in os.listdir(IDAPYTHON_PATH) if f.endswith(".py")]
    for file in file_list:
        import importlib
        import sys
        if file not in sys.modules:
            try:
                # Try load module
                mod = importlib.import_module(file)
            except:
                # it wasn't a real module it was something wierd.
                continue

            for func in mod.__dict__:
                if callable(mod.__dict__[func]):
                    FUNCS.append(str(func))
    return FUNCS

@mcp.tool("get_ida_function_doc")
def get_ida_function_doc(function_name: str) -> Any:
    """Get the documentation of an IDAPython function for reference.
    Args:
        function_name: The name of the function to get the documentation for.
    Returns:
        The documentation of the function as a string.
    """
    file_name = grep_in_directory(IDAPYTHON_PATH, f"def {function_name}")
    import importlib
    import sys
    # return file_name
    if file_name not in sys.modules:    
        mod = importlib.import_module(file_name.replace(".py", ""))
        doc_of_func =  mod.__dict__[function_name].__doc__
    else:
        doc_of_func =  sys.modules[file_name.replace(".py", "")].__dict__[function_name].__doc__
    
    return doc_of_func



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
