#!/usr/bin/env python3
"""
FastMCP Public Health Server with SSE Transport

This server provides five tools:
1. get_public_health_alerts - Retrieves public health alerts with filtering options
2. get_health_risk_trends - Returns time series data for public health risk trends
3. fetch_epi_signal - Fetch specific COVID-19 signals from Delphi Epidata API
4. detect_rising_trend - Detect rising trends in time series data using rolling regression
5. get_server_info - Server information and capabilities

Uses FastMCP framework with SSE transport for improved developer experience.
"""

from typing import List, Optional, Literal
from datetime import datetime
from fastmcp import FastMCP
import pandas as pd
import numpy as np
from scipy.stats import linregress
from epidatpy import EpiDataContext, EpiRange
import os
import tempfile
import logging
import json

def setup_debug_logging():
    """Setup comprehensive debug logging for MCP server"""
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )
    
    # Set up specific loggers for debugging
    logger = logging.getLogger(__name__)
    fastmcp_logger = logging.getLogger("fastmcp")
    
    # Enable debug logging
    logger.setLevel(logging.DEBUG)
    fastmcp_logger.setLevel(logging.DEBUG)
    
    logger.debug("🔧 Debug logging enabled for MCP server")
    return logger

# Setup logging and get logger
logger = setup_debug_logging()

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
def fetch_epi_signal(
    signal: str,
    time_type: Literal["day", "week", "month"] = "day",
    geo_type: Literal["county", "hrr", "msa", "dma", "state"] = "state",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    geo_values: Optional[List[str]] = None
) -> str:
    """
    Fetch a specific COVID-19 signal from the EpiDataContext and save it to a CSV file.
    Args:
        signal (str): The specific signal to fetch. The options are: 
        - smoothed_wwearing_mask_7d. -> Description: People Wearing Masks
        - smoothed_wcovid_vaccinated_appointment_or_accept -> Description: Vaccine Acceptance.
        - sum_anosmia_ageusia_smoothed_search -> Description: COVID Symptom Searches on Google.
        - smoothed_wcli -> COVID-Like Symptoms
        - smoothed_whh_cmnty_cli -> Description: COVID-Like Symptoms in Community
        - smoothed_adj_cli -> Description: COVID-Related Doctor Visits
        - confirmed_7dav_incidence_prop -> Description: COVID Cases
        - confirmed_admissions_covid_1d_prop_7dav -> Description: COVID Hospital Admissions
        - deaths_7dav_incidence_prop -> Description: COVID Deaths

        time_type (Literal["day", "week", "month"]): The time granularity of the data.
        geo_type (Literal["state", "county", "hrr", "msa"]): The geographic granularity of the data.
        start_time (str, optional): The start time for the data query. Format: YYYYMMDD
        end_time (str, optional): The end time for the data query. Format: YYYYMMDD
        geo_values (List[str], optional): Geographic locations to fetch data for.
        Accepted values depend on geo_type:
        - "county": 5-digit FIPS codes (e.g., "06037" for Los Angeles County).
        - "hrr": Hospital Referral Region numbers (1-457).
        - "hhs": HHS region numbers (1-10).
        - "msa": Metropolitan Statistical Area codes (CBSA ID).
        - "dma": Nielsen Designated Market Area codes.
        - "state": 2-letter state codes (e.g., "ny", "ca", "dc", "pr").
        - "nation": ISO country code ("us" only).

    Returns:
        json: A JSON converted DataFrame containing the fetched signal data, with additional metadata columns. 
    """

    logger.debug(f"🔍 Fetching epidemiological signal: {signal}")
    logger.debug(f"Parameters: time_type={time_type}, geo_type={geo_type}, start_time={start_time}, end_time={end_time}")
    if geo_values:
        logger.debug(f"Geographic values: {geo_values}")

    signal_to_source = {
        "smoothed_wwearing_mask_7d": "fb-survey",
        "smoothed_wcovid_vaccinated_appointment_or_accept": "fb-survey",
        "smoothed_wcli": "fb-survey",
        "smoothed_whh_cmnty_cli": "fb-survey",
        "sum_anosmia_ageusia_smoothed_search": "google-symptoms",
        "smoothed_adj_cli": "doctor-visits",
        "deaths_7dav_incidence_prop": "doctor-visits",
        "confirmed_7dav_incidence_prop": "jhu-csse",
        "confirmed_admissions_covid_1d_prop_7dav": "hhs"
    }

    try:
        # Validate signal
        if signal not in signal_to_source:
            logger.warning(f"❌ Invalid signal requested: {signal}")
            return json.dumps({
                "error": f"Invalid signal: {signal}",
                "available_signals": list(signal_to_source.keys())
            })
        
        logger.debug(f"✅ Signal validated: {signal} -> {signal_to_source[signal]}")
        
        # Create time range
        time_values = EpiRange(start_time, end_time) if start_time or end_time else None
        if time_values:
            logger.debug(f"⏰ Time range: {time_values}")
        
        # Initialize EpiData client
        logger.debug("🔄 Initializing EpiData client with cache")
        epidata = EpiDataContext(use_cache=True, cache_max_age_days=7)
        
        # Fetch data
        logger.debug(f"📊 Fetching data for signal: {signal}")
        apicall = epidata.pub_covidcast(
            data_source=signal_to_source[signal],
            signals=[signal],  # signals expects a list
            time_type=time_type,
            geo_type=geo_type,
            time_values=time_values,
            geo_values=geo_values
        )
        
        df = apicall.df()
        logger.debug(f"✅ Retrieved {len(df)} data points")
        
        # Add metadata columns
        df["signal"] = signal
        df["source"] = signal_to_source[signal]
        df["time_type"] = time_type
        df["geo_type"] = geo_type
        
        # Save to temporary CSV for trend analysis
        csv_path = f"{tempfile.gettempdir()}/{signal}.csv"
        df.to_csv(csv_path, index=False)
        logger.debug(f"💾 Saved data to temporary CSV: {csv_path}")
        
        # Return JSON string
        result = df.to_json(orient="records")
        logger.debug("✅ Successfully converted data to JSON")
        return result
                
    except Exception as e:
        logger.error(f"❌ Error fetching signal {signal}: {str(e)}", exc_info=True)
        return json.dumps({
            "error": f"Failed to fetch signal {signal}: {str(e)}",
            "signal": signal
        })


# Tool to detect rising trends in time series data using rolling linear regression
@mcp.tool()
def detect_rising_trend(
    signal_name: str,
    value_column: str,
    date_column: str = "time_value",
    window_size: int = 7,
    min_log_slope: float = 0.01,
    smooth: bool = True
) -> dict:
    """
    Detects rising trends in a time series using rolling linear regression on the log-transformed values.

    Args:
        signal_name (str): Name of the signal to detect rising trends for. The fetch_epi_signal must be called for that signal for prefetching the data. The options are: 
        - smoothed_wwearing_mask_7d. -> Description: People Wearing Masks
        - smoothed_wcovid_vaccinated_appointment_or_accept -> Description: Vaccine Acceptance.
        - sum_anosmia_ageusia_smoothed_search -> Description: COVID Symptom Searches on Google.
        - smoothed_wcli -> COVID-Like Symptoms
        - smoothed_whh_cmnty_cli -> Description: COVID-Like Symptoms in Community
        - smoothed_adj_cli -> Description: COVID-Related Doctor Visits
        - confirmed_7dav_incidence_prop -> Description: COVID Cases
        - confirmed_admissions_covid_1d_prop_7dav -> Description: COVID Hospital Admissions
        - deaths_7dav_incidence_prop -> Description: COVID Deaths
        value_column (str): Column with numeric values to analyze.
        date_column (str, optional): Column with date values (default: "time_value").
        window_size (int, optional): Size of the rolling window (in time steps).
        min_log_slope (float, optional): Minimum slope (on log scale) to qualify as rising trend.
        smooth (bool, optional): Whether to apply a 3-day rolling average before log transform.

    Returns:
        dict: {
            "rising_periods": List of (start_date, end_date),
            "total_periods": int,
            "sample_log_slopes": List[float],
            "status": "success"
        }
    """
    try:
        csv_path = f"{tempfile.gettempdir()}/{signal_name}.csv"
        
        # Check if CSV file exists
        if not os.path.exists(csv_path):
            return {
                "error": f"CSV file for signal {signal_name} not found. Please fetch the signal first using fetch_epi_signal.",
                "status": "error"
            }
        
        df = pd.read_csv(csv_path)
        
        # Validate columns exist
        if date_column not in df.columns:
            return {
                "error": f"Date column '{date_column}' not found. Available columns: {list(df.columns)}",
                "status": "error"
            }
        
        if value_column not in df.columns:
            return {
                "error": f"Value column '{value_column}' not found. Available columns: {list(df.columns)}",
                "status": "error"
            }
        
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column).dropna(subset=[value_column])

        # Ensure strictly positive for log transform
        df = df[df[value_column] > 0]
        
        if len(df) < window_size:
            return {
                "error": f"Not enough data points ({len(df)}) for window size ({window_size})",
                "status": "error"
            }

        if smooth:
            df["smoothed"] = df[value_column].rolling(window=3, center=True).mean()
            series = df["smoothed"].dropna()
            dates = df[df["smoothed"].notna()][date_column].tolist()
        else:
            series = df[value_column]
            dates = df[date_column].tolist()

        log_series = np.log(series)
        log_slopes = []
        rising_periods = []

        for i in range(len(log_series) - window_size + 1):
            y = log_series.iloc[i:i + window_size] if hasattr(log_series, 'iloc') else log_series[i:i + window_size]
            x = list(range(window_size))
            if pd.isna(y).any():
                continue
            slope, _, _, _, _ = linregress(x, y)
            log_slopes.append(slope)

            if slope >= min_log_slope:
                start = dates[i]
                end = dates[i + window_size - 1]
                rising_periods.append((str(start.date()), str(end.date())))

        return {
            "status": "success",
            "rising_periods": rising_periods,
            "total_periods": len(rising_periods),
            "sample_log_slopes": log_slopes[:5],
            "data_points_analyzed": len(log_series),
            "window_size": window_size
        }
        
    except Exception as e:
        return {
            "error": f"Failed to detect trends for signal {signal_name}: {str(e)}",
            "status": "error"
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
            "tools": ["get_public_health_alerts", "get_health_risk_trends", "fetch_epi_signal", "detect_rising_trend", "get_server_info"],
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