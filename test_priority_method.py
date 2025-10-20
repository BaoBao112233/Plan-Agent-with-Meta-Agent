#!/usr/bin/env python3
"""
Test trực tiếp priority_plan method
"""

from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq

def test_priority_plan_method():
    """Test directly the priority_plan method"""
    print("🎯 Testing Priority Plan Method Directly...")
    
    llm = ChatGroq()
    agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
    
    # Mock state
    state = {
        'input': '''I want to create a smart home automation system that controls lighting, 
        temperature, and security cameras. The system should prioritize security, convenience, 
        and energy efficiency. Please create multiple plan options.''',
        'plan_type': 'priority'
    }
    
    print(f"📝 Input: {state['input']}")
    print("\n" + "="*60)
    
    try:
        # Call LLM directly first to see raw response
        from src.message import SystemMessage, HumanMessage
        from src.agent.plan.utils import read_markdown_file
        
        system_prompt = read_markdown_file('./src/agent/plan/prompt/priority_plan.md')
        llm_response = llm.invoke([SystemMessage(system_prompt), HumanMessage(state['input'])])
        
        print(f"\n📄 Raw LLM Response:")
        print("-" * 60)
        print(llm_response.content)
        print("-" * 60)
        
        # Now try extract_plan
        from src.agent.plan.utils import extract_plan
        plan_data = extract_plan(llm_response.content)
        print(f"\n🔍 Extracted Plan Data: {plan_data}")
        
        # Call priority_plan method
        result = agent.priority_plan(state)
        
        print("\n" + "="*60)
        print(f"✅ Priority Plan Result:")
        print(f"📋 Selected Plan: {result.get('plan', [])}")
        
    except Exception as e:
        print(f"❌ Error in priority_plan method: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_priority_plan_method()