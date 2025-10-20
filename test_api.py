"""
🧪 API Test Client
=================

Test client to demonstrate API functionality
"""

import asyncio
import httpx
import json
from typing import Dict, Any

class PlanAgentAPIClient:
    """Client for testing the Plan Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_plans(self, user_input: str, enable_api: bool = True, verbose: bool = False) -> Dict[str, Any]:
        """Create priority plans"""
        payload = {
            "user_input": user_input,
            "enable_api": enable_api,
            "verbose": verbose
        }
        
        response = await self.client.post(f"{self.base_url}/plans/create", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def select_plan(self, plan_id: str, priority: int) -> Dict[str, Any]:
        """Select a priority plan"""
        payload = {"selected_priority": priority}
        
        response = await self.client.post(f"{self.base_url}/plans/{plan_id}/select", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute the selected plan"""
        response = await self.client.post(f"{self.base_url}/plans/{plan_id}/execute")
        response.raise_for_status()
        return response.json()
    
    async def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get plan status"""
        response = await self.client.get(f"{self.base_url}/plans/{plan_id}/status")
        response.raise_for_status()
        return response.json()
    
    async def get_mcp_tools(self) -> Dict[str, Any]:
        """Get available MCP tools"""
        response = await self.client.get(f"{self.base_url}/mcp/tools")
        response.raise_for_status()
        return response.json()
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool"""
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        response = await self.client.post(f"{self.base_url}/mcp/tools/execute", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def test_full_workflow():
    """Test the complete API workflow"""
    client = PlanAgentAPIClient()
    
    try:
        print("🧪 Testing Plan Agent API")
        print("=" * 50)
        
        # 1. Health check
        print("1️⃣ Checking system health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   MCP Server: {health['mcp_server_status']}")
        print(f"   Available Tools: {health['available_tools']}")
        
        # 2. Get MCP tools
        print("\n2️⃣ Getting available MCP tools...")
        tools = await client.get_mcp_tools()
        print(f"   Found {tools['total_count']} tools:")
        for tool in tools['tools'][:3]:  # Show first 3
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 3. Create plans
        print("\n3️⃣ Creating priority plans...")
        user_input = "I want to secure my home and make it energy efficient"
        plans = await client.create_plans(user_input, enable_api=True, verbose=False)
        plan_id = plans['plan_id']
        print(f"   Plan ID: {plan_id}")
        print(f"   Security Plan: {len(plans['security_plan']['tasks'])} tasks")
        print(f"   Convenience Plan: {len(plans['convenience_plan']['tasks'])} tasks")
        print(f"   Energy Plan: {len(plans['energy_plan']['tasks'])} tasks")
        
        # 4. Select security plan
        print("\n4️⃣ Selecting security plan (priority 1)...")
        selection = await client.select_plan(plan_id, 1)
        print(f"   Selected: {selection['selected_priority']}")
        print(f"   Status: {selection['status']}")
        print(f"   Tasks: {len(selection['selected_plan'])}")
        
        # 5. Execute plan
        print("\n5️⃣ Executing plan...")
        execution = await client.execute_plan(plan_id)
        print(f"   Status: {execution['status']}")
        print(f"   Progress: {execution['progress_percentage']}%")
        print(f"   Completed tasks: {len(execution['completed_tasks'])}")
        print(f"   Result: {execution['final_result']}")
        
        # 6. Test direct MCP tool execution
        print("\n6️⃣ Testing direct MCP tool execution...")
        tool_result = await client.execute_mcp_tool("get_device_list", {"token": "test_token"})
        print(f"   Tool: {tool_result['tool_name']}")
        print(f"   Status: {tool_result['status']}")
        print(f"   Execution time: {tool_result['execution_time']:.3f}s")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_full_workflow())