from src.tool import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
load_dotenv()

class SystemTime(BaseModel):
    format:str=Field(...,description="The format of the time",example=['%Y-%m-%d %H:%M:%S'])

@tool("System Time Tool",args_schema=SystemTime)
def system_time_tool(format:str):
    '''
    Retrieves the current system time in a human-readable format.
    '''
    from datetime import datetime
    try:
        current_time = datetime.now().strftime(format)
    except Exception as err:
        return f"Error: {err}"
    return current_time

class GetCurrentTime(BaseModel):
    timezone:str = Field(..., description="The timezone to get the current time for", example=['UTC'])

@tool("Current Time Tool", args_schema=GetCurrentTime)
def current_time_tool(timezone:str) -> str:
    '''
    Returns the current time in the specified timezone.
    '''
    from datetime import datetime
    import pytz
    try:
        timezone = pytz.timezone(timezone)
        current_time = datetime.now(timezone)
        return current_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as err:
        return f"Error: {err}"

class Terminal(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Terminal Tool",args_schema=Terminal)
def terminal_tool(command:str)->str:
    '''
    Executes a shell command in the terminal and returns its output.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=True will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')

        output = f"Command executed successfully.\nStandard Output:\n{result.stdout}\nStandard Error:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        # Command returned a non-zero exit code
        error_output = f"Error executing command: '{e.cmd}'\nExit Code: {e.returncode}\nStandard Output:\n{e.stdout}\nStandard Error:\n{e.stderr}"
        return f"Error: {error_output}"
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class Terminal(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Terminal Tool",args_schema=Terminal)
def terminal_tool(command:str)->str:
    '''
    Executes a shell command in the terminal and returns its output.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=True will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')

        output = f"Command executed successfully.\nStandard Output:\n{result.stdout}\nStandard Error:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        # Command returned a non-zero exit code
        error_output = f"Error executing command: '{e.cmd}'\nExit Code: {e.returncode}\nStandard Output:\n{e.stdout}\nStandard Error:\n{e.stderr}"
        return f"Error: {error_output}"
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class Terminal(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Terminal Tool",args_schema=Terminal)
def terminal_tool(command:str)->str:
    '''
    Executes a shell command in the terminal and returns its output.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=True will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')

        output = f"Command executed successfully.\nStandard Output:\n{result.stdout}\nStandard Error:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        # Command returned a non-zero exit code
        error_output = f"Error executing command: '{e.cmd}'\nExit Code: {e.returncode}\nStandard Output:\n{e.stdout}\nStandard Error:\n{e.stderr}"
        return f"Error: {error_output}"
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class GoogleSearch(BaseModel):
    query:str=Field(...,description="The search query to be performed.",example=["latest AI news"])

@tool("Google Search Tool",args_schema=GoogleSearch)
def google_search_tool(query:str)->str:
    '''
    Performs a Google search for the given query and returns the search results.
    This tool uses DuckDuckGo's search capabilities to simulate Google search results.
    '''
    from duckduckgo_search import DDGS
    import os

    try:
        ddgs = DDGS()
        # Perform a text search using DuckDuckGo, which provides similar results to Google.
        # Limiting to 5 results for brevity and relevance.
        results = ddgs.text(query, max_results=5)

        if not results:
            return "No search results found for the given query."

        formatted_results = []
        for i, result in enumerate(results):
            title = result.get('title', 'No Title')
            href = result.get('href', 'No URL')
            body = result.get('body', 'No Description')
            formatted_results.append(f"Result {i+1}:\nTitle: {title}\nURL: {href}\nDescription: {body}\n")

        return "\n".join(formatted_results)

    except Exception as err:
        return f"Error performing Google search: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecution(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -la', 'echo Hello World'])

@tool("Shell Command Execution Tool",args_schema=ShellCommandExecution)
def shell_command_execution_tool(command:str)->str:
    '''
    Executes an arbitrary shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # shell=True is used to allow arbitrary shell commands, but should be used with caution
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to inspect stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"Standard Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nStandard Error:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command: {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecution(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -la', 'echo Hello World'])

@tool("Shell Command Execution Tool",args_schema=ShellCommandExecution)
def shell_command_execution_tool(command:str)->str:
    '''
    Executes an arbitrary shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # shell=True is used to allow arbitrary shell commands, but should be used with caution
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to inspect stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"Standard Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nStandard Error:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents subprocess.CalledProcessError for non-zero exit codes
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{process.stdout}"
        if process.stderr:
            output += f"\nSTDERR:\n{process.stderr}"
        if process.returncode != 0:
            output += f"\nCommand exited with non-zero status code: {process.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to capture stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l','echo Hello World'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SHELL_COMMAND_API_KEY') # Placeholder for potential API key, not used in this tool.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        return output
    except subprocess.CalledProcessError as e:
        # Handle commands that return a non-zero exit code
        error_output = f"Error: Command '{e.cmd}' failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        return error_output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('<NAME OF API>')
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l /tmp'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SOME_API_KEY') # Placeholder for potential API key usage, not directly used for shell execution.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecution(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -la', 'echo Hello World'])

@tool("Shell Command Execution Tool",args_schema=ShellCommandExecution)
def shell_command_execution_tool(command:str)->str:
    '''
    Executes an arbitrary shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # shell=True is used to allow arbitrary shell commands, but should be used with caution
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to inspect stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"Standard Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nStandard Error:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents subprocess.CalledProcessError for non-zero exit codes
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{process.stdout}"
        if process.stderr:
            output += f"\nSTDERR:\n{process.stderr}"
        if process.returncode != 0:
            output += f"\nCommand exited with non-zero status code: {process.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to capture stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l','echo Hello World'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SHELL_COMMAND_API_KEY') # Placeholder for potential API key, not used in this tool.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        return output
    except subprocess.CalledProcessError as e:
        # Handle commands that return a non-zero exit code
        error_output = f"Error: Command '{e.cmd}' failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        return error_output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('<NAME OF API>')
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l /tmp'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SOME_API_KEY') # Placeholder for potential API key usage, not directly used for shell execution.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class FileCreation(BaseModel):
    file_name:str=Field(...,description="The name of the file to be created.",example=["my_new_file.txt"])

@tool("File Creation Tool",args_schema=FileCreation)
def file_creation_tool(file_name:str)->str:
    '''
    Creates an empty file with the specified name using the 'touch' command.
    '''
    import subprocess
    import os

    try:
        # Ensure the file_name is safe to use in a shell command
        if not file_name or '..' in file_name or '/' in file_name or '\\' in file_name:
            return "Error: Invalid file name provided. File name cannot be empty or contain path separators."

        # Execute the 'touch' command to create an empty file
        result = subprocess.run(['touch', file_name], capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return f"Successfully created empty file: {file_name}"
        else:
            return f"Error creating file {file_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing touch command: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'touch' command not found. Please ensure it is installed and in your system's PATH."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecution(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -la', 'echo Hello World'])

@tool("Shell Command Execution Tool",args_schema=ShellCommandExecution)
def shell_command_execution_tool(command:str)->str:
    '''
    Executes an arbitrary shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # shell=True is used to allow arbitrary shell commands, but should be used with caution
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to inspect stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"Standard Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nStandard Error:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents subprocess.CalledProcessError for non-zero exit codes
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{process.stdout}"
        if process.stderr:
            output += f"\nSTDERR:\n{process.stderr}"
        if process.returncode != 0:
            output += f"\nCommand exited with non-zero status code: {process.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l", "echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    try:
        # Execute the command, capture stdout and stderr
        # text=True decodes stdout/stderr as text using default encoding
        # check=False prevents CalledProcessError for non-zero exit codes, allowing us to capture stderr
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output.strip()
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l','echo Hello World'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SHELL_COMMAND_API_KEY') # Placeholder for potential API key, not used in this tool.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        return output
    except subprocess.CalledProcessError as e:
        # Handle commands that return a non-zero exit code
        error_output = f"Error: Command '{e.cmd}' failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        return error_output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"An unexpected error occurred: {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=["ls -l","echo Hello World"])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('<NAME OF API>')
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except Exception as err:
        return f"Error executing command '{command}': {err}"

class ShellCommandExecutor(BaseModel):
    command:str=Field(...,description="The shell command to be executed.",example=['ls -l /tmp'])

@tool("Shell Command Executor Tool",args_schema=ShellCommandExecutor)
def shell_command_executor_tool(command:str)->str:
    '''
    Executes a given shell command and returns its standard output and standard error.
    '''
    import subprocess
    import os

    # API key for the any API usage as an environment variable, use if needed.
    api_key=os.environ.get('SOME_API_KEY') # Placeholder for potential API key usage, not directly used for shell execution.
    try:
        # Execute the command, capture stdout and stderr, and decode them as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        output = f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status: {result.returncode}"

        return output
    except FileNotFoundError:
        return f"Error: Command not found. Please check the command and try again."
    except Exception as err:
        return f"Error executing command '{command}': {err}"

