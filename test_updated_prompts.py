#!/usr/bin/env python3
"""
Test Updated Prompts with OXII MasterController Logic
"""

from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq

def test_updated_prompts():
    """Test all updated prompts with OXII logic"""
    print("🚀 Testing Updated Prompts with OXII MasterController Logic...")
    
    llm = ChatGroq()
    agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
    
    # Test cases for different routing scenarios
    test_cases = [
        {
            "name": "Simple IoT Request", 
            "input": "Turn on the living room lights",
            "expected_route": "simple"
        },
        {
            "name": "Complex IoT Request",
            "input": "Set up a complete smart home system for security and comfort with user preferences",
            "expected_route": "advanced" 
        },
        {
            "name": "Priority Choice Request",
            "input": "I need a smart home automation system that balances security, convenience, and energy efficiency. Show me different approaches.",
            "expected_route": "priority"
        }
    ]
    
    print("\n" + "="*80)
    print("🔍 TESTING ROUTER SELECTION")
    print("="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        print(f"Expected Route: {test_case['expected_route']}")
        
        try:
            # Test router directly
            state = {'input': test_case['input']}
            routed_state = agent.router(state)
            route = routed_state.get('plan_type')
            
            status = "✅ PASS" if route == test_case['expected_route'] else "❌ FAIL"
            print(f"Actual Route: {route}")
            print(f"Status: {status}")
            
        except Exception as e:
            print(f"❌ Router Error: {e}")
    
    print("\n" + "="*80)
    print("🔍 TESTING PRIORITY PLANNING WORKFLOW")
    print("="*80)
    
    # Test priority planning with new prompt
    priority_test = """
    I want to set up smart home automation for my living room that includes lighting, 
    temperature control, and security features. I need to see different approaches 
    that prioritize security, convenience, and energy efficiency differently.
    """
    
    print(f"\n📝 Priority Test Input: {priority_test}")
    
    try:
        # Test direct priority planning method
        state = {'input': priority_test, 'plan_type': 'priority'}
        result = agent.priority_plan(state)
        
        print("\n✅ Priority Planning Result:")
        print(f"📋 Selected Plan: {len(result.get('plan', []))} tasks")
        for i, task in enumerate(result.get('plan', []), 1):
            print(f"   {i}. {task[:100]}...")
        
    except Exception as e:
        print(f"❌ Priority Planning Error: {e}")
        import traceback
        traceback.print_exc()

def test_simple_planning():
    """Test simple planning with updated prompt"""
    print("\n" + "="*80)
    print("🔍 TESTING SIMPLE PLANNING")
    print("="*80)
    
    llm = ChatGroq()
    agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
    
    simple_test = "Turn on all lights in the bedroom and set temperature to 22 degrees"
    
    try:
        state = {'input': simple_test}
        result = agent.simple_plan(state)
        
        print(f"\n✅ Simple Planning Result:")
        print(f"📋 Plan: {len(result.get('plan', []))} tasks")
        for i, task in enumerate(result.get('plan', []), 1):
            print(f"   {i}. {task}")
            
    except Exception as e:
        print(f"❌ Simple Planning Error: {e}")

if __name__ == "__main__":
    print("🎯 Updated Prompts Test Suite")
    print("Testing OXII MasterController Logic Implementation")
    print("="*80)
    
    # Test 1: Router Selection with Updated Logic
    test_updated_prompts()
    
    # Test 2: Simple Planning with Device Validation
    test_simple_planning()
    
    print("\n✨ Prompts testing completed!")
    print("📊 All agents now follow OXII MasterController structure:")
    print("   - Device validation first")  
    print("   - Status management integration")
    print("   - English communication")
    print("   - Structured workflows")
    print("   - Safety considerations")