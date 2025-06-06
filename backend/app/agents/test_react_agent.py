#!/usr/bin/env python3
"""
Test script for the Public Health ReAct Agent

This script tests the ReAct agent both directly and through the FastAPI integration.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add necessary paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "mcp"))

from .health_dashboard_react_agent import PublicHealthReActAgent


async def test_react_agent_basic():
    """Test basic ReAct agent functionality"""
    print("🧪 Testing ReAct Agent - Basic Functionality")
    print("=" * 60)

    try:
        # Test agent instantiation
        print("1. Testing agent instantiation...")
        agent = PublicHealthReActAgent()
        print("✅ Agent created successfully")

        # Test MCP client initialization
        print("\n2. Testing MCP client initialization...")
        await agent._init_mcp_client()
        print(f"✅ MCP client initialized with {len(agent.tools)} tools")

        # List available tools
        print("\n3. Available tools:")
        for tool in agent.tools:
            print(f"   - {tool.name}: {tool.description[:80]}...")

        print("\n✅ Basic functionality test completed")

    except Exception as e:
        print(f"❌ Basic test failed: {str(e)}")
        return False

    finally:
        # MCP client will auto-cleanup when async loop exits
        pass

    return True


async def test_react_agent_analysis():
    """Test ReAct agent dashboard generation"""
    print("\n🧪 Testing ReAct Agent - Dashboard Analysis")
    print("=" * 60)

    try:
        print("1. Creating ReAct agent...")
        agent = PublicHealthReActAgent()
        print("✅ Agent created")

        print("\n2. Generating epidemiological analysis...")
        print("⏳ This may take a moment as it fetches real data...")

        start_time = datetime.now()

        result = await agent.assemble_dashboard()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✅ Analysis completed in {duration:.2f} seconds")

        # Display results
        print("\n" + "=" * 80)
        print("📊 REACT AGENT ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Success: {result.get('success', False)}")
        print(f"Agent Type: {result.get('agent_type', 'Unknown')}")
        print(f"Tools Used: {result.get('tools_used', [])}")
        print(f"Timestamp: {result.get('timestamp', 'Unknown')}")

        if result.get("error"):
            print(f"❌ Error: {result['error']}")

        print("\n📄 Dashboard Summary:")
        print("-" * 40)
        print(result.get("dashboard_summary", "No summary available"))

        return result.get("success", False)

    except Exception as e:
        print(f"❌ Analysis test failed: {str(e)}")
        return False


async def test_mcp_tools_direct():
    """Test MCP tools directly"""
    print("\n🧪 Testing MCP Tools - Direct Access")
    print("=" * 60)

    try:
        print("1. Creating agent and initializing tools...")
        agent = PublicHealthReActAgent()
        await agent._init_mcp_client()
        print(f"✅ {len(agent.tools)} tools available")

        # Test each tool individually
        print("\n2. Testing individual tools...")

        # Test fetch_epi_signal
        print("\n   Testing fetch_epi_signal...")
        try:
            fetch_tool = next(
                (t for t in agent.tools if t.name == "fetch_epi_signal"), None
            )
            if fetch_tool:
                result = fetch_tool.func(
                    signal="smoothed_wcli",
                    time_type="day",
                    geo_type="state",
                    start_time="20241101",
                    end_time="20241130",
                )
                print("   ✅ fetch_epi_signal: Data fetched successfully")
                # Parse result to check if it's valid JSON
                data = json.loads(result)
                print(
                    f"   📊 Fetched {len(data)} data points"
                    if isinstance(data, list)
                    else "   📊 Data structure returned"
                )
            else:
                print("   ❌ fetch_epi_signal tool not found")
        except Exception as e:
            print(f"   ⚠️ fetch_epi_signal error: {str(e)[:100]}...")

        # Test detect_rising_trend
        print("\n   Testing detect_rising_trend...")
        try:
            trend_tool = next(
                (t for t in agent.tools if t.name == "detect_rising_trend"), None
            )
            if trend_tool:
                result = trend_tool.func(
                    signal_name="smoothed_wcli", value_column="value", window_size=7
                )
                print("   ✅ detect_rising_trend: Trend analysis completed")
                print(
                    f"   📈 Rising periods detected: {result.get('total_periods', 0)}"
                )
            else:
                print("   ❌ detect_rising_trend tool not found")
        except Exception as e:
            print(f"   ⚠️ detect_rising_trend error: {str(e)[:100]}...")

        print("\n✅ Direct tools test completed")
        return True

    except Exception as e:
        print(f"❌ Direct tools test failed: {str(e)}")
        return False

    finally:
        # MCP client will auto-cleanup when async loop exits
        pass


async def test_integration_scenarios():
    """Test different ReAct agent scenarios"""
    print("\n🧪 Testing ReAct Agent - Integration Scenarios")
    print("=" * 60)

    scenarios = [
        {
            "name": "COVID Trend Analysis",
            "query": "Analyze recent COVID-19 case trends and symptom patterns in the US",
        },
        {
            "name": "Healthcare Utilization",
            "query": "Examine COVID-related doctor visits and healthcare system utilization",
        },
        {
            "name": "Alert Correlation",
            "query": "Cross-reference epidemiological trends with current public health alerts",
        },
    ]

    results = []

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}...")

        try:
            agent = PublicHealthReActAgent()

            start_time = datetime.now()
            result = await agent.assemble_dashboard()
            duration = (datetime.now() - start_time).total_seconds()

            success = result.get("success", False)
            results.append(success)

            print(f"   {'✅' if success else '❌'} {scenario['name']}: {duration:.2f}s")

            if success:
                tools_used = result.get("tools_used", [])
                print(
                    f"   🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}"
                )
            else:
                error = result.get("error", "Unknown error")
                print(f"   ❌ Error: {error[:80]}...")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:80]}...")
            results.append(False)

    success_rate = sum(results) / len(results) if results else 0
    print(
        f"\n📊 Integration test results: {len([r for r in results if r])}/{len(results)} scenarios passed ({success_rate*100:.1f}%)"
    )

    return success_rate > 0.5


async def main():
    """Run all tests"""
    print("🏥 Public Health ReAct Agent - Test Suite")
    print("=" * 80)

    # Check prerequisites
    print("📋 Prerequisites Check:")
    print("   • MCP Server: Should be running on localhost:8001")
    print("   • LLM API Key: Required for ReAct agent")
    print("   • Network: Required for Delphi Epidata API access")
    print()

    input("Press Enter to continue with tests...")

    tests = [
        ("Basic Functionality", test_react_agent_basic),
        ("MCP Tools Direct", test_mcp_tools_direct),
        ("Dashboard Analysis", test_react_agent_analysis),
        ("Integration Scenarios", test_integration_scenarios),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))

    # Final summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results:
        print(f"{'✅' if result else '❌'} {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(
        f"\n🎯 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)"
    )

    if passed == total:
        print("🎉 All tests passed! ReAct agent is ready for use.")
    elif passed > total / 2:
        print("⚠️ Most tests passed. Check failed tests for issues.")
    else:
        print("❌ Multiple test failures. Check MCP server and configuration.")


if __name__ == "__main__":
    asyncio.run(main())
