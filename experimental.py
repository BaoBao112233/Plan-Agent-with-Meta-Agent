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

class TimeChecker(BaseModel):
    timezone:str = Field(..., description="The timezone to get the current time from.", example=['UTC', 'US/Pacific'])

@tool("Time Checker Tool", args_schema=TimeChecker)
def time_checker_tool(timezone:str) -> str:
    '''
    Returns the current time in the specified timezone.
    '''
    from datetime import datetime
    import pytz
    try:
        current_time = datetime.now(pytz.timezone(timezone))
        return current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as err:
        return f"Error: {err}"

class Location(BaseModel):
    ip_address:str=Field(...,description="The IP address to be used for identifying the time zone.",example=['192.168.1.1'])

@tool("Time Zone Identifier Tool",args_schema=Location)
def time_zone_identifier_tool(ip_address:str):
    '''
    Identifies the time zone of a given IP address using the ip-api.
    '''
    import requests
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        return data['timezone']
    except Exception as err:
        return f"Error: {err}"

class TimeChecker(BaseModel):
    timezone:str = Field(..., description="The timezone to get the current time from.", example=['UTC', 'US/Pacific'])

@tool("Time Checker Tool", args_schema=TimeChecker)
def time_checker_tool(timezone:str) -> str:
    '''
    Returns the current time in the specified timezone.
    '''
    from datetime import datetime
    import pytz
    try:
        current_time = datetime.now(pytz.timezone(timezone))
        return current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as err:
        return f"Error: {err}"

