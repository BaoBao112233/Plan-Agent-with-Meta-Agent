"""
🎯 Plan Agent FastAPI Models
============================

Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class PlanType(str, Enum):
    """Plan type enumeration"""
    PRIORITY = "priority"
    PRIORITY_SECURITY = "priority_security"
    PRIORITY_CONVENIENCE = "priority_convenience"
    PRIORITY_ENERGY = "priority_energy"

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PlanStatus(str, Enum):
    """Plan status enumeration"""
    DRAFT = "draft"
    PLAN_CREATED = "plan_created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Request Models
class SmartHomeRequest(BaseModel):
    """Request for smart home automation"""
    input: str = Field(..., description="Smart home automation request", min_length=1)
    enable_api: bool = Field(default=True, description="Enable API status tracking")
    verbose: bool = Field(default=False, description="Enable verbose logging")

class PrioritySelectionRequest(BaseModel):
    """Request for priority plan selection"""
    plan_id: str = Field(..., description="Plan ID")
    selected_priority: Literal[1, 2, 3] = Field(..., description="Selected priority (1=Security, 2=Convenience, 3=Energy)")

class MCPToolRequest(BaseModel):
    """Request for direct MCP tool execution"""
    tool_name: str = Field(..., description="MCP tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

class TaskUpdateRequest(BaseModel):
    """Request for task status update"""
    task_id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="New task status")
    result: Optional[str] = Field(None, description="Task execution result")

# Response Models
class PriorityPlan(BaseModel):
    """Priority plan model"""
    priority_type: str = Field(..., description="Priority type (security/convenience/energy)")
    tasks: List[str] = Field(..., description="List of tasks")
    description: str = Field(..., description="Plan description")
    focus: str = Field(..., description="Plan focus area")

class PriorityPlansResponse(BaseModel):
    """Response with 3 priority plans"""
    plan_id: str = Field(..., description="Unique plan ID")
    input: str = Field(..., description="Original user input")
    security_plan: PriorityPlan = Field(..., description="Security priority plan")
    convenience_plan: PriorityPlan = Field(..., description="Convenience priority plan") 
    energy_plan: PriorityPlan = Field(..., description="Energy efficiency plan")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    status: PlanStatus = Field(default=PlanStatus.DRAFT, description="Plan status")

class SelectedPlanResponse(BaseModel):
    """Response after plan selection"""
    plan_id: str = Field(..., description="Plan ID")
    selected_priority: str = Field(..., description="Selected priority type")
    selected_plan: List[str] = Field(..., description="Selected plan tasks")
    status: PlanStatus = Field(..., description="Plan status")
    execution_started: bool = Field(..., description="Whether execution has started")

class TaskInfo(BaseModel):
    """Task information model"""
    task_id: str = Field(..., description="Task ID")
    task_content: str = Field(..., description="Task content")
    status: TaskStatus = Field(..., description="Task status")
    result: Optional[str] = Field(None, description="Task execution result")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class PlanExecutionResponse(BaseModel):
    """Plan execution status response"""
    plan_id: str = Field(..., description="Plan ID")
    status: PlanStatus = Field(..., description="Plan status")
    current_task: Optional[str] = Field(None, description="Currently executing task")
    completed_tasks: List[TaskInfo] = Field(default_factory=list, description="Completed tasks")
    pending_tasks: List[TaskInfo] = Field(default_factory=list, description="Pending tasks")
    progress_percentage: float = Field(..., description="Execution progress (0-100)")
    final_result: Optional[str] = Field(None, description="Final execution result")

class MCPToolInfo(BaseModel):
    """MCP tool information"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")

class MCPToolsResponse(BaseModel):
    """Response with available MCP tools"""
    tools: List[MCPToolInfo] = Field(..., description="Available MCP tools")
    total_count: int = Field(..., description="Total number of tools")

class MCPToolExecutionResponse(BaseModel):
    """Response from MCP tool execution"""
    tool_name: str = Field(..., description="Executed tool name")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters used")
    status: str = Field(..., description="Execution status")
    result: Any = Field(..., description="Tool execution result")
    execution_time: float = Field(..., description="Execution time in seconds")
    is_mock: bool = Field(default=False, description="Whether result is from mock")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    mcp_server_status: str = Field(..., description="MCP server connection status")
    available_tools: int = Field(..., description="Number of available MCP tools")
    groq_api_status: str = Field(..., description="Groq API status")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

class PlanProgressUpdate(BaseModel):
    """Plan progress update for WebSocket"""
    plan_id: str = Field(..., description="Plan ID")
    status: PlanStatus = Field(..., description="Current plan status")
    current_task: Optional[str] = Field(None, description="Currently executing task")
    progress_percentage: float = Field(..., description="Progress percentage")
    message: str = Field(..., description="Progress message")