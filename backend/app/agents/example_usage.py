#!/usr/bin/env python3
"""
Example usage of the Public Health Dashboard Agent

This script demonstrates how to use the LangGraph dashboard agent
from its new location in backend/app/agents.
"""

import asyncio
import sys
import os

# Add the necessary paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'mcp'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from health_dashboard_agent import PublicHealthDashboardAgent


async def main():
    """Example usage of the dashboard agent"""
    print("🏥 Public Health Dashboard Agent Example")
    print("=" * 50)
    
    # Create the agent
    print("📝 Initializing agent...")
    agent = PublicHealthDashboardAgent()
    
    print("💡 Note: Make sure the FastMCP server is running:")
    print("   cd ../../mcp")
    print("   python3 -m uvicorn mcp_public_health:app --host 0.0.0.0 --port 8000")
    print()
    
    try:
        # Generate a dashboard
        print("🔄 Generating dashboard...")
        result = await agent.generate_dashboard(
            "Generate a comprehensive public health dashboard with current alerts and trends"
        )
        
        if result.get('success'):
            print("✅ Dashboard generated successfully!")
            print("\n" + "="*60)
            print(result['dashboard_summary'])
            print("="*60)
            print(f"\n📊 Statistics:")
            print(f"   • Alerts processed: {result.get('alerts_count', 'N/A')}")
            print(f"   • Trends analyzed: {result.get('trends_count', 'N/A')}")
            print(f"   • Generated at: {result.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        print("\n💡 Common issues:")
        print("   • FastMCP server not running")
        print("   • Network connectivity issues")
        print("   • Environment variables not set")


if __name__ == "__main__":
    asyncio.run(main()) 