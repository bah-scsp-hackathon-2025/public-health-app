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
    from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
    
    print('🧪 Testing agent with MCP server integration...')
    agent = PublicHealthDashboardAgent(llm_provider='auto')
    print(f'Agent initialized with LLM: {agent.llm is not None}')
    
    # Test dashboard generation
    print('\n📊 Testing dashboard generation...')
    try:
        result = await agent.generate_dashboard('Generate dashboard focusing on California health data')
        print('✅ Dashboard generation completed successfully!')
        print(f'Result type: {type(result)}')
        
        if isinstance(result, dict):
            if 'dashboard_summary' in result:
                print(f'Dashboard summary preview: {result["dashboard_summary"][:300]}...')
            if 'analysis_result' in result and result['analysis_result']:
                print(f'Analysis insights: {len(result["analysis_result"].get("insights", []))} insights found')
            if 'alerts_data' in result and result['alerts_data']:
                print(f'Alerts data: {result["alerts_data"]["total_alerts"]} alerts processed')
            if 'trends_data' in result and result['trends_data']:
                print(f'Trends data: {result["trends_data"]["metadata"]["total_trend_types"]} trend types processed')
        else:
            print(f'Result: {str(result)[:300]}...')
    except Exception as e:
        print(f'❌ Error during dashboard generation: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent_with_mcp()) 