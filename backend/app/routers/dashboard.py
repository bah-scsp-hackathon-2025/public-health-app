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

# Import the agent using the correct path
from app.agents.health_dashboard_agent import PublicHealthDashboardAgent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardRequest(BaseModel):
    """Request model for dashboard generation"""
    query: str = Field(
        default="Generate comprehensive public health dashboard for current situation",
        description="Natural language description of the dashboard requirements",
        example="Focus on high severity alerts in California"
    )
    llm_provider: Optional[str] = Field(
        default="auto",
        description="LLM provider to use: 'openai', 'anthropic', or 'auto' for auto-detection",
        example="openai"
    )
    mcp_host: Optional[str] = Field(
        default=None,
        description="MCP server host (defaults to environment variable or localhost)",
        example="localhost"
    )
    mcp_port: Optional[int] = Field(
        default=None,
        description="MCP server port (defaults to environment variable or 8000)",
        example=8000
    )


class DashboardResponse(BaseModel):
    """Response model for dashboard generation"""
    success: bool
    dashboard_summary: Optional[str] = None
    alerts_count: Optional[int] = None
    trends_count: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
    generation_time_seconds: Optional[float] = None


class DashboardStatus(BaseModel):
    """Status model for checking dashboard generation status"""
    agent_available: bool
    mcp_server_accessible: bool
    llm_providers: dict
    timestamp: str


@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest):
    """
    Generate a public health dashboard summary using the LangGraph agent.
    
    This endpoint creates a dashboard agent and uses it to:
    1. Fetch health alerts and trends from the MCP server
    2. Analyze the data for patterns and insights
    3. Generate comprehensive dashboard summaries
    4. Provide actionable insights for public health officials
    
    The agent supports multiple LLM providers and graceful degradation.
    """
    start_time = datetime.now()
    
    try:
        # Create the dashboard agent with provided configuration
        agent_kwargs = {}
        if request.llm_provider and request.llm_provider != "auto":
            agent_kwargs["llm_provider"] = request.llm_provider
        if request.mcp_host:
            agent_kwargs["mcp_host"] = request.mcp_host
        if request.mcp_port:
            agent_kwargs["mcp_port"] = request.mcp_port
            
        agent = PublicHealthDashboardAgent(**agent_kwargs)
        
        # Generate the dashboard
        result = await agent.generate_dashboard(request.query)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Return the response
        return DashboardResponse(
            success=result.get("success", False),
            dashboard_summary=result.get("dashboard_summary"),
            alerts_count=result.get("alerts_count"),
            trends_count=result.get("trends_count"),
            timestamp=result.get("timestamp"),
            error=result.get("error"),
            generation_time_seconds=generation_time
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
    - Available LLM providers
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
        
        # Check available LLM providers through settings
        from app.config import settings
        llm_providers = {
            "openai": bool(settings.openai_api_key and settings.openai_api_key.startswith('sk-')),
            "anthropic": bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-'))
        }
        
        return DashboardStatus(
            agent_available=agent_available,
            mcp_server_accessible=mcp_server_accessible,
            llm_providers=llm_providers,
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
            agent_kwargs = {}
            if request.llm_provider and request.llm_provider != "auto":
                agent_kwargs["llm_provider"] = request.llm_provider
            if request.mcp_host:
                agent_kwargs["mcp_host"] = request.mcp_host
            if request.mcp_port:
                agent_kwargs["mcp_port"] = request.mcp_port
                
            agent = PublicHealthDashboardAgent(**agent_kwargs)
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