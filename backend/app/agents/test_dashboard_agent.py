#!/usr/bin/env python3
"""
Test script for the Public Health Dashboard Agent

This script tests the LangGraph agent workflow with and without LLM providers.
It demonstrates the MCP integration and data flow through the agent.
"""

import asyncio
import os
import json
from datetime import datetime

from health_dashboard_agent import PublicHealthDashboardAgent, test_dashboard_agent

async def test_mcp_data_fetching():
    """Test just the MCP data fetching part without LLM"""
    print("🧪 Testing MCP Data Fetching (No LLM Required)")
    print("=" * 60)
    
    try:
        # Create a mock agent just for MCP testing
        agent = PublicHealthDashboardAgent()
        
        # Test MCP client initialization
        await agent._init_mcp_client()
        print("✅ MCP client initialized")
        
        # Test data fetching
        from health_dashboard_agent import DashboardState
        from langchain_core.messages import HumanMessage
        
        initial_state = DashboardState(
            messages=[HumanMessage(content="Test data fetch")],
            current_request="Test MCP integration",
            alerts_data=None,
            trends_data=None,
            analysis_result=None,
            dashboard_summary=None,
            error_message=None,
            timestamp=datetime.now().isoformat()
        )
        
        # Run the data fetching node
        result_state = await agent._fetch_health_data_node(initial_state)
        
        if result_state.get("error_message"):
            print(f"❌ Error: {result_state['error_message']}")
            return False
        
        # Display fetched data summary
        alerts_data = result_state.get("alerts_data", {})
        trends_data = result_state.get("trends_data", {})
        
        print(f"✅ Fetched {alerts_data.get('total_alerts', 0)} alerts")
        print(f"✅ Fetched {len(trends_data.get('trends', {}))} trend categories")
        
        # Show sample data
        if alerts_data.get("alerts"):
            print("\n📋 Sample Alert:")
            sample_alert = alerts_data["alerts"][0]
            print(f"   Title: {sample_alert.get('title', 'N/A')}")
            print(f"   Severity: {sample_alert.get('severity', 'N/A')}")
            print(f"   State: {sample_alert.get('state', 'N/A')}")
            print(f"   Affected: {sample_alert.get('affected_population', 0):,}")
        
        if trends_data.get("trends"):
            print("\n📈 Sample Trend Categories:")
            for trend_name, trend_data in list(trends_data["trends"].items())[:2]:
                latest_point = trend_data.get("data_points", [])[-1] if trend_data.get("data_points") else {}
                print(f"   {trend_data.get('name', trend_name)}: {latest_point.get('value', 'N/A')} {trend_data.get('unit', '')}")
        
        # MCP client will auto-cleanup when async loop exits
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_without_llm():
    """Test the agent workflow without LLM (mock analysis)"""
    print("\n🤖 Testing Agent Workflow (Without LLM)")
    print("=" * 60)
    
    try:
        # Create agent (will fail LLM initialization but we'll handle it)
        class MockLLM:
            async def ainvoke(self, messages):
                class MockResponse:
                    content = json.dumps({
                        "critical_findings": [
                            "High severity alerts detected in multiple states",
                            "Increasing trend in respiratory emergency visits",
                            "COVID-19 outbreaks require immediate attention"
                        ],
                        "risk_assessment": {
                            "high_risk_areas": ["CA", "TX", "WA"],
                            "trending_concerns": ["respiratory issues", "foodborne illness"]
                        },
                        "recommendations": [
                            "Enhanced monitoring in high-risk states",
                            "Increase testing capacity for respiratory illnesses",
                            "Review food safety protocols"
                        ]
                    })
                return MockResponse()
        
        # Create agent with mock LLM
        agent = PublicHealthDashboardAgent()
        agent.llm = MockLLM()
        
        # Test the workflow
        result = await agent.assemble_dashboard()
        
        print("✅ Agent workflow completed")
        print(f"✅ Alerts processed: {result['alerts_count']}")
        print(f"✅ Trends processed: {result['trends_count']}")
        print(f"✅ Success: {result['success']}")
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        else:
            print("\n📊 Generated Summary:")
            print("-" * 40)
            print(result["dashboard_summary"])
        
        return result["success"]
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_real_llm():
    """Test with real LLM if API keys are available"""
    print("\n🧠 Testing with Real LLM")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No API keys found. Skipping real LLM test.")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY to test with real LLM.")
        return True
    
    try:
        # Run the actual test
        result = await test_dashboard_agent()
        return result is not None
        
    except Exception as e:
        print(f"❌ Real LLM test failed: {str(e)}")
        return False

async def test_basic_workflow():
    """Test basic workflow functionality"""
    print("🧪 Testing Basic Agent Workflow")
    print("=" * 50)
    
    try:
        agent = PublicHealthDashboardAgent()
        
        result = await agent.assemble_dashboard()
        
        print("✅ Basic workflow test completed")
        print(f"Success: {result.get('success', False)}")
        print(f"Summary length: {len(result.get('dashboard_summary', ''))}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Basic workflow test failed: {str(e)}")
        return False

async def run_comprehensive_test():
    """Run all tests"""
    print("🏥 Comprehensive Public Health Dashboard Agent Test Suite")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: MCP Data Fetching
    print("\n" + "🔍 TEST 1: MCP Data Fetching")
    result1 = await test_mcp_data_fetching()
    test_results.append(("MCP Data Fetching", result1))
    
    # Test 2: Agent Workflow (Mock LLM)
    print("\n" + "🤖 TEST 2: Agent Workflow (Mock LLM)")
    result2 = await test_agent_without_llm()
    test_results.append(("Agent Workflow (Mock)", result2))
    
    # Test 3: Real LLM (if available)
    print("\n" + "🧠 TEST 3: Real LLM Integration")
    result3 = await test_with_real_llm()
    test_results.append(("Real LLM Integration", result3))
    
    # Test 4: Basic Workflow
    print("\n" + "🧪 TEST 4: Basic Agent Workflow")
    result4 = await test_basic_workflow()
    test_results.append(("Basic Agent Workflow", result4))
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    total_passed = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n🎯 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! The dashboard agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return total_passed == total_tests

async def demo_interactive_features():
    """Demonstrate interactive features"""
    print("\n🎮 Demo: Interactive Features")
    print("=" * 50)
    
    print("The dashboard agent supports interactive mode:")
    print("  python health_dashboard_agent.py interactive")
    print("")
    print("Available commands in interactive mode:")
    print("  - 'alerts only' - Focus on current alerts")
    print("  - 'trends only' - Focus on risk trends") 
    print("  - 'high severity' - High severity issues only")
    print("  - 'state CA' - Focus on California data")
    print("  - 'exit' - Quit the session")
    print("")
    print("Example usage in your LangGraph application:")
    print("""
    from health_dashboard_agent import PublicHealthDashboardAgent
    
    # Create agent
            agent = PublicHealthDashboardAgent()
    
    # Generate dashboard
    result = await agent.assemble_dashboard()
    
    # Use the result
    dashboard_html = result["dashboard_summary"]
    alerts_count = result["alerts_count"]
    """)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "mcp-only":
            asyncio.run(test_mcp_data_fetching())
        elif sys.argv[1] == "mock-llm":
            asyncio.run(test_agent_without_llm())
        elif sys.argv[1] == "real-llm":
            asyncio.run(test_with_real_llm())
        elif sys.argv[1] == "demo":
            asyncio.run(demo_interactive_features())
        else:
            print("Available test modes:")
            print("  python test_dashboard_agent.py mcp-only")
            print("  python test_dashboard_agent.py mock-llm")
            print("  python test_dashboard_agent.py real-llm")
            print("  python test_dashboard_agent.py demo")
    else:
        asyncio.run(run_comprehensive_test()) 