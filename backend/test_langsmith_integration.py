#!/usr/bin/env python3
"""
Test script to demonstrate LangSmith integration for LangGraph workflows.

This script shows how LangSmith tracing works with just environment variables,
without needing explicit langsmith imports.

Usage:
    LANGSMITH_API_KEY=your_key LANGCHAIN_TRACING_V2=true python test_langsmith_integration.py
"""

import os
import asyncio
from datetime import datetime
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent

async def test_langsmith_tracing():
    """Test LangSmith tracing with environment variables"""
    
    print("🧪 Testing LangSmith Integration")
    print("=" * 50)
    
    # Check if LangSmith environment variables are set
    tracing_enabled = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    api_key_set = bool(os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY"))
    project_name = os.environ.get("LANGCHAIN_PROJECT", "public-health-dashboard")
    
    print(f"📊 LangSmith Configuration:")
    print(f"   Tracing Enabled: {tracing_enabled}")
    print(f"   API Key Set: {api_key_set}")
    print(f"   Project Name: {project_name}")
    
    if not tracing_enabled:
        print("\n⚠️  LangSmith tracing is disabled. Set LANGCHAIN_TRACING_V2=true to enable.")
        print("   Also set LANGSMITH_API_KEY or LANGCHAIN_API_KEY to your LangSmith API key.")
        return
        
    if not api_key_set:
        print("\n⚠️  No LangSmith API key found. Set LANGSMITH_API_KEY or LANGCHAIN_API_KEY.")
        return
    
    print(f"\n✅ LangSmith is configured! Traces will be sent to project: {project_name}")
    print("   View traces at: https://smith.langchain.com/")
    
    # Test the ReAct agent with tracing
    print(f"\n🚀 Running ReAct agent test with LangSmith tracing...")
    try:
        agent = PublicHealthReActAgent()
        
        # This will be traced in LangSmith
        result = await agent.generate_dashboard(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        print(f"\n📊 Dashboard generation completed:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Tools Used: {result.get('tools_used', [])}")
        print(f"   Agent Type: {result.get('agent_type', 'unknown')}")
        
        if result.get('success'):
            print(f"\n✅ Check LangSmith project '{project_name}' for detailed traces!")
            print(f"   🔗 https://smith.langchain.com/o/default/projects/p/{project_name.replace(' ', '%20')}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("   Note: This is normal if MCP server is not running or API keys are missing.")

if __name__ == "__main__":
    asyncio.run(test_langsmith_tracing()) 