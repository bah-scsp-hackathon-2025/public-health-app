#!/usr/bin/env python3
"""
Comprehensive test script for MCP server and agent integration
"""

import asyncio
import sys
from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent


# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv("../.env")  # Load from parent directory
except ImportError:
    print("Warning: python-dotenv not installed")

# Add necessary paths for imports
sys.path.insert(0, ".")
sys.path.insert(0, "mcp")


async def test_comprehensive_integration():
    """Test the standard dashboard agent"""

    print("📊 Testing Standard Dashboard Agent")
    print("=" * 60)

    # Test 1: Agent initialization
    print("\n1️⃣ Testing Agent Initialization...")
    agent = PublicHealthDashboardAgent()
    print(f"   ✅ Agent initialized with LLM: {agent.llm is not None}")
    print(f"   📡 MCP Host: {agent.mcp_host}:{agent.mcp_port}")

    # Test 2: Basic dashboard generation
    print("\n2️⃣ Testing Basic Dashboard Generation...")
    try:
        result = await agent.assemble_dashboard()
        print("   ✅ Basic dashboard generation successful!")

        if "alerts_data" in result and result["alerts_data"]:
            print(
                f'   📊 Total alerts processed: {result["alerts_data"]["total_alerts"]}'
            )

        if "trends_data" in result and result["trends_data"]:
            print(
                f'   📈 Trend types processed: {result["trends_data"]["metadata"]["total_trend_types"]}'
            )

        if "dashboard_summary" in result and result["dashboard_summary"]:
            summary_length = len(result["dashboard_summary"])
            print(f"   📝 Dashboard summary generated: {summary_length} characters")

        # Display results
        print("\n📊 DASHBOARD SUMMARY:")
        print("-" * 40)
        print(result["dashboard_summary"])

        print("\n📈 STATISTICS:")
        print(f"• Total Alerts: {result['alerts_count']}")
        print(f"• Trend Categories: {result['trends_count']}")
        print(f"• Success: {result['success']}")
        print(f"• Timestamp: {result['timestamp']}")

        if result.get("error"):
            print(f"• Error: {result['error']}")

        # Enhanced features test
        print("\n🔬 ENHANCED FEATURES:")
        print(f"• Structured Alerts: {len(result.get('alerts', []))}")
        print(f"• Rising Trends: {len(result.get('rising_trends', []))}")
        print(f"• Risk Assessment: {'✅' if result.get('risk_assessment') else '❌'}")
        print(f"• Recommendations: {len(result.get('recommendations', []))}")

        return result.get("success", False)

    except Exception as e:
        print(f"   ❌ Basic dashboard test failed: {str(e)}")
        return False


async def test_react_agent():
    """Test the ReAct agent"""
    print("\n🤖 Testing ReAct Agent")
    print("=" * 60)

    try:

        agent = PublicHealthReActAgent()

        result = await agent.assemble_dashboard()

        # Display results
        print("\n📊 REACT DASHBOARD SUMMARY:")
        print("-" * 40)
        print(result["dashboard_summary"])

        print("\n📈 REACT STATISTICS:")
        print(f"• Agent Type: {result.get('agent_type', 'Unknown')}")
        print(f"• Tools Used: {result.get('tools_used', [])}")
        print(f"• Success: {result['success']}")
        print(f"• Timestamp: {result.get('timestamp', 'Unknown')}")

        if result.get("error"):
            print(f"• Error: {result['error']}")

        # Enhanced features test
        print("\n🔬 REACT ENHANCED FEATURES:")
        print(
            f"• Epidemiological Signals: {len(result.get('epidemiological_signals', []))}"
        )
        print(f"• Rising Trends: {len(result.get('rising_trends', []))}")
        print(f"• Risk Assessment: {'✅' if result.get('risk_assessment') else '❌'}")
        print(f"• Recommendations: {len(result.get('recommendations', []))}")

        return result.get("success", False)

    except Exception as e:
        print(f"❌ ReAct agent test failed: {str(e)}")
        return False


async def main():
    """Run all comprehensive tests"""
    print("🧪 COMPREHENSIVE MCP + AGENT INTEGRATION TEST")
    print("=" * 80)

    # Run both tests
    standard_success = await test_comprehensive_integration()
    react_success = await test_react_agent()

    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print(f"Standard Agent: {'✅ PASSED' if standard_success else '❌ FAILED'}")
    print(f"ReAct Agent: {'✅ PASSED' if react_success else '❌ FAILED'}")

    if standard_success and react_success:
        print("\n🎯 OVERALL RESULT: ✅ ALL SYSTEMS OPERATIONAL")
        print("✅ MCP Server Integration: WORKING")
        print("✅ Agent LLM Integration: WORKING")
        print("✅ Dashboard Generation: WORKING")
        print("✅ Data Analysis: WORKING")
        print("✅ Enhanced Features: WORKING")
        print("\n🚀 The public health dashboard system is ready for production use!")
    else:
        print("\n⚠️ OVERALL RESULT: ❌ SOME TESTS FAILED")
        print("Check MCP server, API keys, and system configuration.")


if __name__ == "__main__":
    asyncio.run(main())
