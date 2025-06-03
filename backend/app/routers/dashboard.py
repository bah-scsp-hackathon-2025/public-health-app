from typing import Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
import sys
import os
from datetime import datetime
import asyncio

# Add the necessary paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))  # Add backend dir
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'mcp'))  # Add mcp dir

# Import the agents using the correct path
from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent
from app.models.dashboard import DashboardRequest, DashboardResponse, DashboardStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest):
    """
    Generate a public health dashboard summary using the LangGraph agent.
    
    This endpoint creates a dashboard agent and uses it to:
    1. Fetch health alerts and trends from the MCP server
    2. Analyze the data for patterns and insights
    3. Generate comprehensive dashboard summaries
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
            
        # Generate the dashboard
        result = await agent.generate_dashboard(request.query)
        
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
            recommendations=result.get("recommendations")
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


@router.post("/generate/async")
async def generate_dashboard_async(request: DashboardRequest, background_tasks: BackgroundTasks):
    """
    Generate a dashboard asynchronously in the background.
    
    This endpoint starts dashboard generation as a background task and returns immediately.
    Use this for long-running dashboard generation that might take time.
    
    Note: This is a simple implementation. In production, you'd want to use
    a proper task queue (like Celery) and return a task ID for status checking.
    """
    task_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def generate_in_background():
        """Background task to generate dashboard"""
        try:
            if request.agent_type == "react":
                agent = PublicHealthReActAgent()
            else:
                agent = PublicHealthDashboardAgent()
            
            result = await agent.generate_dashboard(request.query)
            
            # In production, you'd store this result in a database or cache
            print(f"Background task {task_id} completed: {result.get('success', False)}")
            
        except Exception as e:
            print(f"Background task {task_id} failed: {str(e)}")
    
    background_tasks.add_task(generate_in_background)
    
    return {
        "message": "Dashboard generation started in background",
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    }


# Specific dashboard endpoints for common use cases
@router.get("/alerts-summary", response_model=DashboardResponse)
async def get_alerts_summary():
    """Generate a dashboard focused on current alerts only"""
    request = DashboardRequest(query="Focus on current public health alerts with high priority items")
    return await generate_dashboard(request)


@router.get("/trends-summary", response_model=DashboardResponse) 
async def get_trends_summary():
    """Generate a dashboard focused on health risk trends only"""
    request = DashboardRequest(query="Analyze health risk trends and patterns over time")
    return await generate_dashboard(request)


@router.get("/emergency-summary", response_model=DashboardResponse)
async def get_emergency_summary():
    """Generate a dashboard for emergency response scenarios"""
    request = DashboardRequest(query="Emergency response dashboard focusing on high-severity alerts and immediate action items")
    return await generate_dashboard(request)


@router.post("/epidemiological-analysis", response_model=DashboardResponse)
async def generate_epidemiological_analysis(request: DashboardRequest):
    """
    Generate epidemiological analysis using ReAct agent with real-time data from Delphi Epidata API.
    
    This endpoint uses the ReAct agent to:
    1. Fetch real-time epidemiological data (COVID cases, symptoms, doctor visits, etc.)
    2. Perform statistical trend analysis using rolling regression
    3. Cross-reference with public health alerts
    4. Generate comprehensive epidemiological intelligence
    
    The ReAct agent uses the fetch_epi_signal and detect_rising_trend tools for data-driven analysis.
    MCP server configuration is handled through environment variables.
    """
    start_time = datetime.now()
    
    try:
        # Force ReAct agent for this endpoint
        agent = PublicHealthReActAgent()
        
        # Create epidemiological-focused request
        epi_request = f"""
{request.query}

Focus on epidemiological surveillance and analysis:
1. Fetch recent COVID-19 case data, symptoms, and healthcare utilization
2. Analyze statistical trends and patterns using regression analysis
3. Cross-reference with current public health alerts
4. Provide data-driven intelligence for epidemiological decision-making

Emphasize real-time data analysis and statistical evidence.
"""
        
        # Generate the analysis
        result = await agent.generate_dashboard(epi_request)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Return the response with enhanced structured data
        return DashboardResponse(
            success=result.get("success", False),
            dashboard_summary=result.get("dashboard_summary"),
            timestamp=result.get("timestamp"),
            error=result.get("error"),
            generation_time_seconds=generation_time,
            agent_type="ReAct-Epidemiological",
            tools_used=result.get("tools_used"),
            
            # Enhanced structured data
            alerts=result.get("alerts"),
            rising_trends=result.get("rising_trends"),
            epidemiological_signals=result.get("epidemiological_signals"),
            risk_assessment=result.get("risk_assessment"),
            recommendations=result.get("recommendations")
        )
        
    except Exception as e:
        generation_time = (datetime.now() - start_time).total_seconds()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Epidemiological analysis failed: {str(e)}",
                "generation_time_seconds": generation_time,
                "timestamp": datetime.now().isoformat(),
                "agent_type": "ReAct-Epidemiological"
            }
        ) 