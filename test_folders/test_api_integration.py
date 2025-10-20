#!/usr/bin/env python3
"""
Test script để kiểm tra API integration với Plan Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_client import APIClient
from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq
from dotenv import load_dotenv
from os import environ

load_dotenv()

def test_api_client():
    """Test APIClient độc lập"""
    print("🧪 Testing APIClient...")
    
    api_client = APIClient()
    
    # Test create plan
    print("\n1. Testing create_plan...")
    plan_data = {
        "input": "Test plan creation",
        "plan_type": "simple",
        "current_plan": ["Task 1: Test task", "Task 2: Another test task"],
        "status": "plan_created"
    }
    
    result = api_client.create_plan(plan_data)
    if result:
        print(f"✅ Plan created successfully: {result}")
    else:
        print("❌ Failed to create plan")
        return False
    
    # Test update plan status
    print("\n2. Testing update_plan_status...")
    result = api_client.update_plan_status("in_progress")
    if result:
        print("✅ Plan status updated successfully")
    else:
        print("❌ Failed to update plan status")
    
    # Test update task status
    print("\n3. Testing update_task_status...")
    result = api_client.update_task_status("Task 1: Test task", "completed", "Task completed successfully!")
    if result:
        print("✅ Task status updated successfully")
    else:
        print("❌ Failed to update task status")
    
    # Test get plan
    print("\n4. Testing get_plan...")
    result = api_client.get_plan()
    if result:
        print("✅ Plan retrieved successfully")
        print(f"Plan data: {result}")
    else:
        print("❌ Failed to get plan")
    
    return True

def test_plan_agent_with_api():
    """Test Plan Agent với API integration"""
    print("\n🤖 Testing Plan Agent with API integration...")
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found. Please set it in .env file.")
        return False
    
    try:
        llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
        agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)
        
        print("\nTesting với query đơn giản...")
        response = agent.invoke("Create a simple plan to make a cup of coffee")
        
        print(f"\n🎯 Final Response: {response}")
        print("✅ Plan Agent với API integration hoạt động thành công!")
        
        return True
    except Exception as e:
        print(f"❌ Error testing Plan Agent: {e}")
        return False

def main():
    print("🚀 Starting API Integration Tests\n")
    
    # Check if API server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API Server is running at http://localhost:8000")
        else:
            print("⚠️  API Server might not be running properly")
    except Exception:
        print("❌ Cannot connect to API Server at http://localhost:8000")
        print("Please make sure the API server is running before testing.")
        return
    
    print("\n" + "="*50)
    
    # Test API Client
    if test_api_client():
        print("\n" + "="*50)
        # Test Plan Agent
        test_plan_agent_with_api()
    else:
        print("❌ API Client tests failed. Skipping Plan Agent tests.")

if __name__ == "__main__":
    main()