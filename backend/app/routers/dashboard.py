from fastapi import APIRouter, HTTPException, status
import sys
import os
from datetime import datetime
from typing import List

# Add the necessary paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))  # Add backend dir
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'mcp'))  # Add mcp dir

# Import the agents using the correct path
from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent
from app.agents.strategy_generation_agent import StrategyGenerationAgent
from app.models.dashboard import DashboardRequest, DashboardResponse, DashboardStatus
from app.models.alert import AlertCreate
from app.models.strategy import StrategyCreate

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/assemble", response_model=DashboardResponse)
async def assemble_dashboard(request: DashboardRequest):
    """
    Assemble a public health dashboard summary using the LangGraph agent.
    
    This endpoint creates a dashboard agent and uses it to:
    1. Fetch health alerts and trends from the MCP server
    2. Analyze the data for patterns and insights
    3. Assemble dashboard summary
    4. Provide actionable insights for public health officials
    
    The agent uses Anthropic Claude for enhanced reasoning and analysis.
    MCP server configuration is handled through environment variables.
    """
    start_time = datetime.now()
    
    try:
        # Choose agent type based on request
        if request.agent_type == "react":
            agent = PublicHealthReActAgent()
        else:
            agent = PublicHealthDashboardAgent()
            
        # Generate the dashboard with date parameters
        result = await agent.assemble_dashboard(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Return the response with enhanced structured data
        return DashboardResponse(
            success=result.get("success", False),
            dashboard_summary=result.get("dashboard_summary"),
            timestamp=result.get("timestamp"),
            error=result.get("error"),
            generation_time_seconds=generation_time,
            agent_type=result.get("agent_type", request.agent_type),
            tools_used=result.get("tools_used"),
            
            # Enhanced structured data
            alerts=result.get("alerts"),
            rising_trends=result.get("rising_trends"),
            epidemiological_signals=result.get("epidemiological_signals"),
            risk_assessment=result.get("risk_assessment"),
            recommendations=result.get("recommendations"),
            trends=result.get("trends")
        )
        
    except Exception as e:
        generation_time = (datetime.now() - start_time).total_seconds()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Dashboard generation failed: {str(e)}",
                "generation_time_seconds": generation_time,
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/status", response_model=DashboardStatus)
async def get_dashboard_status():
    """
    Check the status of the dashboard agent and its dependencies.
    
    Returns information about:
    - Agent availability
    - MCP server accessibility  
    - Anthropic API availability
    - System timestamp
    """
    try:
        # Check if agent can be instantiated
        agent_available = True
        try:
            agent = PublicHealthDashboardAgent()
        except Exception:
            agent_available = False
        
        # Check MCP server accessibility
        mcp_server_accessible = False
        if agent_available:
            try:
                # Try to initialize MCP client
                await agent._init_mcp_client()
                mcp_server_accessible = True
            except Exception:
                mcp_server_accessible = False
        
        # Check Anthropic API availability
        from app.config import settings
        anthropic_api_available = bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-'))
        
        return DashboardStatus(
            agent_available=agent_available,
            mcp_server_accessible=mcp_server_accessible,
            anthropic_api_available=anthropic_api_available,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )


@router.post("/generate-strategies", response_model=List[StrategyCreate])
async def generate_strategies_from_alert(alert: AlertCreate):
    """
    Generate multiple strategy variations based on an alert using Claude with extended thinking.
    
    Takes an Alert model as input and generates at least four strategy variations with different 
    severity levels and approaches. Uses policy documents for context and compliance.
    
    The strategies will vary in:
    - Severity level (immediate, moderate, preventive, long-term)
    - Response approach (containment, mitigation, communication, resource allocation)
    - Target audience (public, healthcare workers, officials)
    """
    try:
        # Initialize the strategy generation agent
        agent = StrategyGenerationAgent()
        
        # Generate strategies using the agent
        strategies = await agent.generate_strategies(alert)
        
        return strategies
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation failed: {str(e)}"
        )


