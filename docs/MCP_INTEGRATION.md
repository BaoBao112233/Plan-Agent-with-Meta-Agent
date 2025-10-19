# MCP Integration với Plan Agent

## Tổng quan

Repo này đã được cập nhật để tích hợp với **Model Context Protocol (MCP)** server. Thay vì ToolAgent tự tạo và quản lý tools, giờ đây ToolAgent sẽ kết nối và sử dụng các tools có sẵn từ MCP server.

## 🔧 Cấu trúc mới

### 1. **MCPClient** (`src/mcp_client.py`)
- Client để kết nối với MCP server
- Hỗ trợ các chức năng:
  - `get_available_tools()`: Lấy danh sách tools từ server
  - `call_tool()`: Thực thi tools
  - `search_tools()`: Tìm kiếm tools
  - `validate_parameters()`: Validate input parameters

### 2. **MCPToolAgent** (`src/agent/tool/mcp_agent.py`)
- Tool Agent mới sử dụng MCP server
- Thay thế ToolAgent cũ (giờ là LegacyToolAgent)
- Các chức năng:
  - List tools có sẵn
  - Search tools theo keywords
  - Lấy thông tin chi tiết của tools
  - Thực thi tools với parameters
  - Help và guidance

### 3. **MCPToolWrapper** (`src/mcp_tools.py`)
- Wrapper để tích hợp MCP tools vào MetaAgent
- Chuyển đổi MCP tools thành format mà MetaAgent có thể sử dụng
- Tự động tạo Pydantic schemas cho tool parameters

## 🚀 Cách sử dụng

### 1. Cấu hình

Thêm MCP server URL vào `.env`:
```env
MCP_SERVER_URL=http://localhost:9031
```

### 2. Chạy MCP Server

Đảm bảo MCP server đang chạy:
```bash
cd /path/to/mcp/oxii-server
docker compose up -d
```

### 3. Sử dụng MCP Tool Agent

```python
from src.agent.tool import ToolAgent  # Imports MCPToolAgent
from src.inference.groq import ChatGroq

llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
tool_agent = ToolAgent(llm=llm, verbose=True)

# List all available tools
response = tool_agent.invoke("list all tools")

# Search for specific tools
response = tool_agent.invoke("search for device control tools")

# Get tool information
response = tool_agent.invoke("get info about get_device_list")

# Execute a tool
response = tool_agent.invoke("execute get_device_list with token=abc123")
```

### 4. Sử dụng với MetaAgent

```python
from src.mcp_tools import get_mcp_tools
from src.agent.meta import MetaAgent

# Load MCP tools
mcp_tools = get_mcp_tools()

# Create MetaAgent with MCP tools
meta_agent = MetaAgent(llm=llm, tools=mcp_tools, verbose=True)
response = meta_agent.invoke("Control some smart home devices")
```

### 5. Plan Agent với MCP Integration

Plan Agent tự động sử dụng MetaAgent, và MetaAgent có thể được cấu hình với MCP tools:

```python
from src.agent.plan import PlanAgent

plan_agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)
response = plan_agent.invoke("Create a plan to control smart home devices")
```

## 📋 Available MCP Tools

Dựa trên OXII MCP server, các tools có sẵn bao gồm:

1. **get_device_list** - Liệt kê devices, rooms, houses
2. **switch_device_control** - Điều khiển switch devices (ON/OFF)
3. **control_air_conditioner** - Điều khiển điều hòa (mode, temp, fan)
4. **create_device_cronjob** - Tạo cronjobs cho devices
5. **one_touch_control_all_devices** - Điều khiển tất cả devices
6. **one_touch_control_by_type** - Điều khiển theo loại device
7. **room_one_touch_control** - Điều khiển theo phòng

## 🧪 Testing

### Test MCP Integration
```bash
python test_mcp_integration.py
```

### Test với App
```bash
python app_mcp.py
```

### Test Options trong App
1. **Option 1**: Test MCP Tool Agent trực tiếp
2. **Option 2**: Test MetaAgent với MCP tools
3. **Option 3**: Test Plan Agent (full integration)

## 🔄 Migration từ ToolAgent cũ

### Before (Legacy)
```python
from src.agent.tool import ToolAgent

tool_agent = ToolAgent(location='tools.py', llm=llm)
response = tool_agent.invoke("create a weather tool")
```

### After (MCP)
```python
from src.agent.tool import ToolAgent  # Now MCPToolAgent

tool_agent = ToolAgent(llm=llm)  # No location needed
response = tool_agent.invoke("list weather tools")  # Use existing tools
```

### Backward Compatibility
Legacy ToolAgent vẫn có sẵn:
```python
from src.agent.tool import LegacyToolAgent

legacy_agent = LegacyToolAgent(location='tools.py', llm=llm)
```

## 🛠 Troubleshooting

### MCP Server Connection Issues
- Kiểm tra MCP server có đang chạy: `curl http://localhost:9031/sse`
- Kiểm tra network connectivity
- Xem logs: `docker compose logs -f oxii-server`

### Tool Execution Errors
- Đảm bảo parameters đúng format
- Kiểm tra OXII credentials trong MCP server
- Validate token nếu cần thiết

### Performance Issues
- MCP tools được cache sau lần đầu load
- Sử dụng `refresh_mcp_tools()` để reload nếu cần

## 📚 Architecture Flow

```
User Query → Plan Agent → MetaAgent → MCP Tools → OXII API
                ↓
            API Server (Plan Status Updates)
```

1. **User** gửi query đến Plan Agent
2. **Plan Agent** tạo plan và gửi status lên API server
3. **Plan Agent** sử dụng **MetaAgent** để thực hiện tasks
4. **MetaAgent** có access đến **MCP Tools**
5. **MCP Tools** kết nối với **OXII smart home devices**
6. Results được trả về và plan status được cập nhật

## 🎯 Benefits của MCP Integration

1. **Centralized Tools**: Tất cả tools được quản lý tại MCP server
2. **No Code Generation**: Không cần tạo tools động nữa
3. **Type Safety**: MCP tools có schema rõ ràng
4. **Scalability**: Dễ dàng thêm tools mới qua MCP server
5. **Separation of Concerns**: Logic tool riêng biệt với agent logic
6. **Real Devices**: Trực tiếp điều khiển smart home devices thông qua OXII API

Với setup này, Plan Agent không chỉ có khả năng planning mà còn có thể thực sự điều khiển các thiết bị smart home thông qua MCP server! 🏠🤖