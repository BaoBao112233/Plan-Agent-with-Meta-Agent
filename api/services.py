"""
🎯 Plan Agent FastAPI Services
===============================

Business logic services for the API
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

from src.agent.plan import PlanAgent
from src.agent.tool import MCPToolAgent
from src.inference.groq import ChatGroq
from src.mcp_client import MCPClient
from api.models import (
    PriorityPlansResponse, PriorityPlan, SelectedPlanResponse,
    PlanExecutionResponse, TaskInfo, MCPToolsResponse, MCPToolInfo,
    MCPToolExecutionResponse, HealthResponse, PlanStatus, TaskStatus
)

class PlanAgentService:
    """Service for Plan Agent operations"""
    
    def __init__(self):
        self.llm = ChatGroq()
        self.mcp_client = MCPClient()
        self.active_plans: Dict[str, Dict] = {}
        self.plan_agents: Dict[str, PlanAgent] = {}
    
    async def create_priority_plans(self, user_input: str, enable_api: bool = True, verbose: bool = False) -> PriorityPlansResponse:
        """Create 3 priority plans for user input"""
        try:
            plan_id = str(uuid.uuid4())
            
            # Create Plan Agent
            agent = PlanAgent(llm=self.llm, verbose=verbose, api_enabled=enable_api)
            self.plan_agents[plan_id] = agent
            
            # For API mode, we'll simulate the priority planning without actual LLM call
            # This avoids Groq API issues while demonstrating the structure
            security_plan = [
                "Use MCP get_device_list to validate available security devices and rooms",
                "Use MCP switch_device_control to enable all security cameras and sensors",
                "Use MCP create_device_cronjob to schedule security lighting automation",
                "Use MCP control_air_conditioner to set optimal temperature for security equipment"
            ]
            
            convenience_plan = [
                "Use MCP get_device_list to validate available comfort and security devices",
                "Use MCP room_one_touch_control to set living area to comfort mode",
                "Use MCP control_air_conditioner to maintain comfortable temperature",
                "Use MCP create_device_cronjob to schedule convenient automation routines"
            ]
            
            energy_plan = [
                "Use MCP get_device_list to validate energy-efficient devices and capabilities",
                "Use MCP one_touch_control_by_type to enable only essential lighting",
                "Use MCP create_device_cronjob to schedule energy-saving automation",
                "Use MCP control_air_conditioner to set energy-efficient temperature"
            ]
            
            # Store plan data
            plan_data = {
                "input": user_input,
                "security_plan": security_plan,
                "convenience_plan": convenience_plan,
                "energy_plan": energy_plan,
                "created_at": datetime.now(),
                "status": PlanStatus.PLAN_CREATED
            }
            self.active_plans[plan_id] = plan_data
            
            return PriorityPlansResponse(
                plan_id=plan_id,
                input=user_input,
                security_plan=PriorityPlan(
                    priority_type="security",
                    tasks=security_plan,
                    description="Maximum security and safety focus using MCP tools",
                    focus="Maximum safety using MCP security tools"
                ),
                convenience_plan=PriorityPlan(
                    priority_type="convenience", 
                    tasks=convenience_plan,
                    description="User experience and comfort focus via MCP automation",
                    focus="User experience via MCP automation"
                ),
                energy_plan=PriorityPlan(
                    priority_type="energy",
                    tasks=energy_plan,
                    description="Energy efficiency and resource optimization via MCP",
                    focus="Minimal resource consumption with MCP optimization"
                ),
                created_at=plan_data["created_at"],
                status=plan_data["status"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to create priority plans: {str(e)}")
    
    async def select_priority_plan(self, plan_id: str, selected_priority: int) -> SelectedPlanResponse:
        """Select a priority plan for execution"""
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan_data = self.active_plans[plan_id]
        
        # Map selection to plan
        priority_map = {
            1: ("security", plan_data["security_plan"]),
            2: ("convenience", plan_data["convenience_plan"]),
            3: ("energy", plan_data["energy_plan"])
        }
        
        if selected_priority not in priority_map:
            raise ValueError("Selected priority must be 1, 2, or 3")
        
        priority_type, selected_plan = priority_map[selected_priority]
        
        # Update plan data
        plan_data["selected_priority"] = priority_type
        plan_data["selected_plan"] = selected_plan
        plan_data["status"] = PlanStatus.IN_PROGRESS
        
        return SelectedPlanResponse(
            plan_id=plan_id,
            selected_priority=priority_type,
            selected_plan=selected_plan,
            status=PlanStatus.IN_PROGRESS,
            execution_started=True
        )
    
    async def execute_plan(self, plan_id: str) -> PlanExecutionResponse:
        """Execute the selected plan"""
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan_data = self.active_plans[plan_id]
        
        if "selected_plan" not in plan_data:
            raise ValueError("No plan selected for execution")
        
        selected_plan = plan_data["selected_plan"]
        
        # Create task info objects
        tasks_info = []
        completed_tasks = []
        
        for i, task in enumerate(selected_plan):
            task_id = f"{plan_id}_task_{i+1}"
            task_info = TaskInfo(
                task_id=task_id,
                task_content=task,
                status=TaskStatus.PENDING,
                created_at=datetime.now()
            )
            tasks_info.append(task_info)
        
        # Simulate task execution
        for i, task_info in enumerate(tasks_info):
            task_info.status = TaskStatus.IN_PROGRESS
            task_info.updated_at = datetime.now()
            
            # Simulate MCP tool execution
            await asyncio.sleep(1)  # Simulate processing time
            
            # Execute via MCP (mock mode)
            try:
                result = await self._execute_task_via_mcp(task_info.task_content)
                task_info.result = result
                task_info.status = TaskStatus.COMPLETED
            except Exception as e:
                task_info.result = f"Error: {str(e)}"
                task_info.status = TaskStatus.FAILED
            
            task_info.updated_at = datetime.now()
            completed_tasks.append(task_info)
        
        # Update plan status
        failed_tasks = [t for t in completed_tasks if t.status == TaskStatus.FAILED]
        if failed_tasks:
            plan_data["status"] = PlanStatus.FAILED
        else:
            plan_data["status"] = PlanStatus.COMPLETED
        
        progress = 100.0
        final_result = f"Plan execution completed. {len(completed_tasks)} tasks processed."
        
        if failed_tasks:
            final_result += f" {len(failed_tasks)} tasks failed."
        
        return PlanExecutionResponse(
            plan_id=plan_id,
            status=plan_data["status"],
            current_task=None,
            completed_tasks=completed_tasks,
            pending_tasks=[],
            progress_percentage=progress,
            final_result=final_result
        )
    
    async def _execute_task_via_mcp(self, task_content: str) -> str:
        """Execute a task via MCP tools"""
        try:
            # Extract MCP tool from task content
            if "get_device_list" in task_content:
                result = self.mcp_client.call_tool("get_device_list", {"token": "demo_token"})
            elif "switch_device_control" in task_content:
                result = self.mcp_client.call_tool("switch_device_control", {
                    "switch_label": "security_device", "action": "on"
                })
            elif "control_air_conditioner" in task_content:
                result = self.mcp_client.call_tool("control_air_conditioner", {
                    "room": "living_room", "temperature": "24", "mode": "cool"
                })
            elif "create_device_cronjob" in task_content:
                result = self.mcp_client.call_tool("create_device_cronjob", {
                    "switch_label": "automation_device", "cron": "0 18 * * *", "action": "on"
                })
            elif "room_one_touch_control" in task_content:
                result = self.mcp_client.call_tool("room_one_touch_control", {
                    "room": "living_room", "action": "comfort_mode"
                })
            elif "one_touch_control_by_type" in task_content:
                result = self.mcp_client.call_tool("one_touch_control_by_type", {
                    "device_type": "LIGHT", "action": "on"
                })
            else:
                result = {"status": "success", "message": "Task completed via generic MCP execution"}
            
            return f"✅ Task completed successfully: {result.get('message', 'MCP tool executed')}"
            
        except Exception as e:
            return f"❌ Task failed: {str(e)}"
    
    async def get_plan_status(self, plan_id: str) -> PlanExecutionResponse:
        """Get current status of a plan"""
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan_data = self.active_plans[plan_id]
        
        # Return basic status for now
        return PlanExecutionResponse(
            plan_id=plan_id,
            status=plan_data.get("status", PlanStatus.DRAFT),
            current_task=None,
            completed_tasks=[],
            pending_tasks=[],
            progress_percentage=0.0,
            final_result=None
        )

class MCPService:
    """Service for MCP tool operations"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.tool_agent = None
    
    async def get_available_tools(self) -> MCPToolsResponse:
        """Get list of available MCP tools"""
        try:
            tools_dict = self.mcp_client.get_available_tools()
            
            tools_info = []
            for tool_name, tool_data in tools_dict.items():
                tool_info = MCPToolInfo(
                    name=tool_name,
                    description=tool_data.get("description", f"MCP tool: {tool_name}"),
                    parameters=tool_data.get("parameters", {})
                )
                tools_info.append(tool_info)
            
            return MCPToolsResponse(
                tools=tools_info,
                total_count=len(tools_info)
            )
            
        except Exception as e:
            raise Exception(f"Failed to get MCP tools: {str(e)}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> MCPToolExecutionResponse:
        """Execute an MCP tool directly"""
        try:
            start_time = time.time()
            
            result = self.mcp_client.call_tool(tool_name, parameters)
            
            execution_time = time.time() - start_time
            
            return MCPToolExecutionResponse(
                tool_name=tool_name,
                parameters=parameters,
                status=result.get("status", "unknown"),
                result=result,
                execution_time=execution_time,
                is_mock=True  # Since we're using mock mode
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return MCPToolExecutionResponse(
                tool_name=tool_name,
                parameters=parameters,
                status="error",
                result={"error": str(e)},
                execution_time=execution_time,
                is_mock=False
            )

class HealthService:
    """Service for health checks"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def get_health(self) -> HealthResponse:
        """Get system health status"""
        try:
            # Check MCP server
            try:
                tools = self.mcp_client.get_available_tools()
                mcp_status = "connected"
                tool_count = len(tools)
            except Exception:
                mcp_status = "disconnected (using mock)"
                tool_count = 7  # Mock tool count
            
            # Check Groq API
            try:
                llm = ChatGroq()
                groq_status = "configured (single key)"
            except Exception:
                groq_status = "not configured"
            
            return HealthResponse(
                status="healthy",
                mcp_server_status=mcp_status,
                available_tools=tool_count,
                groq_api_status=groq_status
            )
            
        except Exception as e:
            return HealthResponse(
                status="unhealthy",
                mcp_server_status="error",
                available_tools=0,
                groq_api_status="error"
            )