#!/usr/bin/env python3
"""
FastMCP Public Health Server with SSE Transport

This server provides three tools:
1. get_public_health_alerts - Retrieves public health alerts with filtering options
2. get_health_risk_trends - Returns time series data for public health risk trends
3. get_server_info - Server information and capabilities

Uses FastMCP framework with SSE transport for improved developer experience.
"""

from datetime import datetime
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange
from fastmcp import FastMCP
from typing import List, Optional, Literal

# Create the MCP server with SSE transport
mcp = FastMCP("Public Health FastMCP")

# Complete mock data for public health alerts
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

# Complete mock data for health risk trends
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
    
    # Filter by date range if provided - robust datetime handling
    if start_date:
        try:
            # Convert all timestamps to naive datetime for comparison
            def parse_datetime_naive(dt_str):
                """Parse datetime string and ensure it's timezone-naive"""
                if dt_str.endswith('Z'):
                    # UTC timezone
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).replace(tzinfo=None)
                elif 'T' in dt_str and dt_str.find('+') == -1 and dt_str.find('Z') == -1:
                    # Naive datetime with T separator
                    return datetime.fromisoformat(dt_str)
                else:
                    # Try to parse as-is and make naive
                    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    return dt.replace(tzinfo=None) if dt.tzinfo else dt
            
            start_dt = parse_datetime_naive(start_date)
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if parse_datetime_naive(alert["timestamp"]) >= start_dt
            ]
        except (ValueError, TypeError) as e:
            # Invalid date format, skip filtering
            print(f"Warning: Could not parse start_date '{start_date}': {e}")
            pass
    
    if end_date:
        try:
            def parse_datetime_naive(dt_str):
                """Parse datetime string and ensure it's timezone-naive"""
                if dt_str.endswith('Z'):
                    # UTC timezone
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).replace(tzinfo=None)
                elif 'T' in dt_str and dt_str.find('+') == -1 and dt_str.find('Z') == -1:
                    # Naive datetime with T separator
                    return datetime.fromisoformat(dt_str)
                else:
                    # Try to parse as-is and make naive
                    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    return dt.replace(tzinfo=None) if dt.tzinfo else dt
            
            end_dt = parse_datetime_naive(end_date)
            filtered_alerts = [
                alert for alert in filtered_alerts 
                if parse_datetime_naive(alert["timestamp"]) <= end_dt
            ]
        except (ValueError, TypeError) as e:
            # Invalid date format, skip filtering
            print(f"Warning: Could not parse end_date '{end_date}': {e}")
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
    data_source: str,
    signal: List[str],
    time_type: Literal["day", "week", "month"] = "day",
    geo_type: Literal["county", "hrr", "msa", "dma", "state"] = "state",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    geo_values: Optional[List[str]] = None
) -> dict:
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
        start_time (Optional[str]): The start time for the data query. Format: YYYYMMDD
        end_time (Optional[str]): The end time for the data query. Format: YYYYMMDD
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
        pd.DataFrame: A DataFrame containing the fetched signal data, with additional metadata columns. 
    """

    # Logic to map signal to data source
    ALLOWED_SIGNALS = {
    "fb-survey": [
        "smoothed_wwearing_mask_7d",
        "smoothed_wcovid_vaccinated_appointment_or_accept",
        "smoothed_wcli",
        "smoothed_whh_cmnty_cli"
    ],
    "google-symptoms": [
        "sum_anosmia_ageusia_smoothed_search"
    ],
    "doctor-visits": [
        "smoothed_adj_cli",
        "deaths_7dav_incidence_prop"
    ],
    "jhu-csse": [
        "confirmed_7dav_incidence_prop"
    ],
    "hhs": [
        "confirmed_admissions_covid_1d_prop_7dav"
    ]
    }

    # Inverted mapping: signal -> data_source
    SIGNAL_TO_SOURCE = {
        signal: source
        for source, signals in ALLOWED_SIGNALS.items()
        for signal in signals
    }

    time_values = EpiRange(start_time, end_time)
    epidata = EpiDataContext(use_cache=True, cache_max_age_days=7)
    apicall = epidata.pub_covidcast(
        data_source=source,
        signals=signal,
        time_type=time_type,
        geo_type=geo_type,
        time_values=time_range,
        geo_values=geo_values
    )
    df = apicall.df()
    df["signal"] = signal
    df["source"] = source
    df["time_type"] = time_type
    df["geo_type"] = geo_type
    df["time_values"] = time_values
    df["geo_values"] = geo_values
    df.to_csv(f"{self.cache_dir}/{signal}.csv", index=False)
    return df.to_json(orient="records")
     # TO DO: Serialize the df?
    # def fetch(self):
    #     all_data = []
    #     for entry in tqdm(DELTA_SIGNALS, desc="Fetching signals"):
    #         data = self.fetch_signal(entry["source"], entry["signal"])
    #         all_data.append(data)
    #     return pd.concat(all_data, ignore_index=True)

    # def list_signals(self):
    #     return [entry["signal"] for entry in DELTA_SIGNALS]


# Tool to detect rising trends in time series data using rolling linear regression
@mcp.tool()
def detect_rising_trend(
    csv_path: str,
    value_column: str,
    date_column: str = "time_value",
    window_size: int = 7,
    min_log_slope: float = 0.01,
    smooth: bool = True
) -> dict:
    """
    Detects rising trends in a time series using rolling linear regression on the log-transformed values.

    Args:
        csv_path (str): Path to the time series CSV file.
        value_column (str): Column with numeric values to analyze.
        date_column (str): Column with date values (default: "time_value").
        window_size (int): Size of the rolling window (in time steps).
        min_log_slope (float): Minimum slope (on log scale) to qualify as rising trend.
        smooth (bool): Whether to apply a 3-day rolling average before log transform.

    Returns:
        dict: {
            "rising_periods": List of (start_date, end_date),
            "total_periods": int,
            "sample_log_slopes": List[float],
            "status": "success"
        }
    """
    df = pd.read_csv(csv_path)
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column).dropna(subset=[value_column])

    # Ensure strictly positive for log transform
    df = df[df[value_column] > 0]

    if smooth:
        df["smoothed"] = df[value_column].rolling(window=3, center=True).mean()
        series = df["smoothed"]
    else:
        series = df[value_column]

    log_series = np.log(series)
    dates = df[date_column].tolist()
    log_slopes = []
    rising_periods = []

    for i in range(len(log_series) - window_size + 1):
        y = log_series[i:i + window_size]
        x = list(range(window_size))
        if y.isnull().any():
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
        "sample_log_slopes": log_slopes[:5]
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