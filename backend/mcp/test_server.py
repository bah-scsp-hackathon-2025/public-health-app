#!/usr/bin/env python3
"""
Test script for the Public Health MCP Server

This script tests both tools with various parameter combinations.
"""

import asyncio
import json
from mcp_public_health import get_public_health_alerts, get_health_risk_trends

def test_public_health_alerts():
    """Test the public health alerts tool"""
    print("=== Testing Public Health Alerts Tool ===\n")
    
    # Test 1: Default (no parameters)
    print("Test 1: Default alerts (no parameters)")
    result = get_public_health_alerts()
    print(f"Response type: {type(result)}")
    print(f"Total alerts returned: {result['total_alerts']}")
    print(f"Filters applied: {result['filters_applied']}")
    print()
    
    # Test 2: Filter by states
    print("Test 2: Filter by states (CA, NY)")
    result = get_public_health_alerts(states=["CA", "NY"])
    print(f"Total alerts returned: {result['total_alerts']}")
    print(f"States in results: {[alert['state'] for alert in result['alerts']]}")
    print()
    
    # Test 3: Filter by severity
    print("Test 3: Filter by severity (HIGH)")
    result = get_public_health_alerts(severity="HIGH")
    print(f"Total alerts returned: {result['total_alerts']}")
    print(f"Severities in results: {[alert['severity'] for alert in result['alerts']]}")
    print()
    
    # Test 4: Date range filter
    print("Test 4: Filter by date range")
    result = get_public_health_alerts(
        start_date="2024-01-12T00:00:00Z",
        end_date="2024-01-15T23:59:59Z"
    )
    print(f"Total alerts returned: {result['total_alerts']}")
    print(f"Date range: {result['filters_applied']['date_range']}")
    print()
    
    # Test 5: Limit results
    print("Test 5: Limit results (limit=2)")
    result = get_public_health_alerts(limit=2)
    print(f"Total alerts returned: {result['total_alerts']}")
    print()

def test_health_risk_trends():
    """Test the health risk trends tool"""
    print("=== Testing Health Risk Trends Tool ===\n")
    
    # Test 1: Default (all trends)
    print("Test 1: Default trends (all types)")
    result = get_health_risk_trends()
    print(f"Total trend types returned: {result['metadata']['total_trend_types']}")
    print(f"Available types: {result['available_risk_types']}")
    print()
    
    # Test 2: Specific risk types
    print("Test 2: Specific risk types (COVID visits, ICU occupation)")
    result = get_health_risk_trends(
        risk_types=["covid_doctor_visits", "icu_bed_occupation"]
    )
    print(f"Requested types: {result['requested_risk_types']}")
    print(f"Trend types in response: {list(result['trends'].keys())}")
    print()
    
    # Test 3: Date range filter
    print("Test 3: Filter by date range")
    result = get_health_risk_trends(
        start_date="2024-01-08",
        end_date="2024-01-22"
    )
    print(f"Date range: {result['date_range']}")
    for trend_name, trend_data in result['trends'].items():
        print(f"{trend_name}: {len(trend_data['data_points'])} data points")
    print()
    
    # Test 4: Single trend type with date filter
    print("Test 4: Single trend type with date filter")
    result = get_health_risk_trends(
        risk_types=["symptom_searches"],
        start_date="2024-01-15",
        end_date="2024-01-29"
    )
    trend_data = result['trends']['symptom_searches']
    print(f"Trend: {trend_data['name']}")
    print(f"Data points: {len(trend_data['data_points'])}")
    print(f"Date range: {trend_data['data_points'][0]['date']} to {trend_data['data_points'][-1]['date']}")
    print()

def test_error_cases():
    """Test error handling"""
    print("=== Testing Error Cases ===\n")
    
    # Test invalid date format
    print("Test 1: Invalid date format")
    try:
        result = get_public_health_alerts(start_date="invalid-date")
        print("Error handling test passed - invalid date was handled gracefully")
        print(f"Total alerts returned: {result['total_alerts']}")
    except Exception as e:
        print(f"Expected error caught: {str(e)}")
    print()
    
    # Test invalid risk type
    print("Test 2: Invalid risk type")
    result = get_health_risk_trends(risk_types=["invalid_risk_type"])
    print(f"Trends returned for invalid type: {len(result['trends'])}")
    print()

def main():
    """Run all tests"""
    print("Public Health MCP Server Test Suite")
    print("=" * 50)
    print()
    
    test_public_health_alerts()
    test_health_risk_trends()
    test_error_cases()
    
    print("All tests completed!")

if __name__ == "__main__":
    main() 