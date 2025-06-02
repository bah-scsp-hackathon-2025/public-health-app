#!/usr/bin/env python3
"""
MCP Server for Public Health Data Tools

This server provides two tools:
1. get_public_health_alerts - Retrieves public health alerts with filtering options
2. get_health_risk_trends - Returns time series data for public health risk trends
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("public-health-mcp")

# Create server instance
server = Server("public-health-mcp")

# Mock data for public health alerts
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
    }
]

# Mock data for health risk trends
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
            {"date": "2024-01-29", "value": 41.8, "change_percent": 6.1}
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
            {"date": "2024-01-29", "value": 95, "change_percent": 8.0}
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
            {"date": "2024-01-29", "value": 73.9, "change_percent": -4.1}
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
            {"date": "2024-01-29", "value": 142.1, "change_percent": 4.9}
        ]
    }
}

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool should have a name, description, and input schema.
    """
    return [
        types.Tool(
            name="get_public_health_alerts",
            description="Retrieve public health alerts with optional filtering by date range and states. Returns alerts sorted by timestamp (most recent first).",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start date for filtering alerts (ISO format). If not provided, returns most recent alerts."
                    },
                    "end_date": {
                        "type": "string", 
                        "format": "date-time",
                        "description": "End date for filtering alerts (ISO format). If not provided, uses current time."
                    },
                    "states": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of state codes to filter alerts (e.g., ['CA', 'NY']). If not provided, returns alerts from all states."
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "Filter alerts by severity level"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10,
                        "description": "Maximum number of alerts to return"
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_health_risk_trends",
            description="Retrieve time series data for top public health risk trends including COVID-19 visits, symptom searches, ICU occupation, and respiratory emergency visits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "risk_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["covid_doctor_visits", "symptom_searches", "icu_bed_occupation", "respiratory_emergency_visits"]
                        },
                        "description": "List of risk trend types to retrieve. If not provided, returns all available trends."
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Start date for trend data (YYYY-MM-DD format). If not provided, returns last 30 days."
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date", 
                        "description": "End date for trend data (YYYY-MM-DD format). If not provided, uses current date."
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """
    Handle tool calls.
    """
    if arguments is None:
        arguments = {}
        
    if name == "get_public_health_alerts":
        return await get_public_health_alerts(arguments)
    elif name == "get_health_risk_trends":
        return await get_health_risk_trends(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def get_public_health_alerts(arguments: Dict[str, Any]) -> list[types.TextContent]:
    """
    Retrieve public health alerts with filtering options.
    """
    try:
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date") 
        states = arguments.get("states", [])
        severity = arguments.get("severity")
        limit = arguments.get("limit", 10)
        
        # Start with all alerts
        filtered_alerts = MOCK_ALERTS.copy()
        
        # Filter by states if provided
        if states:
            filtered_alerts = [alert for alert in filtered_alerts if alert["state"] in states]
        
        # Filter by severity if provided
        if severity:
            filtered_alerts = [alert for alert in filtered_alerts if alert["severity"] == severity]
        
        # Filter by date range if provided
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00')) >= start_dt
            ]
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00')) <= end_dt
            ]
        
        # Sort by timestamp descending (most recent first)
        filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        filtered_alerts = filtered_alerts[:limit]
        
        result = {
            "total_alerts": len(filtered_alerts),
            "filters_applied": {
                "states": states if states else "all",
                "severity": severity if severity else "all",
                "date_range": {
                    "start": start_date if start_date else "not specified",
                    "end": end_date if end_date else "not specified"
                }
            },
            "alerts": filtered_alerts
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error in get_public_health_alerts: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=f"Error retrieving public health alerts: {str(e)}"
        )]

async def get_health_risk_trends(arguments: Dict[str, Any]) -> list[types.TextContent]:
    """
    Retrieve time series data for public health risk trends.
    """
    try:
        risk_types = arguments.get("risk_types", list(MOCK_RISK_TRENDS.keys()))
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        
        # Filter data based on requested risk types
        filtered_trends = {}
        for risk_type in risk_types:
            if risk_type in MOCK_RISK_TRENDS:
                trend_data = MOCK_RISK_TRENDS[risk_type].copy()
                
                # Filter data points by date range if provided
                if start_date or end_date:
                    filtered_points = []
                    for point in trend_data["data_points"]:
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
                    
                    trend_data["data_points"] = filtered_points
                
                filtered_trends[risk_type] = trend_data
        
        result = {
            "requested_risk_types": risk_types,
            "available_risk_types": list(MOCK_RISK_TRENDS.keys()),
            "date_range": {
                "start": start_date if start_date else "not specified",
                "end": end_date if end_date else "not specified"
            },
            "trends": filtered_trends,
            "metadata": {
                "data_source": "Mock Public Health Data",
                "last_updated": datetime.now().isoformat(),
                "total_trend_types": len(filtered_trends)
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error in get_health_risk_trends: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error retrieving health risk trends: {str(e)}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="public-health-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 