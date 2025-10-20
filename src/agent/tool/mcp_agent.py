from langchain_core.runnables.graph import MermaidDrawMethod
from src.message import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
# from IPython.display import display, Image  # Optional import
from src.inference import BaseInference
from src.router import LLMRouter
from src.agent import BaseAgent
from src.mcp_client import MCPClient
# from termcolor import colored  # Optional import
from typing import TypedDict

# Define AgentState for MCPToolAgent
class AgentState(TypedDict):
    input: str
    route: str
    output: str
import json

def colored(text, color=None, on_color=None, attrs=None):
    """Simple colored replacement"""
    return text

class MCPToolAgent(BaseAgent):
    """Tool Agent sử dụng MCP server thay vì tự tạo tools"""
    
    def __init__(self, llm: BaseInference = None, mcp_url: str = None, verbose=False):
        self.name = 'MCP Tool Agent'
        self.llm = llm
        self.verbose = verbose
        self.mcp_client = MCPClient(mcp_url)
        self.graph = self.create_graph()
        
        # Load available tools từ MCP server
        self.refresh_tools()
    
    def refresh_tools(self):
        """Refresh danh sách tools từ MCP server"""
        tools = self.mcp_client.get_available_tools()
        if self.verbose:
            print(f"🔄 Loaded {len(tools)} tools from MCP server")
            for tool_name in tools.keys():
                print(f"  - {tool_name}")
    
    def router(self, state: AgentState):
        """Route query để xác định action cần thực hiện"""
        input_value = state.get('input', '') or ''  # Handle None case
        input_text = input_value.lower() if input_value else ''
        
        # Simple keyword-based routing when LLM not available
        if self.llm is None:
            if any(keyword in input_text for keyword in ['list', 'available', 'tools', 'show']):
                return {**state, 'route': 'list_tools'}
            elif any(keyword in input_text for keyword in ['search', 'find']):
                return {**state, 'route': 'search_tools'}
            elif any(keyword in input_text for keyword in ['info', 'detail', 'describe']):
                return {**state, 'route': 'get_tool_info'}
            elif any(keyword in input_text for keyword in ['help', 'how']):
                return {**state, 'route': 'help_with_tool'}
            elif any(keyword in input_text for keyword in ['run', 'execute', 'call', 'control', 'turn', 'get']):
                return {**state, 'route': 'execute_tool'}
            else:
                return {**state, 'route': 'list_tools'}  # Default to list_tools
        
        # Use LLM routing when available
        routes = [
            {
                'name': 'list_tools',
                'description': 'Only when user asks to see available tools, list tools, or what tools are there. Not for executing tools.'
            },
            {
                'name': 'search_tools',
                'description': 'When user wants to search for tools by keyword or functionality but not execute them'
            },
            {
                'name': 'get_tool_info',
                'description': 'When user wants detailed information about a specific tool (parameters, usage) but not execute it'
            },
            {
                'name': 'execute_tool',
                'description': 'When user wants to actually run/execute/call a tool with specific parameters or perform an action like "get device list", "turn on", "control", etc.'
            },
            {
                'name': 'help_with_tool',
                'description': 'When user needs help or guidance on how to use tools'
            }
        ]
        
        llm_router = LLMRouter(routes=routes, llm=self.llm, verbose=False)
        input_query = state.get('input') or ''
        route = llm_router.invoke(input_query)
        return {**state, 'route': route}
    
    def list_tools(self, state: AgentState):
        """Liệt kê tất cả tools có sẵn"""
        tools = self.mcp_client.list_tools()
        
        if not tools:
            output = "❌ No tools available from MCP server. Please check server connection."
        else:
            output = f"📋 Available MCP Tools ({len(tools)}):\n\n"
            for i, tool_name in enumerate(tools, 1):
                tool_info = self.mcp_client.get_tool_info(tool_name)
                description = tool_info.get('description', 'No description available')
                output += f"{i}. **{tool_name}**\n   {description}\n\n"
        
        return {**state, 'output': output}
    
    def search_tools(self, state: AgentState):
        """Tìm kiếm tools dựa trên query"""
        query = state.get('input') or ''
        
        # Extract search keywords từ query
        search_keywords = self.extract_search_keywords(query)
        
        if not search_keywords:
            output = "❌ Please provide keywords to search for tools."
            return {**state, 'output': output}
        
        results = []
        for keyword in search_keywords:
            keyword_results = self.mcp_client.search_tools(keyword)
            results.extend(keyword_results)
        
        # Remove duplicates
        unique_results = []
        seen_tools = set()
        for result in results:
            if result['name'] not in seen_tools:
                unique_results.append(result)
                seen_tools.add(result['name'])
        
        if not unique_results:
            output = f"❌ No tools found matching: {', '.join(search_keywords)}"
        else:
            output = f"🔍 Found {len(unique_results)} tools matching '{', '.join(search_keywords)}':\n\n"
            for result in unique_results:
                tool_name = result['name']
                match_reason = result['match_reason']
                description = result['info'].get('description', 'No description')
                output += f"• **{tool_name}** (matched by {match_reason})\n  {description}\n\n"
        
        return {**state, 'output': output}
    
    def get_tool_info(self, state: AgentState):
        """Lấy thông tin chi tiết về một tool cụ thể"""
        query = state.get('input') or ''
        
        # Extract tool name từ query
        tool_name = self.extract_tool_name(query)
        
        if not tool_name:
            output = "❌ Please specify which tool you want information about."
            return {**state, 'output': output}
        
        tool_info = self.mcp_client.get_tool_info(tool_name)
        
        if not tool_info:
            # Try to find similar tools
            similar_tools = self.mcp_client.search_tools(tool_name)
            if similar_tools:
                suggestions = ", ".join([t['name'] for t in similar_tools[:3]])
                output = f"❌ Tool '{tool_name}' not found. Did you mean: {suggestions}?"
            else:
                output = f"❌ Tool '{tool_name}' not found."
            return {**state, 'output': output}
        
        # Format tool information
        output = f"🔧 **{tool_name}**\n\n"
        output += f"**Description:** {tool_info.get('description', 'No description available')}\n\n"
        
        parameters = tool_info.get('parameters', {})
        if parameters:
            output += "**Parameters:**\n"
            for param_name, param_info in parameters.items():
                param_type = param_info.get('type', 'unknown')
                param_desc = param_info.get('description', 'No description')
                required = " (required)" if param_name in tool_info.get('inputSchema', {}).get('required', []) else ""
                output += f"  • `{param_name}` ({param_type}){required}: {param_desc}\n"
        else:
            output += "**Parameters:** None\n"
        
        return {**state, 'output': output}
    
    def execute_tool(self, state: AgentState):
        """Thực thi một tool với parameters được cung cấp"""
        query = state.get('input') or ''
        
        # Sử dụng LLM để extract tool name và parameters từ query
        execution_info = self.extract_execution_info(query)
        
        tool_name = execution_info.get('tool_name')
        parameters = execution_info.get('parameters', {})
        
        if not tool_name:
            output = "❌ Please specify which tool to execute."
            return {**state, 'output': output}
        
        # Validate tool exists
        if tool_name not in self.mcp_client.available_tools:
            output = f"❌ Tool '{tool_name}' not found. Use 'list tools' to see available tools."
            return {**state, 'output': output}
        
        # Auto-fill missing required parameters với defaults
        parameters = self.auto_fill_parameters(tool_name, parameters, query)
        
        # Validate parameters
        is_valid, errors = self.mcp_client.validate_parameters(tool_name, parameters)
        if not is_valid:
            # Show parameter hints instead of hard failure
            output = f"❌ Parameter validation failed:\n" + "\n".join([f"  • {error}" for error in errors])
            
            # Add helpful parameter hints
            tool_info = self.mcp_client.get_tool_info(tool_name)
            if tool_info:
                required_params = tool_info.get('inputSchema', {}).get('required', [])
                if required_params:
                    output += f"\n\n💡 **Required parameters for {tool_name}:**\n"
                    params_info = tool_info.get('parameters', {})
                    for param in required_params:
                        param_info = params_info.get(param, {})
                        param_desc = param_info.get('description', 'No description')
                        output += f"  • `{param}`: {param_desc}\n"
            
            return {**state, 'output': output}
        
        # Execute tool
        result = self.mcp_client.call_tool(tool_name, parameters)
        
        if result is None:
            output = f"❌ Failed to execute tool '{tool_name}'"
        else:
            # Check if it's real MCP or mock
            is_real_mcp = result.get('real_mcp', False)
            is_mock = result.get('mock', False)
            
            if is_real_mcp:
                output = f"🔌 **{tool_name}** executed via REAL MCP SERVER:\n\n"
            elif is_mock:
                output = f"🧪 **{tool_name}** executed via MOCK (MCP server unavailable):\n\n"
            else:
                output = f"✅ **{tool_name}** executed:\n\n"
            
            # Format result nicely
            if isinstance(result, dict):
                # Display the actual result data
                actual_result = result.get('result', result)
                if isinstance(actual_result, dict):
                    output += json.dumps(actual_result, indent=2, ensure_ascii=False)
                else:
                    output += str(actual_result)
            else:
                output += str(result)
        
        return {**state, 'output': output}
    
    def help_with_tool(self, state: AgentState):
        """Cung cấp help và guidance cho tool usage"""
        query = state.get('input') or ''
        tool_name = self.extract_tool_name(query)
        
        if not tool_name:
            output = """🆘 **MCP Tool Agent Help**
            
Available commands:
• `list tools` - Show all available tools
• `search for [keyword]` - Search tools by keyword  
• `info about [tool_name]` - Get detailed tool information
• `execute [tool_name] with [parameters]` - Run a tool
• `help with [tool_name]` - Get usage examples for a tool

Example usage:
• "list all available tools"
• "search for device control tools"
• "get info about switch_device_control"
• "execute get_device_list with token=abc123"
"""
            return {**state, 'output': output}
        
        tool_info = self.mcp_client.get_tool_info(tool_name)
        if not tool_info:
            output = f"❌ Tool '{tool_name}' not found."
            return {**state, 'output': output}
        
        # Generate usage examples
        output = f"🆘 **Help for {tool_name}**\n\n"
        output += f"**Description:** {tool_info.get('description', 'No description')}\n\n"
        
        parameters = tool_info.get('parameters', {})
        required_params = tool_info.get('inputSchema', {}).get('required', [])
        
        if parameters:
            output += "**Usage Examples:**\n"
            
            # Example 1: With all required parameters
            if required_params:
                example_params = {}
                for param in required_params:
                    param_info = parameters[param]
                    param_type = param_info.get('type', 'string')
                    if param_type == 'string':
                        example_params[param] = f"your_{param}_value"
                    elif param_type == 'integer':
                        example_params[param] = 123
                    elif param_type == 'boolean':
                        example_params[param] = True
                    else:
                        example_params[param] = f"your_{param}_value"
                
                example_str = ", ".join([f"{k}={v}" for k, v in example_params.items()])
                output += f"```\nexecute {tool_name} with {example_str}\n```\n"
        else:
            output += f"```\nexecute {tool_name}\n```\n"
        
        return {**state, 'output': output}
    
    def extract_search_keywords(self, query: str) -> list[str]:
        """Extract search keywords từ query"""
        # Simple keyword extraction - có thể improve bằng LLM
        keywords = []
        query_lower = query.lower()
        
        # Remove common words
        stop_words = {'search', 'for', 'find', 'tool', 'tools', 'the', 'a', 'an', 'with', 'that', 'can'}
        words = query_lower.split()
        
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)
        
        return keywords
    
    def auto_fill_parameters(self, tool_name: str, parameters: dict, query: str) -> dict:
        """Auto-fill missing required parameters với reasonable defaults"""
        tool_info = self.mcp_client.get_tool_info(tool_name)
        if not tool_info:
            return parameters
        
        required_params = tool_info.get('inputSchema', {}).get('required', [])
        params_info = tool_info.get('parameters', {})
        
        # Create a copy to avoid modifying original
        filled_params = parameters.copy()
        query_lower = query.lower()
        
        for param in required_params:
            if param not in filled_params:
                param_info = params_info.get(param, {})
                param_type = param_info.get('type', 'string')
                
                # Smart parameter filling based on parameter name and query context
                if param == 'token':
                    filled_params[param] = "demo_token"
                elif param == 'buttonId':
                    # Try to extract number from query, otherwise use default
                    import re
                    numbers = re.findall(r'\d+', query)
                    filled_params[param] = int(numbers[0]) if numbers else 1  # Integer not string
                elif param == 'action':
                    if any(word in query_lower for word in ['on', 'turn on', 'enable', 'start']):
                        filled_params[param] = "on"
                    elif any(word in query_lower for word in ['off', 'turn off', 'disable', 'stop']):
                        filled_params[param] = "off"
                    else:
                        filled_params[param] = "on"  # Default
                elif param == 'command':
                    if any(word in query_lower for word in ['on', 'turn on', 'enable']):
                        filled_params[param] = "on"
                    elif any(word in query_lower for word in ['off', 'turn off', 'disable']):
                        filled_params[param] = "off"
                    else:
                        filled_params[param] = "on"
                elif param == 'device_type':
                    if 'light' in query_lower:
                        filled_params[param] = "LIGHT"
                    elif 'ac' in query_lower or 'air' in query_lower or 'conditioner' in query_lower:
                        filled_params[param] = "CONDITIONER"
                    elif 'tv' in query_lower:
                        filled_params[param] = "TV"
                    else:
                        filled_params[param] = "LIGHT"  # Default
                elif param == 'room_id':
                    # Extract room from query
                    rooms = ['living room', 'bedroom', 'kitchen', 'bathroom']
                    for room in rooms:
                        if room in query_lower:
                            filled_params[param] = room.replace(' ', '_')
                            break
                    else:
                        filled_params[param] = "living_room"  # Default
                elif param in ['power', 'mode', 'temp', 'fan_speed', 'swing_h', 'swing_v']:
                    # AC specific parameters
                    if param == 'power':
                        filled_params[param] = "on" if 'on' in query_lower else "off"
                    elif param == 'mode':
                        if 'cool' in query_lower:
                            filled_params[param] = "cool"
                        elif 'heat' in query_lower:
                            filled_params[param] = "heat"
                        else:
                            filled_params[param] = "auto"
                    elif param == 'temp':
                        # Try to extract temperature from query
                        import re
                        temps = re.findall(r'(\d{1,2})\s*(?:degree|°|celsius|c)', query_lower)
                        filled_params[param] = temps[0] if temps else "24"  # String not int
                    elif param == 'fan_speed':
                        if 'high' in query_lower:
                            filled_params[param] = "high"
                        elif 'low' in query_lower:
                            filled_params[param] = "low"
                        else:
                            filled_params[param] = "auto"
                    elif param in ['swing_h', 'swing_v']:
                        filled_params[param] = "off"
                elif param_type == 'boolean':
                    filled_params[param] = True
                elif param_type == 'integer':
                    filled_params[param] = 1
                else:
                    # String type, provide generic default
                    filled_params[param] = f"default_{param}"
        
        if filled_params != parameters:
            if self.verbose:
                added_params = {k: v for k, v in filled_params.items() if k not in parameters}
                print(f"🔧 Auto-filled parameters: {added_params}")
        
        return filled_params
    
    def extract_tool_name(self, query: str) -> str:
        """Extract tool name từ query"""
        available_tools = self.mcp_client.list_tools()
        query_lower = query.lower()
        
        # Direct match
        for tool in available_tools:
            if tool.lower() in query_lower:
                return tool
        
        # Fuzzy match (simple)
        for tool in available_tools:
            tool_words = tool.lower().split('_')
            if any(word in query_lower for word in tool_words if len(word) > 3):
                return tool
        
        return ""
    
    def extract_execution_info(self, query: str) -> dict:
        """Extract tool name và parameters từ execution query sử dụng LLM"""
        
        # Get detailed tool information for better parameter extraction
        tools_info = []
        for tool_name in self.mcp_client.list_tools():
            tool_info = self.mcp_client.get_tool_info(tool_name)
            if tool_info:
                required_params = tool_info.get('inputSchema', {}).get('required', [])
                params_info = tool_info.get('parameters', {})
                
                tool_desc = f"- {tool_name}: {tool_info.get('description', '')}"
                if required_params:
                    param_details = []
                    for param in required_params:
                        param_info = params_info.get(param, {})
                        param_type = param_info.get('type', 'string')
                        param_details.append(f"{param}({param_type})")
                    tool_desc += f" | Required: {', '.join(param_details)}"
                tools_info.append(tool_desc)
        
        system_prompt = f"""You are a smart home tool execution parser. Extract tool name and parameters from user query.

Available tools:
{chr(10).join(tools_info)}

Rules:
1. If user asks to "list" or "show" tools → Don't extract parameters, return empty
2. If user wants to execute a tool → Extract the most appropriate tool and provide required parameters
3. For missing required parameters, use reasonable defaults or ask user

Common parameter patterns:
- token: Use "demo_token" as default
- buttonId: Extract number from context as integer (e.g., 1, 2, 3)
- action: "on"/"off" based on user intent
- room_id: Extract room name from query
- device_type: "LIGHT", "AC", "TV" etc.
- temp: Temperature as string (e.g., "22", "25")

Return JSON format:
{{
    "tool_name": "exact_tool_name_or_empty",
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }}
}}

Examples:
- "get device list" → {{"tool_name": "get_device_list", "parameters": {{"token": "demo_token"}}}}
- "turn on light 3" → {{"tool_name": "switch_device_control", "parameters": {{"token": "demo_token", "buttonId": 3, "action": "on"}}}}
- "turn on bedroom light" → {{"tool_name": "switch_device_control", "parameters": {{"token": "demo_token", "buttonId": 1, "action": "on"}}}}
- "set AC to 22 degrees" → {{"tool_name": "control_air_conditioner", "parameters": {{"power": "on", "temp": "22", "mode": "auto"}}}}
- "list tools" → {{"tool_name": "", "parameters": {{}}}}
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(system_prompt),
                HumanMessage(f"Parse this query: {query}")
            ], json=True)
            
            return response.content
        except Exception as e:
            if self.verbose:
                print(f"Error parsing execution info: {e}")
            return {"tool_name": "", "parameters": {}}
    
    def controller(self, state: AgentState):
        """Controller cho graph routing"""
        return state.get('route')
    
    def create_graph(self):
        """Tạo execution graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node('router', self.router)
        workflow.add_node('list_tools', self.list_tools)
        workflow.add_node('search_tools', self.search_tools)
        workflow.add_node('get_tool_info', self.get_tool_info)
        workflow.add_node('execute_tool', self.execute_tool)
        workflow.add_node('help_with_tool', self.help_with_tool)
        
        # Set entry point
        workflow.set_entry_point('router')
        
        # Add conditional edges
        workflow.add_conditional_edges('router', self.controller)
        
        # All nodes end
        workflow.add_edge('list_tools', END)
        workflow.add_edge('search_tools', END)
        workflow.add_edge('get_tool_info', END)
        workflow.add_edge('execute_tool', END)
        workflow.add_edge('help_with_tool', END)
        
        return workflow.compile(debug=False)
    
    def invoke(self, input: str) -> dict[str, str]:
        """Execute tool agent với input query"""
        if self.verbose:
            print(f'Entering ' + colored(self.name, 'black', 'on_white'))
            print(colored(f'Query: {input}', color='grey', attrs=['bold']))
        
        # Refresh tools để đảm bảo có latest tools
        self.refresh_tools()
        
        state = {
            'input': input,
            'route': '',
            'tool_data': {},
            'error': '',
            'output': ''
        }
        
        result = self.graph.invoke(state)
        output = result.get('output', '')
        route = result.get('route', '')
        
        if self.verbose:
            print(colored(f'Route: {route}', color='blue', attrs=['bold']))
            print(colored(f'Output: {output}', color='green'))
        
        return {
            'route': route,
            'output': output,
            'available_tools': len(self.mcp_client.available_tools)
        }
    
    def stream(self, input: str):
        """Streaming interface (placeholder)"""
        pass