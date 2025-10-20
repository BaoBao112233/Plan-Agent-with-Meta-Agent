# 🚀 Plan Agent FastAPI REST API

This directory contains the FastAPI REST API implementation for the Plan Agent with Meta Agent system.

## 📁 API Structure

```
api/
├── __init__.py         # Package initialization
├── main.py            # FastAPI application and routes
├── models.py          # Pydantic models for requests/responses
├── services.py        # Business logic services
└── routers.py         # Modular API routers
```

## 🎯 Key Features

### Plan Management
- **POST /plans/create** - Create security, convenience, and energy priority plans
- **POST /plans/{plan_id}/select** - Select a priority plan (1=Security, 2=Convenience, 3=Energy)
- **POST /plans/{plan_id}/execute** - Execute the selected plan using MCP tools
- **GET /plans/{plan_id}/status** - Get real-time plan execution status

### MCP Tools Integration
- **GET /mcp/tools** - List all available MCP smart home tools
- **POST /mcp/tools/execute** - Execute any MCP tool directly with custom parameters

### Real-time Communication
- **WebSocket /ws/{client_id}** - Real-time updates for plan execution and tool usage
- Live progress updates during plan execution
- Tool execution notifications

### System Health
- **GET /health** - System health check (MCP server, Groq API status)
- **GET /** - Interactive landing page with API documentation

## 🛠️ MCP Tools Available

1. **get_device_list** - Get all smart home devices
2. **switch_device_control** - Control switches (on/off)
3. **control_air_conditioner** - Manage AC settings
4. **create_device_cronjob** - Schedule device automation
5. **room_one_touch_control** - Room-level control
6. **one_touch_control_by_type** - Control by device type
7. **get_device_cronjobs** - View scheduled tasks

## 📊 API Models

### Request Models
- `SmartHomeRequest` - User input for plan creation
- `PrioritySelectionRequest` - Plan selection (1/2/3)
- `MCPToolRequest` - Direct tool execution
- `TaskUpdateRequest` - Task progress updates

### Response Models
- `PriorityPlansResponse` - Three priority plans with tasks
- `SelectedPlanResponse` - Selected plan confirmation
- `PlanExecutionResponse` - Execution status and progress
- `MCPToolsResponse` - Available tools list
- `MCPToolExecutionResponse` - Tool execution results

### WebSocket Models
- `WebSocketMessage` - Real-time messages
- `PlanProgressUpdate` - Live execution updates

## 🚀 Running the API

```bash
# Start the server
python run_api.py

# Or manually with uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing the API

```bash
# Run comprehensive tests
python test_api.py

# Or use curl for individual endpoints
curl -X POST "http://localhost:8000/plans/create" \
     -H "Content-Type: application/json" \
     -d '{"user_input": "Secure my home", "enable_api": true}'
```

## 📚 Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Landing Page**: http://localhost:8000/ (Overview)

## 🔧 Configuration

The API automatically configures:
- CORS middleware for cross-origin requests
- WebSocket connection management
- Mock MCP fallback when server unavailable
- Comprehensive error handling and logging

## 🏗️ Architecture

```
Client Request → FastAPI Router → Service Layer → MCP Client → Smart Home Devices
                      ↓
                 WebSocket Updates → Real-time Client Notifications
```

The API follows a clean architecture pattern:
1. **Router Layer** - HTTP endpoints and request validation
2. **Service Layer** - Business logic and MCP integration
3. **Model Layer** - Data validation and serialization
4. **Client Layer** - MCP tool execution and device control