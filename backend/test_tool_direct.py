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
        
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Find the fetch_epi_signal tool
        fetch_tool = None
        for tool in tools:
            if tool.name == 'fetch_epi_signal':
                fetch_tool = tool
                break
        
        if fetch_tool:
            print('🧪 Testing fetch_epi_signal...')
            result = await fetch_tool.ainvoke({
                'signal': 'smoothed_wcli',
                'time_type': 'day',
                'geo_type': 'state',
                'start_time': '20231201',
                'end_time': '20231231'
            })
            print(f'✅ Tool success: {type(result)}')
            print(f'Result preview: {str(result)[:500]}...')
        else:
            print('❌ fetch_epi_signal tool not found')
            
        # Test server info tool
        info_tool = None
        for tool in tools:
            if tool.name == 'get_server_info':
                info_tool = tool
                break
        
        if info_tool:
            print('\n🧪 Testing get_server_info...')
            result = await info_tool.ainvoke({})
            print(f'✅ Server info success: {type(result)}')
            print(f'Server info: {str(result)[:300]}...')
        else:
            print('❌ get_server_info tool not found')
        
    except Exception as e:
        print(f'❌ Tool test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool()) 