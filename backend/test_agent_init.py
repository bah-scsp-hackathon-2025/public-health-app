#!/usr/bin/env python3
"""
Test script to check agent initialization
"""

import asyncio
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

async def test_agent_init():
    from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
    
    try:
        print("Testing agent initialization...")
        
        agent = PublicHealthDashboardAgent()
        print(f'✅ Agent initialized')
        print(f'LLM configured: {agent.llm is not None}')
        print(f'LLM type: {type(agent.llm).__name__ if agent.llm else "None"}')
        print(f'MCP Host: {agent.mcp_host}')
        print(f'MCP Port: {agent.mcp_port}')
        
        return True
    except Exception as e:
        print(f'❌ Agent initialization failed: {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_agent_init()) 