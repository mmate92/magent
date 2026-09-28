from functions.get_files_info import get_file_content, get_files_info, run_python_file, schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file, write_file
import json
from collections.abc import Callable

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "write_file": write_file,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file
}


# Available schemas for the LLM to get info on functions
available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]

def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    if not function_name in function_map:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }
    function_args["working_directory"] = "./calculator"
    result: str = function_map[function_name](**function_args)
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    }