#!/usr/bin/env python3
"""
Test script for the Public Health MCP Server

This script tests both tools with various parameter combinations.
"""

import asyncio
import json
from mcp_public_health import get_public_health_alerts, get_health_risk_trends

async def test_public_health_alerts():
    """Test the public health alerts tool"""
    print("=== Testing Public Health Alerts Tool ===\n")
    
    # Test 1: Default (no parameters)
    print("Test 1: Default alerts (no parameters)")
    result = await get_public_health_alerts({})
    print(f"Response length: {len(result[0].text)} characters")
    data = json.loads(result[0].text)
    print(f"Total alerts returned: {data['total_alerts']}")
    print(f"Filters applied: {data['filters_applied']}")
    print()
    
    # Test 2: Filter by states
    print("Test 2: Filter by states (CA, NY)")
    result = await get_public_health_alerts({"states": ["CA", "NY"]})
    data = json.loads(result[0].text)
    print(f"Total alerts returned: {data['total_alerts']}")
    print(f"States in results: {[alert['state'] for alert in data['alerts']]}")
    print()
    
    # Test 3: Filter by severity
    print("Test 3: Filter by severity (HIGH)")
    result = await get_public_health_alerts({"severity": "HIGH"})
    data = json.loads(result[0].text)
    print(f"Total alerts returned: {data['total_alerts']}")
    print(f"Severities in results: {[alert['severity'] for alert in data['alerts']]}")
    print()
    
    # Test 4: Date range filter
    print("Test 4: Filter by date range")
    result = await get_public_health_alerts({
        "start_date": "2024-01-12T00:00:00Z",
        "end_date": "2024-01-15T23:59:59Z"
    })
    data = json.loads(result[0].text)
    print(f"Total alerts returned: {data['total_alerts']}")
    print(f"Date range: {data['filters_applied']['date_range']}")
    print()
    
    # Test 5: Limit results
    print("Test 5: Limit results (limit=2)")
    result = await get_public_health_alerts({"limit": 2})
    data = json.loads(result[0].text)
    print(f"Total alerts returned: {data['total_alerts']}")
    print()

async def test_health_risk_trends():
    """Test the health risk trends tool"""
    print("=== Testing Health Risk Trends Tool ===\n")
    
    # Test 1: Default (all trends)
    print("Test 1: Default trends (all types)")
    result = await get_health_risk_trends({})
    data = json.loads(result[0].text)
    print(f"Total trend types returned: {data['metadata']['total_trend_types']}")
    print(f"Available types: {data['available_risk_types']}")
    print()
    
    # Test 2: Specific risk types
    print("Test 2: Specific risk types (COVID visits, ICU occupation)")
    result = await get_health_risk_trends({
        "risk_types": ["covid_doctor_visits", "icu_bed_occupation"]
    })
    data = json.loads(result[0].text)
    print(f"Requested types: {data['requested_risk_types']}")
    print(f"Trend types in response: {list(data['trends'].keys())}")
    print()
    
    # Test 3: Date range filter
    print("Test 3: Filter by date range")
    result = await get_health_risk_trends({
        "start_date": "2024-01-08",
        "end_date": "2024-01-22"
    })
    data = json.loads(result[0].text)
    print(f"Date range: {data['date_range']}")
    for trend_name, trend_data in data['trends'].items():
        print(f"{trend_name}: {len(trend_data['data_points'])} data points")
    print()
    
    # Test 4: Single trend type with date filter
    print("Test 4: Single trend type with date filter")
    result = await get_health_risk_trends({
        "risk_types": ["symptom_searches"],
        "start_date": "2024-01-15",
        "end_date": "2024-01-29"
    })
    data = json.loads(result[0].text)
    trend_data = data['trends']['symptom_searches']
    print(f"Trend: {trend_data['name']}")
    print(f"Data points: {len(trend_data['data_points'])}")
    print(f"Date range: {trend_data['data_points'][0]['date']} to {trend_data['data_points'][-1]['date']}")
    print()

async def test_error_cases():
    """Test error handling"""
    print("=== Testing Error Cases ===\n")
    
    # Test invalid date format
    print("Test 1: Invalid date format")
    try:
        result = await get_public_health_alerts({"start_date": "invalid-date"})
        print("Error handling test passed")
    except Exception as e:
        print(f"Expected error caught: {str(e)}")
    print()
    
    # Test invalid risk type
    print("Test 2: Invalid risk type")
    result = await get_health_risk_trends({"risk_types": ["invalid_risk_type"]})
    data = json.loads(result[0].text)
    print(f"Trends returned for invalid type: {len(data['trends'])}")
    print()

async def main():
    """Run all tests"""
    print("Public Health MCP Server Test Suite")
    print("=" * 50)
    print()
    
    await test_public_health_alerts()
    await test_health_risk_trends()
    await test_error_cases()
    
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 