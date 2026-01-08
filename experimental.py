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

