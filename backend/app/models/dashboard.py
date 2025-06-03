from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DashboardRequest(BaseModel):
    """Request model for dashboard generation"""
    query: str = Field(
        default="Generate comprehensive public health dashboard for current situation",
        description="Natural language description of the dashboard requirements",
        example="Focus on high severity alerts in California"
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


class DashboardStatus(BaseModel):
    """Status model for checking dashboard generation status"""
    agent_available: bool
    mcp_server_accessible: bool
    anthropic_api_available: bool
    timestamp: str 