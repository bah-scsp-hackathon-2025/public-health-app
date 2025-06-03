#!/usr/bin/env python3
"""
Test script to check agent initialization
"""

import asyncio
import sys
import os

# Add necessary paths for imports
sys.path.insert(0, '.')
sys.path.insert(0, 'mcp')

async def test_agent_init():
    from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
    
    print('🧪 Testing agent initialization...')
    agent = PublicHealthDashboardAgent(llm_provider='auto')
    print(f'LLM Provider: {agent.llm_provider}')
    print(f'LLM Object: {type(agent.llm)}')
    print(f'Has LLM: {agent.llm is not None}')
    
    if agent.llm:
        print('✅ Agent has LLM - should work with full analysis')
    else:
        print('⚠️ Agent has no LLM - will use basic mode')

if __name__ == "__main__":
    asyncio.run(test_agent_init()) 