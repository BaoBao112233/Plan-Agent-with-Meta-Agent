"""
🚀 Plan Agent FastAPI Main Application
=====================================

FastAPI REST API for the Plan Agent with Meta Agent system
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import Dict, List, Optional
import uuid
from datetime import datetime

from api.models import (
    SmartHomeRequest, PrioritySelectionRequest, MCPToolRequest,
    PriorityPlansResponse, SelectedPlanResponse, PlanExecutionResponse,
    MCPToolsResponse, MCPToolExecutionResponse, HealthResponse,
    WebSocketMessage, PlanProgressUpdate
)
from api.services import PlanAgentService, MCPService, HealthService

# FastAPI app instance
app = FastAPI(
    title="Plan Agent with Meta Agent API",
    description="REST API for intelligent home automation using MCP tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service instances
plan_service = PlanAgentService()
mcp_service = MCPService()
health_service = HealthService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# ===============================================
# PLAN AGENT ENDPOINTS
# ===============================================

@app.post("/plans/create", response_model=PriorityPlansResponse)
async def create_priority_plans(request: SmartHomeRequest):
    """
    🎯 Create three priority plans for smart home automation
    
    Creates security, convenience, and energy efficiency plans using MCP tools.
    """
    try:
        result = await plan_service.create_priority_plans(
            user_input=request.user_input,
            enable_api=request.enable_api,
            verbose=request.verbose
        )
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "plan_created",
            "plan_id": result.plan_id,
            "input": request.user_input
        }))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plans/{plan_id}/select", response_model=SelectedPlanResponse)
async def select_priority_plan(plan_id: str, request: PrioritySelectionRequest):
    """
    🎯 Select a priority plan for execution
    
    Choose from:
    - 1: Security priority (maximum safety)
    - 2: Convenience priority (user experience)  
    - 3: Energy priority (resource optimization)
    """
    try:
        result = await plan_service.select_priority_plan(
            plan_id=plan_id,
            selected_priority=request.selected_priority
        )
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "plan_selected",
            "plan_id": plan_id,
            "priority": result.selected_priority
        }))
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plans/{plan_id}/execute", response_model=PlanExecutionResponse)
async def execute_plan(plan_id: str):
    """
    🚀 Execute the selected plan using MCP tools
    
    Executes all tasks in the selected plan sequentially.
    """
    try:
        result = await plan_service.execute_plan(plan_id)
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "plan_executed",
            "plan_id": plan_id,
            "status": result.status.value,
            "progress": result.progress_percentage
        }))
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plans/{plan_id}/status", response_model=PlanExecutionResponse)
async def get_plan_status(plan_id: str):
    """
    📊 Get current status of a plan
    
    Returns execution progress and task status.
    """
    try:
        result = await plan_service.get_plan_status(plan_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================================
# MCP TOOLS ENDPOINTS
# ===============================================

@app.get("/mcp/tools", response_model=MCPToolsResponse)
async def get_mcp_tools():
    """
    🛠️ Get list of available MCP tools
    
    Returns all available smart home automation tools.
    """
    try:
        result = await mcp_service.get_available_tools()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/tools/execute", response_model=MCPToolExecutionResponse)
async def execute_mcp_tool(request: MCPToolRequest):
    """
    🔧 Execute an MCP tool directly
    
    Execute any MCP tool with custom parameters.
    """
    try:
        result = await mcp_service.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "tool_executed",
            "tool_name": request.tool_name,
            "status": result.status
        }))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================================
# WEBSOCKET ENDPOINTS
# ===============================================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    🔄 WebSocket connection for real-time updates
    
    Provides real-time updates for plan execution and tool usage.
    """
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    client_id
                )
            elif message.get("type") == "subscribe":
                await manager.send_personal_message(
                    json.dumps({"type": "subscribed", "client_id": client_id}),
                    client_id
                )
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# ===============================================
# HEALTH & SYSTEM ENDPOINTS
# ===============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    ❤️ System health check
    
    Returns status of MCP server, available tools, and API configuration.
    """
    try:
        result = await health_service.get_health()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    🏠 API Documentation Landing Page
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Plan Agent API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .header { text-align: center; color: #2c3e50; }
            .section { margin: 30px 0; padding: 20px; border-left: 4px solid #3498db; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .method { color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
            .post { background: #28a745; }
            .get { background: #007bff; }
            code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Plan Agent with Meta Agent API</h1>
            <p>Intelligent home automation using MCP tools</p>
        </div>
        
        <div class="section">
            <h2>🎯 Plan Management</h2>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/plans/create</code> - Create priority plans
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/plans/{plan_id}/select</code> - Select a plan
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/plans/{plan_id}/execute</code> - Execute plan
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/plans/{plan_id}/status</code> - Get plan status
            </div>
        </div>
        
        <div class="section">
            <h2>🛠️ MCP Tools</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/mcp/tools</code> - List available tools
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/mcp/tools/execute</code> - Execute MCP tool
            </div>
        </div>
        
        <div class="section">
            <h2>🔄 Real-time</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/ws/{client_id}</code> - WebSocket connection
            </div>
        </div>
        
        <div class="section">
            <h2>📚 Documentation</h2>
            <p>
                • <a href="/docs">Interactive API Documentation (Swagger)</a><br>
                • <a href="/redoc">Alternative Documentation (ReDoc)</a><br>
                • <a href="/health">System Health Check</a>
            </p>
        </div>
    </body>
    </html>
    """

# ===============================================
# STARTUP EVENTS
# ===============================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Plan Agent FastAPI Server")
    print("📊 Health check at: /health")
    print("📚 Documentation at: /docs")
    print("🔄 WebSocket at: /ws/{client_id}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Plan Agent FastAPI Server")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )