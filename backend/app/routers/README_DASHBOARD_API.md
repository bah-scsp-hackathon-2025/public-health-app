# Dashboard API Documentation

## Overview

The Dashboard API provides endpoints for generating comprehensive public health dashboards using AI-powered analysis. The system uses **Anthropic Claude** for intelligent analysis and integrates with epidemiological data sources through MCP (Model Context Protocol) servers.

### Enhanced Structured Data

All endpoints now return both human-readable dashboard summaries and structured data for programmatic use:

- **`alerts`**: Detailed alert information with priority scoring and risk assessment
- **`rising_trends`**: Statistical trend analysis with significance indicators  
- **`epidemiological_signals`**: Real-time health indicators from multiple data sources
- **`risk_assessment`**: Overall risk evaluation with confidence levels
- **`recommendations`**: Actionable recommendations with priority and target audience

This dual approach provides both executive-level summaries and machine-readable data for integration into other systems.

**Getting Counts**: Alert and trend counts can be derived from the array lengths:
```javascript
const alertsCount = response.alerts.length;
const trendsCount = response.rising_trends.length;
const signalsCount = response.epidemiological_signals.length;
```

## Base URL

```
http://localhost:8000/dashboard
```

## Request/Response Models

### DashboardRequest

```json
{
    "query": "Generate comprehensive public health dashboard for current situation",
    "agent_type": "react"  // optional: "standard" or "react"
}
```

### DashboardResponse

```json
{
    "success": true,
    "dashboard_summary": "📊 **PUBLIC HEALTH DASHBOARD SUMMARY**...",
    "timestamp": "2024-01-15T10:30:00Z",
    "error": null,
    "generation_time_seconds": 12.5,
    "agent_type": "react",
    "tools_used": ["fetch_epi_signal", "detect_rising_trend"],
    
    // Enhanced structured data (populated with actual data)
    "alerts": [
        {
            "id": "alert_001",
            "title": "COVID-19 Outbreak Alert",
            "severity": "HIGH",
            "state": "CA",
            "affected_population": 45000,
            "analysis": {
                "priority_score": 85,
                "risk_level": "high"
            }
        }
    ],
    "rising_trends": [
        {
            "signal_name": "confirmed_7dav_incidence_prop",
            "trend_direction": "rising",
            "rising_periods": 3,
            "risk_level": "medium"
        }
    ],
    "epidemiological_signals": [
        {
            "signal_name": "smoothed_wcli",
            "display_name": "COVID-Like Symptoms",
            "trend_direction": "rising",
            "data_source": "delphi_epidata_api"
        }
    ],
    "risk_assessment": {
        "overall_risk_level": "medium",
        "confidence_level": "high",
        "geographic_distribution": "regional"
    },
    "recommendations": [
        {
            "priority": "high",
            "action": "Enhance surveillance in affected areas",
            "target_audience": "Public Health Officials"
        }
    ]
}
```

### DashboardStatus

```json
{
    "agent_available": true,
    "mcp_server_accessible": true,
    "anthropic_api_available": true,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoints

### 1. Generate Dashboard

**POST** `/generate`

Generate a customized public health dashboard.

**Request Body:**
```json
{
    "query": "Focus on high severity alerts in California and trending health metrics",
    "agent_type": "react"
}
```

**Response:**
```json
{
    "success": true,
    "dashboard_summary": "📊 **PUBLIC HEALTH DASHBOARD SUMMARY**\n\n🚨 **CURRENT SITUATION**...",
    "timestamp": "2024-01-15T10:30:00Z",
    "generation_time_seconds": 15.3,
    "agent_type": "react",
    "alerts": [
        {
            "id": "alert_001",
            "title": "High Severity Health Alert",
            "severity": "HIGH",
            "state": "CA",
            "affected_population": 50000,
            "analysis": {
                "priority_score": 90,
                "risk_level": "critical"
            }
        }
    ],
    "rising_trends": [
        {
            "signal_name": "respiratory_visits",
            "trend_direction": "rising",
            "risk_level": "high"
        }
    ],
    "risk_assessment": {
        "overall_risk_level": "high",
        "geographic_distribution": "regional"
    },
    "recommendations": [
        {
            "priority": "urgent",
            "action": "Deploy additional testing resources"
        }
    ]
}
```

### 2. Dashboard Status

**GET** `/status`

Check the status of dashboard generation services.

**Response:**
```json
{
    "agent_available": true,
    "mcp_server_accessible": true,
    "anthropic_api_available": true,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Alerts Summary

**GET** `/alerts-summary`

Generate a dashboard focused specifically on current alerts.

**Response:** Same as `/generate` but focused on alerts.

### 4. Trends Summary

**GET** `/trends-summary`

Generate a dashboard focused on health risk trends over time.

**Response:** Same as `/generate` but focused on trends.

### 5. Emergency Summary

**GET** `/emergency-summary`

Generate a dashboard optimized for emergency response scenarios.

**Response:** Same as `/generate` but with emergency focus.

### 6. Epidemiological Analysis

**POST** `/epidemiological-analysis`

Generate comprehensive epidemiological analysis using the ReAct agent with real-time data.

**Request Body:**
```json
{
    "query": "Analyze recent COVID-19 trends and hospital capacity nationwide",
    "agent_type": "react"
}
```

**Response:**
```json
{
    "success": true,
    "dashboard_summary": "🔬 **EPIDEMIOLOGICAL ANALYSIS**...",
    "timestamp": "2024-01-15T10:30:00Z",
    "generation_time_seconds": 45.2,
    "agent_type": "ReAct-Epidemiological",
    "tools_used": ["fetch_epi_signal", "detect_rising_trend"],
    "epidemiological_signals": [...],
    "rising_trends": [...],
    "risk_assessment": {...}
}
```

### 7. Async Generation

**POST** `/generate/async`

Start dashboard generation as a background task.

**Request Body:** Same as `/generate`

**Response:**
```json
{
    "message": "Dashboard generation started in background",
    "task_id": "dashboard_20240115_103000",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Agent Types

### Standard Agent
- **Type:** `"standard"`
- **Description:** Uses LangGraph workflow for structured data processing
- **Best for:** General dashboard generation, alert analysis, basic trending
- **Features:** Sample data integration, enhanced analytics, structured responses

### ReAct Agent  
- **Type:** `"react"`
- **Description:** Uses ReAct pattern with real-time epidemiological tools
- **Best for:** Real-time epidemiological analysis, statistical trend detection
- **Features:** Live API integration, statistical analysis, evidence-based insights

## Configuration

### Environment Variables

```bash
# Required for AI analysis
ANTHROPIC_API_KEY=sk-ant-...

# MCP Server Configuration
MCP_SERVER_HOST=localhost  # Default: localhost
MCP_SERVER_PORT=8000      # Default: 8000
```

### Agent Configuration

Both agents now use **Anthropic Claude Sonnet 4.0** with thinking mode for enhanced reasoning capabilities. MCP server connection settings are configured through environment variables only.

## Error Handling

All endpoints return structured error responses:

```json
{
    "success": false,
    "error": "Dashboard generation failed: Connection timeout",
    "timestamp": "2024-01-15T10:30:00Z",
    "generation_time_seconds": 5.0
}
```

## Integration Examples

### Python Client

```python
import requests

# Generate standard dashboard
response = requests.post(
    "http://localhost:8000/dashboard/generate",
    json={
        "query": "Emergency response dashboard for wildfire areas",
        "agent_type": "react"
    }
)

result = response.json()
if result["success"]:
    print(result["dashboard_summary"])
```

### JavaScript/Frontend

```javascript
const generateDashboard = async (query) => {
    const response = await fetch('/dashboard/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: query,
            agent_type: 'standard'
        })
    });
    
    const result = await response.json();
    return result;
};
```

### cURL

```bash
# Generate epidemiological analysis
curl -X POST http://localhost:8000/dashboard/epidemiological-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze COVID trends in the Pacific Northwest",
    "agent_type": "react"
  }'
```

## Performance Notes

- **Standard Agent:** Typically 10-20 seconds for full dashboard
- **ReAct Agent:** 30-60 seconds due to real-time data fetching and analysis
- **Async Generation:** Use for long-running requests to avoid timeouts
- **Caching:** Consider implementing caching for frequently requested dashboards

## Troubleshooting

### Common Issues

1. **"Agent not available"**
   - Check Anthropic API key is set
   - Verify API key has sufficient credits

2. **"MCP server not accessible"**
   - Ensure MCP server is running on configured port
   - Check network connectivity to MCP server

3. **"Generation timeout"**
   - Use async endpoint for complex requests
   - Check system resources and API rate limits

### Debug Mode

Set `DEBUG=1` environment variable for detailed logging:

```bash
DEBUG=1 uvicorn app.main:app --port 8000
``` 