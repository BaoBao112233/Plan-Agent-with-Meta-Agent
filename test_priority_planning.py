#!/usr/bin/env python3
"""
Test Priority Planning Feature
Kiểm tra tính năng lập kế hoạch ưu tiên mới của Plan Agent
"""

from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq

def test_priority_planning():
    """Test the new priority planning feature"""
    print("🚀 Testing Priority Planning Feature...")
    
    # Khởi tạo PlanAgent với priority planning
    llm = ChatGroq()
    agent = PlanAgent(
        llm=llm,
        verbose=True,
        api_enabled=False  # Tắt API để test local
    )
    
    # Test case: IoT smart home automation
    test_input = """
    I want to create a smart home automation system that controls lighting, temperature, 
    and security cameras. The system should be accessible via mobile app and web interface.
    Please help me plan the implementation.
    """
    
    print(f"\n📝 Test Input: {test_input}")
    print("\n" + "="*60)
    
    try:
        # Invoke the agent - nó sẽ tự chọn route priority nếu phù hợp
        result = agent.invoke(test_input)
        
        print("\n" + "="*60)
        print(f"✅ Priority Planning Result:")
        print(f"📋 Final Plan: {result}")
        
    except Exception as e:
        print(f"❌ Error during priority planning: {e}")
        import traceback
        traceback.print_exc()

def test_router_selection():
    """Test if router correctly selects priority route"""
    print("\n🔄 Testing Router Selection...")
    
    llm = ChatGroq()
    agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
    
    # Test router directly
    test_cases = [
        "Create a simple file backup script",  # Should be simple
        "Design a complex IoT system with multiple priorities",  # Should be priority
        "Set up a web server with user authentication and database"  # Could be priority
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case}")
        
        try:
            state = {'input': test_case}
            routed_state = agent.router(state)
            route = routed_state.get('plan_type')
            print(f"   ➡️  Selected Route: {route}")
            
        except Exception as e:
            print(f"   ❌ Router Error: {e}")

if __name__ == "__main__":
    print("🎯 Priority Planning Test Suite")
    print("="*50)
    
    # Test 1: Router Selection
    test_router_selection()
    
    # Test 2: Full Priority Planning Flow
    print("\n" + "="*50)
    test_priority_planning()
    
    print("\n✨ Test completed!")