#!/usr/bin/env python3
"""
Test script to demonstrate Langfuse integration for LangGraph workflows.

This script shows how Langfuse tracing works with callback handlers,
providing observability for LangChain/LangGraph applications.

Usage:
    LANGFUSE_SECRET_KEY=your_secret_key LANGFUSE_PUBLIC_KEY=your_public_key python test_langfuse_integration.py
"""

import os
import asyncio
from datetime import datetime
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent

async def test_langfuse_tracing():
    """Test Langfuse tracing with callback handlers"""
    
    print("🧪 Testing Langfuse Integration")
    print("=" * 50)
    
    # Check if Langfuse environment variables are set
    tracing_enabled = os.environ.get("LANGFUSE_TRACING", "true").lower() == "true"
    secret_key_set = bool(os.environ.get("LANGFUSE_SECRET_KEY"))
    public_key_set = bool(os.environ.get("LANGFUSE_PUBLIC_KEY"))
    langfuse_host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    project_name = os.environ.get("LANGFUSE_PROJECT", "public-health-dashboard")
    
    print(f"📊 Langfuse Configuration:")
    print(f"   Tracing Enabled: {tracing_enabled}")
    print(f"   Secret Key Set: {secret_key_set}")
    print(f"   Public Key Set: {public_key_set}")
    print(f"   Host: {langfuse_host}")
    print(f"   Project Name: {project_name}")
    
    if not tracing_enabled:
        print("\n⚠️  Langfuse tracing is disabled. Set LANGFUSE_TRACING=true to enable.")
        return
        
    if not secret_key_set or not public_key_set:
        print("\n⚠️  Missing Langfuse keys. Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY.")
        print("   Get your keys from: https://cloud.langfuse.com/ (or your self-hosted instance)")
        return
    
    print(f"\n✅ Langfuse is configured! Traces will be sent to project: {project_name}")
    print(f"   View traces at: {langfuse_host}")
    
    # Test the ReAct agent with tracing
    print(f"\n🚀 Running ReAct agent test with Langfuse tracing...")
    try:
        agent = PublicHealthReActAgent()
        
        # This will be traced in Langfuse via callback handlers
        result = await agent.generate_dashboard(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        print(f"\n📊 Dashboard generation completed:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Tools Used: {result.get('tools_used', [])}")
        print(f"   Agent Type: {result.get('agent_type', 'unknown')}")
        
        if result.get('success'):
            print(f"\n✅ Check Langfuse project '{project_name}' for detailed traces!")
            print(f"   🔗 {langfuse_host}/project/{project_name}")
            print("   📊 Traces include: LLM calls, tool executions, and workflow steps")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("   Note: This is normal if MCP server is not running or API keys are missing.")

if __name__ == "__main__":
    asyncio.run(test_langfuse_tracing()) 