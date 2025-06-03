# Public Health MCP Server

This MCP (Model Context Protocol) server provides tools for accessing public health data including alerts and risk trends.

## Overview

The server currently provides two main tools:

1. **get_public_health_alerts** - Retrieves public health alerts with filtering capabilities
2. **get_health_risk_trends** - Returns time series data for public health risk trends

## Features

### Public Health Alerts Tool
- Filters by date range (start_date, end_date)
- Filters by states (e.g., CA, NY, TX)
- Filters by severity (LOW, MEDIUM, HIGH)
- Sorts by timestamp (most recent first)
- Configurable result limits

### Health Risk Trends Tool
- Multiple risk trend types:
  - COVID-19 doctor visits
  - Flu symptom searches
  - ICU bed occupation rates
  - Respiratory emergency visits
- Time series data with percentage changes
- Date range filtering
- Multiple trend types in single request

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the server executable:
```bash
chmod +x mcp_public_health.py
```

## Usage

### Running the Server

```bash
python mcp_public_health.py
```

The server runs using stdin/stdout streams for MCP communication.

### Tool Examples

#### Get Public Health Alerts

**Get recent alerts (default):**
```json
{
  "name": "get_public_health_alerts",
  "arguments": {}
}
```

**Filter by states and severity:**
```json
{
  "name": "get_public_health_alerts", 
  "arguments": {
    "states": ["CA", "NY"],
    "severity": "HIGH",
    "limit": 5
  }
}
```

**Filter by date range:**
```json
{
  "name": "get_public_health_alerts",
  "arguments": {
    "start_date": "2024-01-10T00:00:00Z",
    "end_date": "2024-01-15T23:59:59Z"
  }
}
```

#### Get Health Risk Trends

**Get all trends:**
```json
{
  "name": "get_health_risk_trends",
  "arguments": {}
}
```

**Get specific risk types:**
```json
{
  "name": "get_health_risk_trends",
  "arguments": {
    "risk_types": ["covid_doctor_visits", "icu_bed_occupation"]
  }
}
```

**Filter by date range:**
```json
{
  "name": "get_health_risk_trends",
  "arguments": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

## Data Structure

### Alert Response Format
```json
{
  "total_alerts": 3,
  "filters_applied": {
    "states": ["CA"],
    "severity": "HIGH", 
    "date_range": {
      "start": "2024-01-10T00:00:00Z",
      "end": "not specified"
    }
  },
  "alerts": [
    {
      "id": "alert_001",
      "title": "COVID-19 Outbreak in Downtown Area",
      "description": "...",
      "severity": "HIGH",
      "state": "CA",
      "county": "Los Angeles",
      "timestamp": "2024-01-15T14:30:00Z",
      "alert_type": "OUTBREAK",
      "affected_population": 15000,
      "source": "LA County Health Department"
    }
  ]
}
```

### Risk Trends Response Format
```json
{
  "requested_risk_types": ["covid_doctor_visits"],
  "available_risk_types": ["covid_doctor_visits", "symptom_searches", "icu_bed_occupation", "respiratory_emergency_visits"],
  "trends": {
    "covid_doctor_visits": {
      "name": "COVID-19 Doctor Visits",
      "description": "Weekly trend of COVID-19 related doctor visits",
      "unit": "visits_per_100k",
      "data_points": [
        {
          "date": "2024-01-01",
          "value": 45.2,
          "change_percent": -12.3
        }
      ]
    }
  },
  "metadata": {
    "data_source": "Mock Public Health Data",
    "last_updated": "2024-01-15T10:30:00Z",
    "total_trend_types": 1
  }
}
```

## Current Data

The server currently uses mock data for demonstration purposes. The mock data includes:

### Alert Types
- OUTBREAK (COVID-19, Norovirus)
- SEASONAL (Flu activity)
- FOOD_SAFETY (E. coli contamination)
- ENVIRONMENTAL (Air quality)

### Risk Trend Types
- **covid_doctor_visits**: Weekly COVID-19 related doctor visits
- **symptom_searches**: Search volume for flu-related symptoms
- **icu_bed_occupation**: ICU bed occupation percentage
- **respiratory_emergency_visits**: Emergency department visits for respiratory issues

## Configuration

The server configuration is defined in `config.json` and includes:
- Server metadata
- Tool descriptions
- Logging configuration
- Data source settings

## Development

### Adding New Alert Types
1. Add new alert objects to `MOCK_ALERTS` list
2. Follow the existing schema structure
3. Update documentation

### Adding New Risk Trends
1. Add new trend data to `MOCK_RISK_TRENDS` dictionary
2. Include data points with date, value, and change_percent
3. Update the tool schema enum values

### Extending Functionality
- Add new filtering options to existing tools
- Create additional tools for other public health data
- Implement real data source connections

## License

This project is part of the public health application suite. 