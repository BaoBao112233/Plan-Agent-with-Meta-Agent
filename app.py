#!/usr/bin/env python3
"""
🎯 Plan Agent with OXII MasterController Logic
===========================================

Main application for IoT smart home automation using Plan Agent with:
- Device validation first approach
- 3-tier priority planning (Security/Convenience/Energy)
- Status management and API integration
- MCP tools integration for device control
- Dual API key failover protection

Usage:
    python app.py
"""

import sys
import time
from datetime import datetime
from typing import Optional

def display_banner():
    """Display application banner"""
    print("🎯 OXII MasterController - Plan Agent System")
    print("=" * 55)
    print("🏠 IoT Smart Home Automation with Priority Planning")
    print("🔧 Device Validation → Planning → Execution → Status")
    print("⚡ Dual API Key Protection & MCP Tools Integration")
    print("=" * 55)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def test_priority_planning():
    """Test Priority Planning workflow with 3-tier choice architecture using MCP tools only"""
    print("🎯 Testing MCP-Based Priority Planning (3-Tier Choice Architecture)")
    print("=" * 70)
    
    try:
        from src.agent.plan import PlanAgent
        from src.inference.groq import ChatGroq
        
        # Initialize with enhanced error handling
        llm = ChatGroq()
        agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
        
        print("� MCP-Only Priority Planning Features:")
        print("   ✅ Security Priority Plans (Maximum safety via MCP tools)")
        print("   ✅ Convenience Priority Plans (User experience via MCP automation)")  
        print("   ✅ Energy Efficiency Plans (Resource optimization via MCP scheduling)")
        print("   ✅ MCP device validation in all plans (get_device_list first)")
        print("   ✅ User selection before execution")
        print("   ✅ NO custom tools - MCP tools only")
        print()
        
        # Example queries for MCP-based priority planning
        example_queries = [
            "MCP-based request: Use MCP tools to turn on living room lights with security priority",
            "Smart home automation: Create MCP-based evening routine with convenience focus",
            "Energy efficient control: Use MCP tools to optimize bedroom climate with minimal power"
        ]
        
        print("📝 MCP-Based Example Queries:")
        for i, query in enumerate(example_queries, 1):
            print(f"   {i}. {query}")
        print()
        
        # Get user input
        while True:
            user_input = input("Enter your MCP smart home request (or 'examples' to see examples, 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'examples':
                for i, query in enumerate(example_queries, 1):
                    print(f"{i}. {query}")
                continue
            elif not user_input:
                print("⚠️  Please enter a request.")
                continue
            
            try:
                print(f"\n🚀 Processing with MCP Tools: {user_input}")
                print("-" * 70)
                
                start_time = time.time()
                result = agent.invoke(user_input)
                elapsed = time.time() - start_time
                
                print(f"\n✅ MCP-Based Planning completed in {elapsed:.1f}s")
                print("📋 Final MCP Result:")
                print("-" * 40)
                print(result)
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n⚠️  Process interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("💡 Tip: Try a simpler MCP-based request or check your internet connection")
            
            print("\n" + "=" * 70)
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Setup Error: {e}")

def test_mcp_integration():
    """Test MCP Tool Agent for direct device control"""
    print("🔧 Testing MCP Tool Integration")
    print("=" * 60)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        agent = MCPToolAgent(llm=llm, verbose=True)
        
        print("🔌 MCP Tools Features:")
        print("   ✅ Direct device control commands")
        print("   ✅ Smart home device management") 
        print("   ✅ Room-based controls")
        print("   ✅ Scheduling and automation")
        print()
        
        # Example MCP commands
        example_commands = [
            "list tools - Show all available MCP tools",
            "get device list - Show all connected devices",
            "control air conditioner in bedroom",
            "turn on all lights in living room",
            "create schedule for morning routine"
        ]
        
        print("📝 Example MCP Commands:")
        for i, cmd in enumerate(example_commands, 1):
            print(f"   {i}. {cmd}")
        print()
        
        while True:
            user_input = input("Enter MCP command (or 'examples' to see examples, 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'examples':
                for i, cmd in enumerate(example_commands, 1):
                    print(f"{i}. {cmd}")
                continue
            elif not user_input:
                print("⚠️  Please enter a command.")
                continue
            
            try:
                print(f"\n🔧 Executing: {user_input}")
                print("-" * 50)
                
                start_time = time.time()
                result = agent.invoke(user_input)
                elapsed = time.time() - start_time
                
                route = result.get('route', 'unknown')
                output = result.get('output', 'No output')
                
                print(f"\n✅ Completed in {elapsed:.1f}s")
                print(f"📍 Route: {route}")
                print("📋 Output:")
                print("-" * 30)
                print(output)
                print("-" * 30)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
            print()
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Setup Error: {e}")

def test_full_workflow():
    """Test complete workflow: Planning → MCP Execution → Status Updates"""
    print("🚀 Testing Full OXII Workflow")
    print("=" * 60)
    
    try:
        from src.agent.plan import PlanAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        # Enable API for status updates in full workflow
        agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)
        
        print("� Full Workflow Features:")
        print("   ✅ Device validation before planning")
        print("   ✅ Priority-based plan generation")
        print("   ✅ User selection and confirmation")
        print("   ✅ MCP tool execution via Meta Agent")
        print("   ✅ Task status updates (RUNNING → DONE/FAILED)")
        print("   ✅ Plan status management")
        print("   ✅ API integration for monitoring")
        print()
        
        workflow_examples = [
            "Set up evening security mode for the house",
            "Create energy-efficient automation for bedroom",
            "Configure morning routine with lights and temperature"
        ]
        
        print("📝 Workflow Examples:")
        for i, example in enumerate(workflow_examples, 1):
            print(f"   {i}. {example}")
        print()
        
        user_input = input("Enter your smart home automation request: ").strip()
        
        if not user_input:
            print("⚠️  Using default example...")
            user_input = workflow_examples[0]
        
        try:
            print(f"\n🚀 Starting Full Workflow: {user_input}")
            print("=" * 60)
            print("📋 This will demonstrate:")
            print("   1. Device validation")
            print("   2. Priority plan generation (3 options)")
            print("   3. User selection")
            print("   4. Plan execution with status updates")
            print("   5. Final status reporting")
            print("-" * 60)
            
            start_time = time.time()
            result = agent.invoke(user_input)
            elapsed = time.time() - start_time
            
            print(f"\n✅ Workflow completed in {elapsed:.1f}s")
            print("📋 Final Workflow Result:")
            print("=" * 60)
            print(result)
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Workflow Error: {e}")
            print("💡 This might be due to API connectivity or rate limits")
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Setup Error: {e}")

def show_help():
    """Show application help and features"""
    print("📖 OXII MasterController - Help & Features")
    print("=" * 60)
    print()
    print("🎯 CORE FEATURES:")
    print("   1. Priority Planning - 3-tier choice architecture")
    print("      • Security Priority (Maximum safety)")
    print("      • Convenience Priority (User experience)")
    print("      • Energy Efficiency Priority (Resource optimization)")
    print()
    print("   2. Device Validation - Always verify before action")
    print("      • Check device availability")
    print("      • Validate safety parameters")
    print("      • Ensure compatibility")
    print()
    print("   3. Status Management - Track all operations")
    print("      • Task status: PENDING → RUNNING → DONE/FAILED")
    print("      • Plan status: DRAFT → RUNNING → DONE/FAILED")
    print("      • API integration for monitoring")
    print()
    print("   4. MCP Integration - Direct device control")
    print("      • Smart home device management")
    print("      • Room-based controls")
    print("      • Scheduling and automation")
    print()
    print("🔧 WORKFLOW MODES:")
    print("   • Simple Planning: Direct, straightforward requests")
    print("   • Advanced Planning: Interactive with user preferences")
    print("   • Priority Planning: 3-option choice architecture")
    print()
    print("⚡ RELIABILITY FEATURES:")
    print("   • Dual API key failover protection")
    print("   • Rate limit handling")
    print("   • Error recovery and retry logic")
    print("   • English communication throughout")
    print()

def main():
    """Main application entry point with MCP-Only OXII MasterController logic"""
    display_banner()
    
    while True:
        print("🎯 Select Mode (MCP Tools Only):")
        print("   1. MCP Priority Planning (Only Available Mode)")
        print("   2. MCP Tool Integration (Direct Access)")
        print("   3. Full MCP Workflow (Complete Pipeline)")
        print("   4. Help & Features")
        print("   5. Exit")
        print()
        print("📌 Note: This system uses ONLY MCP Smart Home Tools")
        print("   - No custom tools created")
        print("   - All device operations via MCP")
        print("   - get_device_list validates devices first")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            test_priority_planning()
        elif choice == "2":
            test_mcp_integration()
        elif choice == "3":
            test_full_workflow()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("\n👋 Thank you for using MCP-Only OXII MasterController!")
            print("🏠 Your smart home automation system is ready with MCP tools.")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please select 1-5.")
        
        print("\n" + "=" * 60)
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        print("💡 Please check your configuration and try again.")
        sys.exit(1)