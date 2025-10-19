"""
MCP Tools Wrapper để tích hợp MCP tools vào MetaAgent
"""

from src.mcp_client import MCPClient
from src.tool import tool
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import json

class MCPToolWrapper:
    """Wrapper để biến MCP tools thành tools có thể sử dụng trong MetaAgent"""
    
    def __init__(self, mcp_url: str = None):
        self.mcp_client = MCPClient(mcp_url)
        self.wrapped_tools = {}
        self._create_wrapped_tools()
    
    def _create_wrapped_tools(self):
        """Tạo wrapped tools từ MCP server"""
        tools = self.mcp_client.get_available_tools()
        
        for tool_name, tool_info in tools.items():
            # Tạo dynamic tool function
            wrapped_tool = self._create_tool_function(tool_name, tool_info)
            self.wrapped_tools[tool_name] = wrapped_tool
    
    def _create_tool_function(self, tool_name: str, tool_info: Dict):
        """Tạo tool function cho một MCP tool"""
        
        # Tạo Pydantic model cho parameters
        parameters = tool_info.get('parameters', {})
        required_params = tool_info.get('inputSchema', {}).get('required', [])
        
        # Build pydantic fields
        model_fields = {}
        for param_name, param_schema in parameters.items():
            param_type = param_schema.get('type', 'string')
            param_desc = param_schema.get('description', f'Parameter {param_name}')
            is_required = param_name in required_params
            
            # Map JSON schema types to Python types
            if param_type == 'string':
                field_type = str
            elif param_type == 'integer':
                field_type = int
            elif param_type == 'number':
                field_type = float
            elif param_type == 'boolean':
                field_type = bool
            elif param_type == 'array':
                field_type = List[str]  # Simplified
            elif param_type == 'object':
                field_type = Dict[str, Any]
            else:
                field_type = str  # Default to string
            
            if is_required:
                model_fields[param_name] = (field_type, Field(..., description=param_desc))
            else:
                model_fields[param_name] = (field_type, Field(None, description=param_desc))
        
        # Create dynamic Pydantic model
        if model_fields:
            DynamicModel = type(f"{tool_name}Args", (BaseModel,), model_fields)
        else:
            # Empty model for tools without parameters
            DynamicModel = type(f"{tool_name}Args", (BaseModel,), {})
        
        # Create the actual tool function
        @tool(tool_info.get('description', f'MCP tool: {tool_name}'), args_schema=DynamicModel)
        def mcp_tool_function(**kwargs) -> str:
            """Dynamically generated MCP tool wrapper"""
            # Filter out None values
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            
            # Call the MCP tool
            result = self.mcp_client.call_tool(tool_name, filtered_kwargs)
            
            if result is None:
                return f"Error: Failed to execute {tool_name}"
            
            # Format result for LLM consumption
            if isinstance(result, dict):
                return json.dumps(result, indent=2, ensure_ascii=False)
            else:
                return str(result)
        
        # Set function name for identification
        mcp_tool_function.__name__ = tool_name
        mcp_tool_function.mcp_tool_name = tool_name
        
        return mcp_tool_function
    
    def get_tools(self) -> List:
        """Lấy danh sách tất cả wrapped tools"""
        return list(self.wrapped_tools.values())
    
    def get_tool(self, tool_name: str):
        """Lấy một tool cụ thể"""
        return self.wrapped_tools.get(tool_name)
    
    def refresh_tools(self):
        """Refresh tools từ MCP server"""
        self.wrapped_tools.clear()
        self._create_wrapped_tools()
    
    def list_available_tools(self) -> List[str]:
        """Liệt kê tên của tất cả tools có sẵn"""
        return list(self.wrapped_tools.keys())

# Global instance để sử dụng trong MetaAgent
_mcp_wrapper = None

def get_mcp_tools(mcp_url: str = None) -> List:
    """
    Lấy MCP tools để sử dụng trong MetaAgent
    
    Args:
        mcp_url: URL của MCP server (optional)
    
    Returns:
        List of wrapped MCP tools
    """
    global _mcp_wrapper
    
    if _mcp_wrapper is None:
        _mcp_wrapper = MCPToolWrapper(mcp_url)
    
    return _mcp_wrapper.get_tools()

def refresh_mcp_tools():
    """Refresh MCP tools cache"""
    global _mcp_wrapper
    if _mcp_wrapper:
        _mcp_wrapper.refresh_tools()

def list_mcp_tool_names() -> List[str]:
    """Liệt kê tên của tất cả MCP tools"""
    global _mcp_wrapper
    if _mcp_wrapper:
        return _mcp_wrapper.list_available_tools()
    return []