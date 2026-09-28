import os
import subprocess
from typing import TypedDict

class FileInfo(TypedDict):
    file_size: int
    is_dir: bool

def get_files_info(working_directory: str, directory: str = ".") -> str:

    wd_path = os.path.abspath(working_directory)
    dir_path = os.path.normpath(os.path.join(wd_path, directory))
    is_valid_target_dir_path = os.path.commonpath([wd_path, dir_path]) == wd_path

    if not is_valid_target_dir_path:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(dir_path):
        return f'Error: "{directory}" is not a directory'

    dir_info_dict: dict[str, FileInfo] = {}
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            dir_info_dict[item] = {"file_size": os.path.getsize(item_path), "is_dir": os.path.isdir(item_path)}
    except Exception as e:
        return f'Error: Getting info on the files in {directory} failed'
        # return f"Error: {e}"

    file_info_summary = ""
    for k, v in dir_info_dict.items():
        file_info_summary += f"- {k}: file_size={v["file_size"]} bytes, is_dir={v['is_dir']}\n"
    return file_info_summary

def get_file_content(working_directory: str, file_path: str) -> str:

    try:
        wd_path = os.path.abspath(working_directory)
        file_full_abs_path = os.path.normpath(os.path.join(wd_path, file_path))
        is_valid_file_path = os.path.commonpath([wd_path, file_full_abs_path]) == wd_path
    except Exception as e:
        return f"Error: Could not validate file path accessibility for {file_path}: {e}"


    if not is_valid_file_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_full_abs_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(file_full_abs_path, "r") as f:
            file_content = f.read(10000)
            if f.read(1):
                file_content += f'[...File "{file_path}" truncated at {10000} characters]'
    except Exception as e:
        return f"Error: Could not open or read file: {file_path}: {e}"

    return file_content

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        wd_path = os.path.abspath(working_directory)
        file_full_abs_path = os.path.normpath(os.path.join(wd_path, file_path))
        is_valid_file_path = os.path.commonpath([wd_path, file_full_abs_path]) == wd_path
    
        if not is_valid_file_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(file_full_abs_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        os.makedirs(os.path.dirname(file_full_abs_path), exist_ok=True)

        with open(file_full_abs_path, "w") as f:
            f.write(content)

    except Exception as e:
            return f"Error: Cannot write to file {file_path}: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        wd_path = os.path.abspath(working_directory)
        file_full_abs_path = os.path.normpath(os.path.join(wd_path, file_path))
        is_valid_file_path = os.path.commonpath([wd_path, file_full_abs_path]) == wd_path
    
        if not is_valid_file_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(file_full_abs_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_full_abs_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        os.makedirs(os.path.dirname(file_full_abs_path), exist_ok=True)

        command = ["python", file_full_abs_path]
        if args:
            command.extend(args)
        sp_run_result = subprocess.run(command, cwd=wd_path, text=True, capture_output=True, timeout=30)

    except Exception as e:
        return f"Error: executing Python file: {e}"

    final_result = ""
    if sp_run_result.returncode != 0:
        final_result += f"Process exited with code {sp_run_result.returncode}"
    if not sp_run_result.stderr and not sp_run_result.stdout:
        final_result += "No output produced"
    else:
        if sp_run_result.stdout:
            final_result += f"STDOUT: {sp_run_result.stdout}"
        if sp_run_result.stderr:
            final_result += f"STDERR: {sp_run_result.stderr}"
    
    return final_result


schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Reads the contents of a file and returns it as a string",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory.",
                },
            },
            "required": ["file_path"]
        },
    },
}

schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content into the specified file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write, relative to the working directory",
                },
                "content": {
                    "type": "string",
                    "description": "The content to be written into the file. Uses standard Python write()",
                },
            },
            "required": ["file_path", "content"]
        },
    },
}

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a specified Python file within the working directory and returns its output",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to run, relative to the working directory.",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"        
                    },
                    "description": "The list of arguments for the run command",
                },
            },
            "required": ["file_path"]
        },
    },
}