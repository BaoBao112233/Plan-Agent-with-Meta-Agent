"""
MCP Tools Wrapper để tích hợp MCP tools vào MetaAgent
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import Tool
from src.mcp_client import MCPClient
from src.tool import tool
import json

class MCPToolsWrapper:
    """Wrapper để chuyển đổi MCP tools thành LangChain tools cho MetaAgent"""
    
    def __init__(self, mcp_url: str = None):
        self.mcp_client = MCPClient(mcp_url)
        self.tools = []
        self._load_mcp_tools()
    
    def _load_mcp_tools(self):
        """Load và chuyển đổi tất cả MCP tools thành LangChain tools"""
        available_tools = self.mcp_client.get_available_tools()
        
        for tool_name, tool_info in available_tools.items():
            langchain_tool = self._convert_mcp_tool_to_langchain(tool_name, tool_info)
            if langchain_tool:
                self.tools.append(langchain_tool)
    
    def _convert_mcp_tool_to_langchain(self, tool_name: str, tool_info: Dict) -> Optional[Tool]:
        """Chuyển đổi một MCP tool thành LangChain tool"""
        try:
            description = tool_info.get('description', f'MCP tool: {tool_name}')
            parameters = tool_info.get('parameters', {})
            
            # Tạo function để execute MCP tool
            def execute_mcp_tool(**kwargs):
                try:
                    # Validate parameters
                    is_valid, errors = self.mcp_client.validate_parameters(tool_name, kwargs)
                    if not is_valid:
                        return f"❌ Parameter validation failed: {'; '.join(errors)}"
                    
                    # Execute tool
                    result = self.mcp_client.call_tool(tool_name, kwargs)
                    if result is None:
                        return f"❌ Failed to execute tool '{tool_name}'"
                    
                    # Format result
                    if isinstance(result, dict):
                        return json.dumps(result, indent=2, ensure_ascii=False)
                    else:
                        return str(result)
                        
                except Exception as e:
                    return f"❌ Error executing '{tool_name}': {e}"
            
            # Tạo LangChain tool
            return Tool(
                name=tool_name,
                description=description,
                func=execute_mcp_tool
            )
            
        except Exception as e:
            print(f"❌ Error converting tool '{tool_name}': {e}")
            return None
    
    def get_tools(self) -> List[Tool]:
        """Lấy danh sách LangChain tools"""
        return self.tools
    
    def get_tool_names(self) -> List[str]:
        """Lấy danh sách tên tools"""
        return [tool.name for tool in self.tools]
    
    def refresh_tools(self):
        """Refresh tools từ MCP server"""
        self.tools.clear()
        self._load_mcp_tools()

# Pydantic models cho các MCP tools chính
class DeviceListParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")

class SwitchDeviceParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    house_id: str = Field(..., description="House ID")
    device_id: str = Field(..., description="Device ID for SH1/SH2 devices")
    button_code: str = Field(..., description="Button code")
    command: str = Field(..., description="Command: ON or OFF")

class ACControlParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    serial_number: str = Field(..., description="AC device serial number")
    mode: str = Field(..., description="AC mode: heat, cool, auto, fan, dry")
    temperature: int = Field(..., description="Temperature setting")
    fan_speed: str = Field(..., description="Fan speed: auto, low, medium, high")

class CronjobParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    device_id: str = Field(None, description="Device ID (for switch devices)")
    button_id: str = Field(None, description="Button ID (for remote buttons)")
    action: str = Field(..., description="Action: add, update, delete")
    cron_expression: str = Field(None, description="Cron expression (6 fields)")
    command: str = Field(None, description="Command for the cronjob")

class OneTouchParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    house_id: str = Field(..., description="House ID")
    status: str = Field(..., description="Status: ON or OFF")

class OneTouchByTypeParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    house_id: str = Field(..., description="House ID")
    device_type: str = Field(..., description="Device type: LIGHT, CONDITIONER, etc.")
    status: str = Field(..., description="Status: ON or OFF")

class RoomOneTouchParams(BaseModel):
    token: str = Field(..., description="OXII authentication token")
    room_id: str = Field(..., description="Room ID")
    status: str = Field(..., description="Status: ON or OFF")

# Individual tool wrappers với proper schemas
@tool("Get Device List", args_schema=DeviceListParams)
def get_device_list_tool(token: str) -> str:
    """List homes, rooms, devices, and remote buttons from OXII system"""
    wrapper = MCPToolsWrapper()
    result = wrapper.mcp_client.call_tool("get_device_list", {"token": token})
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to get device list"

@tool("Switch Device Control", args_schema=SwitchDeviceParams)
def switch_device_control_tool(token: str, house_id: str, device_id: str, button_code: str, command: str) -> str:
    """Toggle SH1/SH2 relay devices ON/OFF"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "house_id": house_id,
        "device_id": device_id,
        "button_code": button_code,
        "command": command
    }
    result = wrapper.mcp_client.call_tool("switch_device_control", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to control switch device"

@tool("Control Air Conditioner", args_schema=ACControlParams)
def control_air_conditioner_tool(token: str, serial_number: str, mode: str, temperature: int, fan_speed: str) -> str:
    """Full AC control including mode, temperature, and fan speed"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "serial_number": serial_number,
        "mode": mode,
        "temperature": temperature,
        "fan_speed": fan_speed
    }
    result = wrapper.mcp_client.call_tool("control_air_conditioner", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to control air conditioner"

@tool("Create Device Cronjob", args_schema=CronjobParams)
def create_device_cronjob_tool(token: str, action: str, device_id: str = None, button_id: str = None, 
                              cron_expression: str = None, command: str = None) -> str:
    """Add/update/remove cronjobs for switches or AC devices"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "action": action
    }
    if device_id:
        params["device_id"] = device_id
    if button_id:
        params["button_id"] = button_id
    if cron_expression:
        params["cron_expression"] = cron_expression
    if command:
        params["command"] = command
        
    result = wrapper.mcp_client.call_tool("create_device_cronjob", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to manage cronjob"

@tool("One Touch Control All", args_schema=OneTouchParams)
def one_touch_control_all_tool(token: str, house_id: str, status: str) -> str:
    """Execute house-wide preset (turn everything on/off)"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "house_id": house_id,
        "status": status
    }
    result = wrapper.mcp_client.call_tool("one_touch_control_all_devices", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to execute one touch control"

@tool("One Touch Control By Type", args_schema=OneTouchByTypeParams)
def one_touch_control_by_type_tool(token: str, house_id: str, device_type: str, status: str) -> str:
    """Toggle devices by type (LIGHT, CONDITIONER, etc.)"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "house_id": house_id,
        "device_type": device_type,
        "status": status
    }
    result = wrapper.mcp_client.call_tool("one_touch_control_by_type", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to execute type-based control"

@tool("Room One Touch Control", args_schema=RoomOneTouchParams)
def room_one_touch_control_tool(token: str, room_id: str, status: str) -> str:
    """Run single-room preset (turn room devices on/off)"""
    wrapper = MCPToolsWrapper()
    params = {
        "token": token,
        "room_id": room_id,
        "status": status
    }
    result = wrapper.mcp_client.call_tool("room_one_touch_control", params)
    if result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return "❌ Failed to execute room control"

# Function để lấy tất cả MCP tools cho MetaAgent
def get_mcp_tools_for_meta_agent() -> List:
    """Lấy danh sách MCP tools để sử dụng trong MetaAgent"""
    return [
        get_device_list_tool,
        switch_device_control_tool,
        control_air_conditioner_tool,
        create_device_cronjob_tool,
        one_touch_control_all_tool,
        one_touch_control_by_type_tool,
        room_one_touch_control_tool
    ]