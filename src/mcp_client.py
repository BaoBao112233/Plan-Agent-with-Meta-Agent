import requests
import json
import re
from typing import List, Dict, Optional, Any
from os import environ
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    """Client để kết nối và sử dụng tools từ MCP server"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or environ.get("MCP_SERVER_URL", "http://localhost:9031")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.available_tools = {}
        self.docs_cache = None
        self.session_id = None
    
    def get_session_id(self) -> Optional[str]:
        """Lấy session_id từ SSE endpoint"""
        if self.session_id:
            return self.session_id
            
        try:
            # Thử lấy session_id từ SSE với timeout ngắn
            response = self.session.get(f"{self.base_url}/sse", timeout=2, stream=True)
            
            # Đọc dữ liệu nhanh từ stream
            content = b""
            for chunk in response.iter_content(chunk_size=1024):
                content += chunk
                if b"session_id=" in content:
                    break
                if len(content) > 2048:  # Giới hạn đọc
                    break
            
            content_str = content.decode('utf-8', errors='ignore')
            match = re.search(r'session_id=([a-f0-9]+)', content_str)
            if match:
                self.session_id = match.group(1)
                print(f"✅ Got session_id: {self.session_id}")
                return self.session_id
            
            print("❌ Could not extract session_id from SSE")
            
            # Fallback: Tạo session_id ngẫu nhiên và thử
            import uuid
            fallback_session = uuid.uuid4().hex
            print(f"🔄 Trying fallback session_id: {fallback_session}")
            self.session_id = fallback_session
            return self.session_id
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting session_id: {e}")
            # Fallback: Tạo session_id ngẫu nhiên
            import uuid
            fallback_session = uuid.uuid4().hex
            print(f"🔄 Using fallback session_id: {fallback_session}")
            self.session_id = fallback_session
            return self.session_id
    
    def get_server_docs(self) -> Optional[Dict]:
        """Lấy documentation từ MCP server"""
        try:
            response = self.session.get(f"{self.base_url}/docs.json")
            response.raise_for_status()
            self.docs_cache = response.json()
            return self.docs_cache
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting MCP server docs: {e}")
            return None
    
    def get_available_tools(self) -> Dict[str, Dict]:
        """Lấy danh sách tools có sẵn từ MCP server"""
        try:
            # Sử dụng endpoint /docs.json để lấy tools catalog
            response = self.session.get(f"{self.base_url}/docs.json", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tools_data = data.get('tools', [])
            
            self.available_tools = {}
            for tool in tools_data:
                tool_name = tool['name']
                self.available_tools[tool_name] = {
                    'name': tool_name,
                    'description': tool.get('description', ''),
                    'inputSchema': tool.get('parameters', {}),
                    'parameters': tool.get('parameters', {}).get('properties', {}),
                    'required': tool.get('parameters', {}).get('required', [])
                }
            
            return self.available_tools
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting available tools: {e}")
            return {}
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """Gọi một tool trên MCP server"""
        if tool_name not in self.available_tools:
            print(f"❌ Tool '{tool_name}' not found in available tools")
            return None
        
        try:
            # First try to call real MCP server
            result = self._call_real_mcp_tool(tool_name, parameters)
            if result:
                return result
            
            # Fallback to mock if MCP server fails
            print(f"⚠️  MCP server call failed, falling back to mock for demo")
            return self._get_mock_response(tool_name, parameters)
            
        except Exception as e:
            print(f"❌ Error calling tool '{tool_name}': {e}")
            return None
    
    def _call_real_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict]:
        """Call real MCP server tool"""
        try:
            print(f"🔌 Calling real MCP tool '{tool_name}' with parameters: {parameters}")
            
            # Get session ID
            session_id = self.get_session_id()
            if not session_id:
                print("❌ No session ID available")
                return None
            
            # Prepare request payload
            payload = {
                "tool": tool_name,
                "arguments": parameters,
                "session_id": session_id
            }
            
            # Call MCP server messages endpoint
            response = self.session.post(
                f"{self.base_url}/messages", 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Real MCP tool '{tool_name}' executed successfully")
                return {
                    "result": result,
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "mock": False,
                    "real_mcp": True
                }
            else:
                print(f"❌ MCP server error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Real MCP call failed: {e}")
            return None
    
    def _get_mock_response(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """Get mock response as fallback"""
        print(f"🧪 Mock executing tool '{tool_name}' with parameters: {parameters}")
        
        # Mock responses cho từng tool
        mock_responses = {
            "get_device_list": {
                "rooms": [
                    {"id": "room1", "name": "Living Room", "devices": ["light1", "tv1"]},
                    {"id": "room2", "name": "Bedroom", "devices": ["light2", "ac1"]}
                ],
                "devices": [
                    {"id": "light1", "name": "Living Room Light", "type": "LIGHT", "status": "off"},
                    {"id": "tv1", "name": "Living Room TV", "type": "TV", "status": "off"},
                    {"id": "light2", "name": "Bedroom Light", "type": "LIGHT", "status": "on"},
                    {"id": "ac1", "name": "Bedroom AC", "type": "CONDITIONER", "status": "off"}
                ]
            },
            "switch_device_control": {
                "success": True,
                "message": f"Device {parameters.get('buttonId', 'unknown')} turned {parameters.get('action', 'unknown')}"
            },
            "control_air_conditioner": {
                "success": True,
                "message": f"AC set to {parameters.get('temp', '24')}°C, mode: {parameters.get('mode', 'auto')}"
            },
            "one_touch_control_all_devices": {
                "success": True,
                "message": f"All devices turned {parameters.get('command', 'unknown')}"
            },
            "one_touch_control_by_type": {
                "success": True,
                "message": f"All {parameters.get('device_type', 'unknown')} devices turned {parameters.get('action', 'unknown')}"
            },
            "create_device_cronjob": {
                "success": True,
                "message": f"Cronjob created for device {parameters.get('buttonId', 'unknown')}"
            },
            "room_one_touch_control": {
                "success": True,
                "message": f"Room {parameters.get('room_id', 'unknown')} executed {parameters.get('one_touch_code', 'unknown')}"
            }
        }
        
        mock_result = mock_responses.get(tool_name, {"success": True, "message": f"Tool {tool_name} executed"})
        
        print(f"✅ Tool '{tool_name}' executed successfully (MOCK)")
        return {
            "result": mock_result, 
            "tool_name": tool_name, 
            "parameters": parameters,
            "mock": True,
            "real_mcp": False
        }
            
        # except Exception as e:
        #     print(f"❌ Error calling tool '{tool_name}': {e}")
        #     return None
    
    def list_tools(self) -> List[str]:
        """Liệt kê tất cả tools có sẵn"""
        if not self.available_tools:
            self.get_available_tools()
        return list(self.available_tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết của một tool"""
        if not self.available_tools:
            self.get_available_tools()
        return self.available_tools.get(tool_name)
    
    def get_tool_parameters(self, tool_name: str) -> Dict:
        """Lấy parameters của một tool"""
        tool_info = self.get_tool_info(tool_name)
        if tool_info:
            return tool_info.get('parameters', {})
        return {}
    
    def search_tools(self, query: str) -> List[Dict]:
        """Tìm kiếm tools dựa trên query"""
        if not self.available_tools:
            self.get_available_tools()
        
        matching_tools = []
        query_lower = query.lower()
        
        for tool_name, tool_info in self.available_tools.items():
            # Search in tool name
            if query_lower in tool_name.lower():
                matching_tools.append({
                    'name': tool_name,
                    'match_reason': 'name',
                    'info': tool_info
                })
                continue
            
            # Search in description
            description = tool_info.get('description', '').lower()
            if query_lower in description:
                matching_tools.append({
                    'name': tool_name,
                    'match_reason': 'description',
                    'info': tool_info
                })
        
        return matching_tools
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate parameters cho một tool"""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return False, [f"Tool '{tool_name}' not found"]
        
        required_params = tool_info.get('inputSchema', {}).get('required', [])
        available_params = tool_info.get('parameters', {})
        errors = []
        
        # Check required parameters
        for param in required_params:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
        
        # Check parameter types (basic validation)
        for param_name, param_value in parameters.items():
            if param_name in available_params:
                param_schema = available_params[param_name]
                expected_type = param_schema.get('type')
                if expected_type and not self._validate_type(param_value, expected_type):
                    errors.append(f"Parameter '{param_name}' should be of type {expected_type}")
        
        return len(errors) == 0, errors
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Basic type validation"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True  # Unknown type, assume valid