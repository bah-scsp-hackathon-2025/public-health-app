#!/usr/bin/env python3
"""
Test script to check agent integration with MCP server
"""

import sys
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('../.env')  # Load from parent directory
except ImportError:
    print("Warning: python-dotenv not installed")

# Add necessary paths for imports
sys.path.insert(0, '.')
sys.path.insert(0, 'mcp')

async def test_agent_with_mcp():
    """Test agent with real MCP server"""
    from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
    
    print("🧪 Testing Agent with MCP Server")
    print("=" * 50)
    
    try:
        print("1. Creating agent...")
        agent = PublicHealthDashboardAgent()
        print(f"   ✅ Agent created with LLM: {agent.llm is not None}")
        
        print("\n2. Testing dashboard generation...")
        result = await agent.generate_dashboard(
            "Generate comprehensive public health dashboard"
        )
        
        print(f"   ✅ Dashboard generated successfully")
        print(f"   📊 Alerts: {result.get('alerts_count', 0)}")
        print(f"   📈 Trends: {result.get('trends_count', 0)}")
        print(f"   ⚡ Success: {result.get('success', False)}")
        
        if result.get('dashboard_summary'):
            print(f"\n📄 Summary preview:")
            summary = result['dashboard_summary']
            print(summary[:200] + "..." if len(summary) > 200 else summary)
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent_with_mcp()) 