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

