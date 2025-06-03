#!/usr/bin/env python3
"""
Test script to test MCP tools directly
"""

import asyncio
import sys
import os

# Add necessary paths for imports
sys.path.insert(0, 'mcp')
sys.path.insert(0, 'app')

async def test_tool():
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        client_config = {
            'public-health-fastmcp': {
                'url': 'http://localhost:8000/sse',
                'transport': 'sse',
            }
        }
        
        client = MultiServerMCPClient(client_config)
        tools = await client.get_tools()
        
        # Find the alerts tool
        alerts_tool = None
        for tool in tools:
            if tool.name == 'get_public_health_alerts':
                alerts_tool = tool
                break
        
        if alerts_tool:
            print('🧪 Testing with agent parameters...')
            result = await alerts_tool.ainvoke({
                'limit': 20,
                'start_date': '2025-05-03T22:13:24.174018'
            })
            print(f'✅ Tool success: {type(result)}')
            print(f'Result preview: {str(result)[:500]}...')
        else:
            print('❌ Tool not found')
        
    except Exception as e:
        print(f'❌ Tool test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool()) 