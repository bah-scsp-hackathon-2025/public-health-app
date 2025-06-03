#!/usr/bin/env python3
"""
FastMCP Public Health Server with SSE Transport

This server provides two tools:
1. get_public_health_alerts - Retrieves public health alerts with filtering options
2. get_health_risk_trends - Returns time series data for public health risk trends

Uses FastMCP framework with SSE transport for improved developer experience.
"""

from typing import List, Optional, Literal
from datetime import datetime
from fastmcp import FastMCP

# Create the MCP server with SSE transport
mcp = FastMCP("Public Health FastMCP")

# Complete mock data for public health alerts (keeping all detail)
MOCK_ALERTS = [
    {
        "id": "alert_001",
        "title": "COVID-19 Outbreak in Downtown Area",
        "description": "Increased COVID-19 cases detected in downtown business district. Enhanced testing and safety measures recommended.",
        "severity": "HIGH",
        "state": "CA",
        "county": "Los Angeles",
        "timestamp": "2024-01-15T14:30:00Z",
        "alert_type": "OUTBREAK",
        "affected_population": 15000,
        "source": "LA County Health Department"
    },
    {
        "id": "alert_002", 
        "title": "Flu Activity Increasing Statewide",
        "description": "Influenza activity showing upward trend across multiple counties. Vaccination recommended.",
        "severity": "MEDIUM",
        "state": "NY",
        "county": "Multiple",
        "timestamp": "2024-01-14T09:15:00Z",
        "alert_type": "SEASONAL",
        "affected_population": 500000,
        "source": "NY State Health Department"
    },
    {
        "id": "alert_003",
        "title": "Food Safety Alert - E. coli Contamination",
        "description": "E. coli contamination detected in local produce. Recall issued for specific batch numbers.",
        "severity": "HIGH",
        "state": "TX",
        "county": "Harris",
        "timestamp": "2024-01-13T16:45:00Z",
        "alert_type": "FOOD_SAFETY",
        "affected_population": 75000,
        "source": "Texas Health Services"
    },
    {
        "id": "alert_004",
        "title": "Air Quality Advisory",
        "description": "Poor air quality due to wildfire smoke. Sensitive individuals advised to limit outdoor activities.",
        "severity": "MEDIUM",
        "state": "CA",
        "county": "Orange",
        "timestamp": "2024-01-12T11:20:00Z",
        "alert_type": "ENVIRONMENTAL",
        "affected_population": 200000,
        "source": "CA Air Resources Board"
    },
    {
        "id": "alert_005",
        "title": "Norovirus Outbreak at Schools",
        "description": "Multiple norovirus cases reported at three elementary schools. Enhanced cleaning protocols implemented.",
        "severity": "MEDIUM",
        "state": "FL",
        "county": "Miami-Dade",
        "timestamp": "2024-01-11T08:30:00Z",
        "alert_type": "OUTBREAK",
        "affected_population": 5000,
        "source": "Miami-Dade Health Department"
    },
    {
        "id": "alert_006",
        "title": "Heat Wave Warning",
        "description": "Extreme heat conditions expected for next 5 days. Public cooling centers opened.",
        "severity": "HIGH",
        "state": "AZ",
        "county": "Maricopa",
        "timestamp": "2024-01-10T16:00:00Z",
        "alert_type": "ENVIRONMENTAL",
        "affected_population": 450000,
        "source": "Arizona Department of Health"
    },
    {
        "id": "alert_007",
        "title": "Measles Cases Confirmed",
        "description": "Three confirmed measles cases linked to international travel. Contact tracing in progress.",
        "severity": "HIGH",
        "state": "WA",
        "county": "King",
        "timestamp": "2024-01-09T13:22:00Z",
        "alert_type": "OUTBREAK",
        "affected_population": 25000,
        "source": "Washington State Health Department"
    },
    {
        "id": "alert_008",
        "title": "Water Quality Alert",
        "description": "Elevated bacteria levels detected in municipal water supply. Boil water advisory issued.",
        "severity": "MEDIUM",
        "state": "OH",
        "county": "Cuyahoga",
        "timestamp": "2024-01-08T07:45:00Z",
        "alert_type": "ENVIRONMENTAL",
        "affected_population": 120000,
        "source": "Ohio Environmental Protection Agency"
    }
]

# Complete mock data for health risk trends (keeping all detail)
MOCK_RISK_TRENDS = {
    "covid_doctor_visits": {
        "name": "COVID-19 Doctor Visits",
        "description": "Weekly trend of COVID-19 related doctor visits",
        "unit": "visits_per_100k",
        "data_points": [
            {"date": "2024-01-01", "value": 45.2, "change_percent": -12.3},
            {"date": "2024-01-08", "value": 52.1, "change_percent": 15.3},
            {"date": "2024-01-15", "value": 48.7, "change_percent": -6.5},
            {"date": "2024-01-22", "value": 39.4, "change_percent": -19.1},
            {"date": "2024-01-29", "value": 41.8, "change_percent": 6.1},
            {"date": "2024-02-05", "value": 44.2, "change_percent": 5.7},
            {"date": "2024-02-12", "value": 38.9, "change_percent": -12.0}
        ]
    },
    "symptom_searches": {
        "name": "Flu Symptom Searches",
        "description": "Search volume for flu-related symptoms",
        "unit": "search_index",
        "data_points": [
            {"date": "2024-01-01", "value": 78, "change_percent": 5.4},
            {"date": "2024-01-08", "value": 85, "change_percent": 9.0},
            {"date": "2024-01-15", "value": 92, "change_percent": 8.2},
            {"date": "2024-01-22", "value": 88, "change_percent": -4.3},
            {"date": "2024-01-29", "value": 95, "change_percent": 8.0},
            {"date": "2024-02-05", "value": 103, "change_percent": 8.4},
            {"date": "2024-02-12", "value": 97, "change_percent": -5.8}
        ]
    },
    "icu_bed_occupation": {
        "name": "ICU Bed Occupation",
        "description": "Percentage of ICU beds occupied",
        "unit": "percentage",
        "data_points": [
            {"date": "2024-01-01", "value": 72.5, "change_percent": -2.1},
            {"date": "2024-01-08", "value": 75.8, "change_percent": 4.6},
            {"date": "2024-01-15", "value": 79.2, "change_percent": 4.5},
            {"date": "2024-01-22", "value": 77.1, "change_percent": -2.7},
            {"date": "2024-01-29", "value": 73.9, "change_percent": -4.1},
            {"date": "2024-02-05", "value": 76.4, "change_percent": 3.4},
            {"date": "2024-02-12", "value": 74.8, "change_percent": -2.1}
        ]
    },
    "respiratory_emergency_visits": {
        "name": "Respiratory Emergency Visits",
        "description": "Emergency department visits for respiratory issues",
        "unit": "visits_per_100k",
        "data_points": [
            {"date": "2024-01-01", "value": 125.3, "change_percent": 8.2},
            {"date": "2024-01-08", "value": 132.7, "change_percent": 5.9},
            {"date": "2024-01-15", "value": 128.9, "change_percent": -2.9},
            {"date": "2024-01-22", "value": 135.4, "change_percent": 5.0},
            {"date": "2024-01-29", "value": 142.1, "change_percent": 4.9},
            {"date": "2024-02-05", "value": 138.7, "change_percent": -2.4},
            {"date": "2024-02-12", "value": 144.2, "change_percent": 4.0}
        ]
    },
    "mental_health_calls": {
        "name": "Mental Health Crisis Calls",
        "description": "Volume of mental health crisis hotline calls",
        "unit": "calls_per_100k",
        "data_points": [
            {"date": "2024-01-01", "value": 23.1, "change_percent": 12.4},
            {"date": "2024-01-08", "value": 25.8, "change_percent": 11.7},
            {"date": "2024-01-15", "value": 22.4, "change_percent": -13.2},
            {"date": "2024-01-22", "value": 27.9, "change_percent": 24.6},
            {"date": "2024-01-29", "value": 24.6, "change_percent": -11.8},
            {"date": "2024-02-05", "value": 26.3, "change_percent": 6.9},
            {"date": "2024-02-12", "value": 28.1, "change_percent": 6.8}
        ]
    },
    "foodborne_illness_reports": {
        "name": "Foodborne Illness Reports",
        "description": "Reported cases of foodborne illnesses",
        "unit": "reports_per_100k",
        "data_points": [
            {"date": "2024-01-01", "value": 3.2, "change_percent": -8.6},
            {"date": "2024-01-08", "value": 4.1, "change_percent": 28.1},
            {"date": "2024-01-15", "value": 3.7, "change_percent": -9.8},
            {"date": "2024-01-22", "value": 5.2, "change_percent": 40.5},
            {"date": "2024-01-29", "value": 4.8, "change_percent": -7.7},
            {"date": "2024-02-05", "value": 3.9, "change_percent": -18.8},
            {"date": "2024-02-12", "value": 4.4, "change_percent": 12.8}
        ]
    }
}

@mcp.tool()
def get_public_health_alerts(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None, 
    states: Optional[List[str]] = None,
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None,
    alert_type: Optional[Literal["OUTBREAK", "SEASONAL", "FOOD_SAFETY", "ENVIRONMENTAL"]] = None,
    limit: int = 10
) -> dict:
    """
    Retrieve public health alerts with optional filtering by date range and states.
    Returns alerts sorted by timestamp (most recent first).
    
    Args:
        start_date: Start date for filtering alerts (ISO format). If not provided, returns most recent alerts.
        end_date: End date for filtering alerts (ISO format). If not provided, uses current time.
        states: List of state codes to filter alerts (e.g., ['CA', 'NY']). If not provided, returns alerts from all states.
        severity: Filter alerts by severity level (LOW, MEDIUM, HIGH)
        alert_type: Filter alerts by type (OUTBREAK, SEASONAL, FOOD_SAFETY, ENVIRONMENTAL)
        limit: Maximum number of alerts to return (1-100)
    """
    # Start with all alerts
    filtered_alerts = MOCK_ALERTS.copy()
    
    # Filter by states if provided
    if states:
        filtered_alerts = [alert for alert in filtered_alerts if alert["state"] in states]
    
    # Filter by severity if provided
    if severity:
        filtered_alerts = [alert for alert in filtered_alerts if alert["severity"] == severity]
    
    # Filter by alert type if provided
    if alert_type:
        filtered_alerts = [alert for alert in filtered_alerts if alert["alert_type"] == alert_type]
    
    # Filter by date range if provided
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00')) >= start_dt
            ]
        except ValueError:
            # Invalid date format, return error in metadata
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00')) <= end_dt
            ]
        except ValueError:
            # Invalid date format, return error in metadata
            pass
    
    # Sort by timestamp descending (most recent first)
    filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply limit
    filtered_alerts = filtered_alerts[:min(limit, 100)]  # Cap at 100 for safety
    
    return {
        "total_alerts": len(filtered_alerts),
        "filters_applied": {
            "states": states if states else "all",
            "severity": severity if severity else "all",
            "alert_type": alert_type if alert_type else "all",
            "date_range": {
                "start": start_date if start_date else "not specified",
                "end": end_date if end_date else "not specified"
            },
            "limit": limit
        },
        "alerts": filtered_alerts,
        "metadata": {
            "server": "FastMCP Public Health Server",
            "timestamp": datetime.now().isoformat(),
            "total_available_alerts": len(MOCK_ALERTS)
        }
    }

@mcp.tool()
def get_health_risk_trends(
    risk_types: Optional[List[Literal["covid_doctor_visits", "symptom_searches", "icu_bed_occupation", "respiratory_emergency_visits", "mental_health_calls", "foodborne_illness_reports"]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Retrieve time series data for top public health risk trends including COVID-19 visits, 
    symptom searches, ICU occupation, respiratory emergency visits, mental health calls, and foodborne illness reports.
    
    Args:
        risk_types: List of risk trend types to retrieve. Available options: covid_doctor_visits, 
                   symptom_searches, icu_bed_occupation, respiratory_emergency_visits, mental_health_calls, foodborne_illness_reports.
                   If not provided, returns all available trends.
        start_date: Start date for trend data (YYYY-MM-DD format). If not provided, returns all available data.
        end_date: End date for trend data (YYYY-MM-DD format). If not provided, returns all available data.
    """
    if risk_types is None:
        risk_types = list(MOCK_RISK_TRENDS.keys())
    
    # Filter data based on requested risk types
    filtered_trends = {}
    for risk_type in risk_types:
        if risk_type in MOCK_RISK_TRENDS:
            trend_data = MOCK_RISK_TRENDS[risk_type].copy()
            
            # Filter data points by date range if provided
            if start_date or end_date:
                filtered_points = []
                for point in trend_data["data_points"]:
                    try:
                        point_date = datetime.strptime(point["date"], "%Y-%m-%d").date()
                        
                        # Check start date
                        if start_date:
                            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                            if point_date < start_dt:
                                continue
                        
                        # Check end date
                        if end_date:
                            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                            if point_date > end_dt:
                                continue
                        
                        filtered_points.append(point)
                    except ValueError:
                        # Invalid date format, skip filtering
                        filtered_points = trend_data["data_points"]
                        break
                
                trend_data["data_points"] = filtered_points
            
            filtered_trends[risk_type] = trend_data
    
    return {
        "requested_risk_types": risk_types,
        "available_risk_types": list(MOCK_RISK_TRENDS.keys()),
        "date_range": {
            "start": start_date if start_date else "not specified",
            "end": end_date if end_date else "not specified"
        },
        "trends": filtered_trends,
        "metadata": {
            "server": "FastMCP Public Health Server",
            "data_source": "Mock Public Health Data",
            "last_updated": datetime.now().isoformat(),
            "total_trend_types": len(filtered_trends),
            "transport": "SSE"
        }
    }

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the MCP server and available capabilities.
    
    Returns:
        dict: Server information including version, available tools, and statistics.
    """
    return {
        "server_name": "Public Health FastMCP Server",
        "version": "2.0.0",
        "framework": "FastMCP",
        "transport": "SSE (Server-Sent Events)",
        "capabilities": {
            "tools": ["get_public_health_alerts", "get_health_risk_trends", "get_server_info"],
            "resources": [],
            "prompts": []
        },
        "statistics": {
            "total_mock_alerts": len(MOCK_ALERTS),
            "total_risk_trend_types": len(MOCK_RISK_TRENDS),
            "available_alert_severities": ["LOW", "MEDIUM", "HIGH"],
            "available_alert_types": ["OUTBREAK", "SEASONAL", "FOOD_SAFETY", "ENVIRONMENTAL"],
            "available_states": list(set(alert["state"] for alert in MOCK_ALERTS))
        },
        "last_updated": datetime.now().isoformat()
    }

# FastMCP will automatically handle server setup, SSE transport, and schema generation!
if __name__ == "__main__":
    # Run with SSE transport (HTTP server)
    mcp.run(transport="sse", port=8000, host="0.0.0.0") 