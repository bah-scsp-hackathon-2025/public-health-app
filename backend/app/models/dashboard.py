from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .trend import TrendResponse
from .alert import AlertCreate
from .strategy import StrategyCreate


class DashboardRequest(BaseModel):
    """Request model for dashboard generation"""
    start_date: Optional[str] = Field(
        default="2020-02-01",
        description="Start date for data analysis in YYYY-MM-DD format. If not provided, uses appropriate default period.",
        example="2020-02-01"
    )
    end_date: Optional[str] = Field(
        default="2022-02-01",
        description="End date for data analysis in YYYY-MM-DD format. If not provided, uses current date.",
        example="2022-02-01"
    )
    agent_type: Optional[str] = Field(
        default="react",
        description="Agent type to use: 'standard' for workflow-based agent or 'react' for ReAct agent with epidemiological tools",
        example="react"
    )


class DashboardResponse(BaseModel):
    """Response model for dashboard generation"""
    success: bool
    dashboard_summary: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    agent_type: Optional[str] = None
    tools_used: Optional[list] = None
    
    # Enhanced data fields
    alerts: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Actual alert data with analysis and recommendations"
    )
    rising_trends: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Detected rising trends from time series analysis"
    )
    epidemiological_signals: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Epidemiological signal data and analysis"
    )
    risk_assessment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Overall risk assessment based on data analysis"
    )
    recommendations: Optional[List[str]] = Field(
        default=None,
        description="Actionable recommendations based on analysis"
    )
    trends: Optional[List[TrendResponse]] = Field(
        default=None,
        description="Raw epidemiological data from successful fetch_epi_signal calls"
    )


class DashboardStatus(BaseModel):
    """Status model for checking dashboard generation status"""
    agent_available: bool
    mcp_server_accessible: bool
    anthropic_api_available: bool
    timestamp: str


class PolicyDraftRequest(BaseModel):
    """Request model for policy draft generation"""
    strategy: StrategyCreate = Field(
        description="The selected strategy to implement as a policy"
    )
    alert: AlertCreate = Field(
        description="The original alert that triggered the strategy"
    )
    author: Optional[str] = Field(
        default="AI Policy Generator",
        description="Author name for the policy draft"
    ) 