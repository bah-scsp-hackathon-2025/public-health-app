#!/usr/bin/env python3
"""
Demo script for the Public Health Dashboard Agent

This script demonstrates the LangGraph agent workflow with mock data,
showing how it would work with real MCP server data.
"""

import asyncio
import json
from datetime import datetime, timedelta
from health_dashboard_agent import PublicHealthDashboardAgent

# Mock data that simulates what the FastMCP server would return
MOCK_ALERTS_DATA = {
    "total_alerts": 12,
    "alerts": [
        {
            "id": "alert_001",
            "title": "COVID-19 Outbreak in Nursing Facilities",
            "description": "Multiple nursing facilities reporting increased COVID-19 cases",
            "severity": "HIGH",
            "state": "CA",
            "affected_population": 45000,
            "date_issued": (datetime.now() - timedelta(days=2)).isoformat(),
            "status": "ACTIVE"
        },
        {
            "id": "alert_002", 
            "title": "Foodborne Illness Cluster",
            "description": "Salmonella outbreak linked to contaminated produce",
            "severity": "HIGH",
            "state": "TX",
            "affected_population": 12000,
            "date_issued": (datetime.now() - timedelta(days=1)).isoformat(),
            "status": "ACTIVE"
        },
        {
            "id": "alert_003",
            "title": "Air Quality Emergency",
            "description": "Wildfire smoke causing hazardous air quality",
            "severity": "MEDIUM",
            "state": "WA",
            "affected_population": 890000,
            "date_issued": datetime.now().isoformat(),
            "status": "ACTIVE"
        },
        {
            "id": "alert_004",
            "title": "Heat Wave Warning",
            "description": "Extreme temperatures expected for next 5 days",
            "severity": "MEDIUM",
            "state": "AZ",
            "affected_population": 320000,
            "date_issued": datetime.now().isoformat(),
            "status": "ACTIVE"
        },
        {
            "id": "alert_005",
            "title": "Water Contamination",
            "description": "E. coli detected in municipal water supply",
            "severity": "HIGH",
            "state": "FL",
            "affected_population": 78000,
            "date_issued": (datetime.now() - timedelta(hours=6)).isoformat(),
            "status": "ACTIVE"
        }
    ]
}

MOCK_TRENDS_DATA = {
    "trends": {
        "respiratory_visits": {
            "name": "Respiratory Emergency Visits",
            "description": "Emergency department visits for respiratory issues",
            "unit": "visits per 100k population",
            "data_points": [
                {"date": (datetime.now() - timedelta(days=30)).isoformat(), "value": 45.2},
                {"date": (datetime.now() - timedelta(days=23)).isoformat(), "value": 48.1},
                {"date": (datetime.now() - timedelta(days=16)).isoformat(), "value": 52.3},
                {"date": (datetime.now() - timedelta(days=9)).isoformat(), "value": 55.7},
                {"date": (datetime.now() - timedelta(days=2)).isoformat(), "value": 58.9}
            ]
        },
        "foodborne_illness": {
            "name": "Foodborne Illness Reports",
            "description": "Reported cases of foodborne illness",
            "unit": "cases per 100k population",
            "data_points": [
                {"date": (datetime.now() - timedelta(days=30)).isoformat(), "value": 12.1},
                {"date": (datetime.now() - timedelta(days=23)).isoformat(), "value": 13.8},
                {"date": (datetime.now() - timedelta(days=16)).isoformat(), "value": 14.2},
                {"date": (datetime.now() - timedelta(days=9)).isoformat(), "value": 15.1},
                {"date": (datetime.now() - timedelta(days=2)).isoformat(), "value": 13.9}
            ]
        },
        "covid_cases": {
            "name": "COVID-19 Cases",
            "description": "New COVID-19 cases reported",
            "unit": "cases per 100k population",
            "data_points": [
                {"date": (datetime.now() - timedelta(days=30)).isoformat(), "value": 89.3},
                {"date": (datetime.now() - timedelta(days=23)).isoformat(), "value": 85.7},
                {"date": (datetime.now() - timedelta(days=16)).isoformat(), "value": 82.1},
                {"date": (datetime.now() - timedelta(days=9)).isoformat(), "value": 78.4},
                {"date": (datetime.now() - timedelta(days=2)).isoformat(), "value": 84.8}
            ]
        },
        "air_quality_index": {
            "name": "Air Quality Index",
            "description": "Average air quality measurements",
            "unit": "AQI",
            "data_points": [
                {"date": (datetime.now() - timedelta(days=30)).isoformat(), "value": 65.2},
                {"date": (datetime.now() - timedelta(days=23)).isoformat(), "value": 72.1},
                {"date": (datetime.now() - timedelta(days=16)).isoformat(), "value": 89.3},
                {"date": (datetime.now() - timedelta(days=9)).isoformat(), "value": 156.7},
                {"date": (datetime.now() - timedelta(days=2)).isoformat(), "value": 178.9}
            ]
        }
    }
}

class MockMCPTool:
    """Mock MCP tool for demonstration"""
    def __init__(self, name, data):
        self.name = name
        self.data = data
    
    async def ainvoke(self, params):
        return self.data

class MockMCPClient:
    """Mock MCP client for demonstration"""
    async def get_tools(self):
        return [
            MockMCPTool("get_public_health_alerts", MOCK_ALERTS_DATA),
            MockMCPTool("get_health_risk_trends", MOCK_TRENDS_DATA)
        ]
    
    async def close(self):
        pass

async def demo_dashboard_agent():
    """Demonstrate the dashboard agent with mock data"""
    print("🏥 Public Health Dashboard Agent Demo")
    print("=" * 60)
    print("This demo shows the LangGraph agent workflow using mock data")
    print("that simulates real public health alerts and trends.")
    print("=" * 60)
    
    # Create agent
    agent = PublicHealthDashboardAgent()
    
    # Replace MCP client with mock
    agent.mcp_client = MockMCPClient()
    
    print("\n🚀 Generating dashboard with mock health data...")
    print("-" * 60)
    
    # Generate dashboard
    result = await agent.generate_dashboard(
        "Generate a comprehensive public health dashboard focusing on current alerts and emerging trends"
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 GENERATED DASHBOARD SUMMARY")
    print("=" * 80)
    print(result["dashboard_summary"])
    
    print("\n" + "=" * 80)
    print("📈 DASHBOARD STATISTICS")
    print("=" * 80)
    print(f"• Total Alerts Processed: {result['alerts_count']}")
    print(f"• Trend Categories Analyzed: {result['trends_count']}")
    print(f"• Generation Timestamp: {result['timestamp']}")
    print(f"• Processing Success: {result['success']}")
    
    if result.get("error"):
        print(f"• Error Details: {result['error']}")
    
    print("\n" + "=" * 80)
    print("🎯 DEMO INSIGHTS")
    print("=" * 80)
    print("This demonstrates how the LangGraph agent:")
    print("1. ✅ Fetches data from MCP servers (simulated)")
    print("2. ✅ Analyzes health patterns and trends")
    print("3. ✅ Generates executive-level summaries")
    print("4. ✅ Handles errors gracefully")
    print("5. ✅ Works with or without LLM providers")
    
    print("\n🔗 Integration Options:")
    print("• Web dashboards (Flask, FastAPI)")
    print("• Slack/Teams notifications")
    print("• Scheduled reports")
    print("• Real-time monitoring systems")
    
    return result

async def demo_interactive_requests():
    """Demo different types of dashboard requests"""
    print("\n" + "=" * 80)
    print("🎮 INTERACTIVE REQUEST DEMO")
    print("=" * 80)
    
    agent = PublicHealthDashboardAgent()
    agent.mcp_client = MockMCPClient()
    
    # Different request types
    requests = [
        ("High Severity Focus", "Focus on high severity alerts requiring immediate action"),
        ("Regional Analysis", "Analyze health situation in California and Texas"),
        ("Trend Analysis", "Focus on emerging health trends and patterns"),
        ("Emergency Response", "Generate emergency response priorities")
    ]
    
    for request_name, request_text in requests:
        print(f"\n📋 {request_name}:")
        print("-" * 40)
        
        result = await agent.generate_dashboard(request_text)
        
        # Show abbreviated summary
        summary_lines = result["dashboard_summary"].split('\n')[:8]
        for line in summary_lines:
            if line.strip():
                print(line)
        print("... (truncated for demo)")
        
        print(f"✅ Processed {result['alerts_count']} alerts, {result['trends_count']} trends")

if __name__ == "__main__":
    print("🏥 Public Health Dashboard Agent - Complete Demo")
    print("=" * 80)
    
    # Run main demo
    asyncio.run(demo_dashboard_agent())
    
    # Run interactive demo
    asyncio.run(demo_interactive_requests())
    
    print("\n" + "=" * 80)
    print("🎉 Demo Complete!")
    print("=" * 80)
    print("To use with real data:")
    print("1. Start the FastMCP server: python3 -m uvicorn fastmcp_server:app --port 8000")
    print("2. Set API keys: export OPENAI_API_KEY=your-key")
    print("3. Run: python health_dashboard_agent.py")
    print("4. Or interactive mode: python health_dashboard_agent.py interactive") 