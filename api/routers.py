"""
🎯 Plan Agent API Routers
========================

Modular API routers for different functionalities
"""

from fastapi import APIRouter, HTTPException
from api.models import (
    SmartHomeRequest, PrioritySelectionRequest, MCPToolRequest,
    PriorityPlansResponse, SelectedPlanResponse, PlanExecutionResponse,
    MCPToolsResponse, MCPToolExecutionResponse
)
from api.services import PlanAgentService, MCPService

# Plan management router
plan_router = APIRouter(prefix="/plans", tags=["Plans"])
plan_service = PlanAgentService()

@plan_router.post("/create", response_model=PriorityPlansResponse)
async def create_priority_plans(request: SmartHomeRequest):
    """Create three priority plans for smart home automation"""
    try:
        return await plan_service.create_priority_plans(
            user_input=request.user_input,
            enable_api=request.enable_api,
            verbose=request.verbose
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@plan_router.post("/{plan_id}/select", response_model=SelectedPlanResponse)
async def select_priority_plan(plan_id: str, request: PrioritySelectionRequest):
    """Select a priority plan for execution"""
    try:
        return await plan_service.select_priority_plan(
            plan_id=plan_id,
            selected_priority=request.selected_priority
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@plan_router.post("/{plan_id}/execute", response_model=PlanExecutionResponse)
async def execute_plan(plan_id: str):
    """Execute the selected plan using MCP tools"""
    try:
        return await plan_service.execute_plan(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@plan_router.get("/{plan_id}/status", response_model=PlanExecutionResponse)
async def get_plan_status(plan_id: str):
    """Get current status of a plan"""
    try:
        return await plan_service.get_plan_status(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP tools router
mcp_router = APIRouter(prefix="/mcp", tags=["MCP Tools"])
mcp_service = MCPService()

@mcp_router.get("/tools", response_model=MCPToolsResponse)
async def get_mcp_tools():
    """Get list of available MCP tools"""
    try:
        return await mcp_service.get_available_tools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mcp_router.post("/tools/execute", response_model=MCPToolExecutionResponse)
async def execute_mcp_tool(request: MCPToolRequest):
    """Execute an MCP tool directly"""
    try:
        return await mcp_service.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))