#!/usr/bin/env python3
"""
Full workflow test cho priority planning
"""

from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq

def test_full_priority_workflow():
    """Test complete priority planning workflow"""
    print("🚀 Testing Full Priority Planning Workflow...")
    
    llm = ChatGroq()
    agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
    
    # Test case với query trigger priority
    test_input = """
    I need to set up a comprehensive smart home system that controls lighting, temperature, 
    HVAC, security cameras, door locks, and window sensors. The system should balance 
    security requirements, user convenience, and energy efficiency. I want to see different 
    approaches and choose the best one for my needs.
    """
    
    print(f"📝 Test Input: {test_input}")
    print("\n" + "="*80)
    
    try:
        # This should trigger the router to select 'priority' route
        result = agent.invoke(test_input)
        
        print("\n" + "="*80)
        print(f"✅ Full Workflow Result:")
        print(f"📋 Final Output: {result}")
        
    except Exception as e:
        print(f"❌ Error in full workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_priority_workflow()