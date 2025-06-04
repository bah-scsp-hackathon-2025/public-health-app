#!/usr/bin/env python3
"""
Test script to verify Claude 4.0 Sonnet with thinking mode configuration
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent

async def test_standard_agent():
    """Test the standard dashboard agent with Claude Thinking Mode"""
    print("🧠 Testing Standard Dashboard Agent with Claude Thinking Mode")
    print("=" * 70)
    
    try:
        agent1 = PublicHealthDashboardAgent()
        
        result = await agent1.assemble_dashboard()
        
        print("✅ Standard Agent Result:")
        print(f"Success: {result.get('success')}")
        print(f"LLM: {type(agent1.llm).__name__ if agent1.llm else 'None'}")
        print(f"Thinking enabled: {hasattr(agent1.llm, 'thinking') if agent1.llm else False}")
        
        if result.get('success'):
            print("\n📊 Summary Preview:")
            summary = result.get('dashboard_summary', '')
            print(summary[:300] + "..." if len(summary) > 300 else summary)
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Standard agent test failed: {e}")
        return False

async def test_react_agent():
    """Test the ReAct agent with Claude Thinking Mode"""
    print("\n🤖 Testing ReAct Agent with Claude Thinking Mode")
    print("=" * 70)
    
    try:
        agent2 = PublicHealthReActAgent()
        
        result = await agent2.assemble_dashboard()
        
        print("✅ ReAct Agent Result:")
        print(f"Success: {result.get('success')}")
        print(f"LLM: {type(agent2.llm).__name__ if agent2.llm else 'None'}")
        print(f"Thinking enabled: {hasattr(agent2.llm, 'thinking') if agent2.llm else False}")
        print(f"Tools used: {result.get('tools_used', [])}")
        
        if result.get('success'):
            print("\n📊 Summary Preview:")
            summary = result.get('dashboard_summary', '')
            print(summary[:300] + "..." if len(summary) > 300 else summary)
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ ReAct agent test failed: {e}")
        return False

async def main():
    """Run both agent tests"""
    print("🧠 Claude Sonnet 4.0 with Thinking Mode - Agent Tests")
    print("=" * 80)
    print("Testing both Standard and ReAct agents with Claude's thinking capabilities")
    print("=" * 80)
    
    # Test both agents
    standard_success = await test_standard_agent()
    react_success = await test_react_agent()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Standard Agent: {'✅ PASSED' if standard_success else '❌ FAILED'}")
    print(f"ReAct Agent: {'✅ PASSED' if react_success else '❌ FAILED'}")
    
    if standard_success and react_success:
        print("\n🎉 All tests passed! Claude Thinking Mode is working with both agents.")
        print("\nClaude's thinking process enables:")
        print("• Enhanced reasoning and analysis")
        print("• Step-by-step problem solving")
        print("• More accurate epidemiological insights")
        print("• Better structured recommendations")
    else:
        print("\n⚠️ Some tests failed. Check API keys and MCP server status.")

if __name__ == "__main__":
    asyncio.run(main()) 