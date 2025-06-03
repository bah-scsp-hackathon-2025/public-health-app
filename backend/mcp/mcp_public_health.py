#!/usr/bin/env python3
"""
FastMCP Public Health Server with SSE Transport

This server provides three tools:
1. fetch_epi_signal - Fetch specific COVID-19 signals from Delphi Epidata API
2. detect_rising_trend - Detect rising trends in time series data using rolling regression
3. get_server_info - Server information and capabilities

Uses FastMCP framework with SSE transport for improved developer experience.
"""

from datetime import datetime
from fastmcp import FastMCP
import pandas as pd
import numpy as np
from scipy.stats import linregress
import os
import tempfile
import logging
import json
import requests
# from load_dotenv import load_dotenv
# load_dotenv(".env")


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

@mcp.tool()
def fetch_epi_signal(
    signal: str,
    time_type: str,
    geo_type: str,
    start_time: str,
    end_time: str,
    as_json: bool = True
) -> json:
    """
    Fetch a specific COVID-19 signal from the EpiDataContext and return a JSON.
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
        Accepted values depend on geo_type:
        - "county": 5-digit FIPS codes (e.g., "06037" for Los Angeles County).
        - "hrr": Hospital Referral Region numbers (1-457).
        - "hhs": HHS region numbers (1-10).
        - "msa": Metropolitan Statistical Area codes (CBSA ID).
        - "dma": Nielsen Designated Market Area codes.
        - "state": 2-letter state codes (e.g., "ny", "ca", "dc", "pr").
        - "nation": ISO country code ("us" only).

    Returns:
        json: A JSON containing the fetched signal data, with additional metadata columns. 
    """
    BASE_URL = "https://api.delphi.cmu.edu/epidata/covidcast/"

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
    params = {
        "data_source": signal_to_source[signal],
        "signal": signal,
        "time_type": time_type,
        "geo_type": geo_type,
        "time_values": start_time + "-" + end_time,  # Combine start_time and end_time
        "as_of": end_time,  # Use the end_time as the 'as_of' date
        "geo_value": "*",
    }
    response = requests.get(BASE_URL, params=params, verify=False) # Disable SSL verification for testing purposes
    if as_json:
        response.raise_for_status()
        return response.json()
    

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
        # Get the last fetched data from temporary storage
        # For production, this would query the actual data source
        temp_dir = tempfile.gettempdir()
        csv_file = os.path.join(temp_dir, f"{signal_name}_data.csv")
        
        logger.debug(f"🔍 Looking for data file: {csv_file}")
        
        if not os.path.exists(csv_file):
            logger.warning(f"⚠️ No data file found for signal: {signal_name}")
            return {
                "rising_periods": [],
                "total_periods": 0,
                "sample_log_slopes": [],
                "status": "no_data",
                "message": f"No data available for signal: {signal_name}. Please fetch data first using fetch_epi_signal."
            }
        
        # Load the data
        df = pd.read_csv(csv_file)
        logger.debug(f"📊 Loaded data shape: {df.shape}")
        logger.debug(f"📊 Columns: {list(df.columns)}")
        
        if value_column not in df.columns:
            return {
                "rising_periods": [],
                "total_periods": 0,
                "sample_log_slopes": [],
                "status": "error",
                "message": f"Column '{value_column}' not found in data. Available columns: {list(df.columns)}"
            }
        
        if date_column not in df.columns:
            return {
                "rising_periods": [],
                "total_periods": 0,
                "sample_log_slopes": [],
                "status": "error", 
                "message": f"Date column '{date_column}' not found in data. Available columns: {list(df.columns)}"
            }
        
        # Convert date column to datetime
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Sort by date
        df = df.sort_values(date_column)
        
        # Remove rows with missing values
        df = df.dropna(subset=[value_column])
        
        if len(df) < window_size * 2:
            return {
                "rising_periods": [],
                "total_periods": 0,
                "sample_log_slopes": [],
                "status": "insufficient_data",
                "message": f"Not enough data points ({len(df)}) for analysis. Need at least {window_size * 2} points."
            }
        
        # Apply smoothing if requested
        if smooth:
            df[f'{value_column}_smoothed'] = df[value_column].rolling(window=3, center=True).mean()
            analysis_column = f'{value_column}_smoothed'
        else:
            analysis_column = value_column
        
        # Remove any zero or negative values for log transformation
        df = df[df[analysis_column] > 0]
        
        if len(df) < window_size * 2:
            return {
                "rising_periods": [],
                "total_periods": 0,
                "sample_log_slopes": [],
                "status": "insufficient_positive_data",
                "message": "Not enough positive data points for log-scale analysis."
            }
        
        # Apply log transformation
        df['log_values'] = np.log(df[analysis_column])
        
        # Calculate rolling regression slopes
        df['day_index'] = range(len(df))
        
        slopes = []
        rising_periods = []
        current_rising_start = None
        
        for i in range(window_size, len(df) - window_size + 1):
            # Get window data
            window_x = df['day_index'].iloc[i-window_size:i+window_size].values
            window_y = df['log_values'].iloc[i-window_size:i+window_size].values
            
            # Calculate linear regression
            try:
                slope, intercept, r_value, p_value, std_err = linregress(window_x, window_y)
                slopes.append(slope)
                
                # Check if this constitutes a rising trend
                is_rising = slope >= min_log_slope
                
                if is_rising and current_rising_start is None:
                    # Start of a new rising period
                    current_rising_start = df[date_column].iloc[i].strftime('%Y-%m-%d')
                elif not is_rising and current_rising_start is not None:
                    # End of current rising period
                    current_rising_end = df[date_column].iloc[i-1].strftime('%Y-%m-%d')
                    rising_periods.append((current_rising_start, current_rising_end))
                    current_rising_start = None
                    
            except Exception as reg_error:
                logger.warning(f"⚠️ Regression error at index {i}: {str(reg_error)}")
                continue
        
        # Handle case where data ends during a rising period
        if current_rising_start is not None:
            current_rising_end = df[date_column].iloc[-1].strftime('%Y-%m-%d')
            rising_periods.append((current_rising_start, current_rising_end))
        
        logger.debug(f"✅ Detected {len(rising_periods)} rising periods for {signal_name}")
        
        return {
            "rising_periods": rising_periods,
            "total_periods": len(rising_periods),
            "sample_log_slopes": slopes[-10:] if len(slopes) > 10 else slopes,  # Last 10 slopes as sample
            "status": "success",
            "analysis_details": {
                "window_size": window_size,
                "min_log_slope": min_log_slope,
                "smoothing_applied": smooth,
                "data_points_analyzed": len(df),
                "value_column": value_column,
                "date_column": date_column
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in detect_rising_trend: {str(e)}")
        return {
            "rising_periods": [],
            "total_periods": 0,
            "sample_log_slopes": [],
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
def get_server_info() -> dict:
    """
    Returns information about the FastMCP Public Health server and its capabilities.
    
    Returns:
        dict: Server information including version, capabilities, and available tools
    """
    return {
        "server_name": "Public Health FastMCP",
        "version": "1.9.2",
        "description": "FastMCP server providing epidemiological data analysis tools",
        "transport": "SSE (Server-Sent Events)",
        "capabilities": [
            "Epidemiological signal fetching from Delphi EpiData API",
            "Statistical trend detection using rolling regression",
            "Real-time data analysis and processing"
        ],
        "tools": ["fetch_epi_signal", "detect_rising_trend", "get_server_info"],
        "data_sources": [
            "Delphi EpiData API (COVID-19 signals)",
            "Real-time epidemiological surveillance data"
        ],
        "features": [
            "Type-safe tool definitions",
            "Comprehensive error handling", 
            "Debug logging support",
            "Flexible time and geographic filtering"
        ],
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run(transport="sse")
