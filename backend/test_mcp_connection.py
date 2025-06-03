#!/usr/bin/env python3
"""
Test script to diagnose MCP connection issues
"""

import asyncio
import sys
import os

# Add necessary paths for imports
sys.path.insert(0, 'mcp')
sys.path.insert(0, 'app')

async def test_mcp_connection():
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        print("🔍 Testing MCP connection...")
        
        client_config = {
            'public-health-fastmcp': {
                'url': 'http://localhost:8000/sse',
                'transport': 'sse',
            }
        }
        
        print("📡 Creating MCP client...")
        client = MultiServerMCPClient(client_config)
        print('✅ MCP client created')
        
        print("🔧 Getting available tools...")
        tools = await client.get_tools()
        print(f'✅ Got {len(tools)} tools:')
        for tool in tools:
            print(f'   - {tool.name}: {tool.description[:50]}...')
        
        if tools:
            print(f"\n🧪 Testing first tool: {tools[0].name}")
            result = await tools[0].ainvoke({"limit": 3})
            print(f'✅ Tool test successful: {type(result)}')
        
        await client.close()
        print('✅ Connection test successful!')
        
    except Exception as e:
        print(f'❌ Connection test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 