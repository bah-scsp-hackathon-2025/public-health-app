#!/usr/bin/env python3
"""
Public Health Dashboard Agent using LangGraph

This agent workflow uses the FastMCP Public Health server to:
1. Fetch public health alerts and risk trends
2. Analyze the data for patterns and insights
3. Generate comprehensive dashboard summaries
4. Provide actionable insights for public health officials

The agent demonstrates real-world usage of MCP servers with LangGraph.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from operator import add
from typing import Dict, List, Optional, TypedDict, Annotated

# Load configuration from settings
from ..config import settings

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip
    pass

# Configure logging for LangGraph debugging
def setup_debug_logging():
    """Setup comprehensive debug logging for LangGraph execution"""
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )
    
    # Set up specific loggers for debugging
    logger = logging.getLogger(__name__)
    langgraph_logger = logging.getLogger("langgraph")
    langchain_logger = logging.getLogger("langchain")
    
    # Enable debug logging for LangGraph components
    logger.setLevel(logging.DEBUG)
    langgraph_logger.setLevel(logging.DEBUG)
    langchain_logger.setLevel(logging.DEBUG)
    
    # Enable debug for other relevant components
    logging.getLogger("langchain_core").setLevel(logging.DEBUG)
    logging.getLogger("langchain_mcp_adapters").setLevel(logging.DEBUG)
    
    logger.debug("🔧 Debug logging enabled for LangGraph workflow")
    return logger

# Setup logging and get logger
logger = setup_debug_logging()

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

# Langfuse imports
from langfuse.callback import CallbackHandler


# State management for the agent workflow
class DashboardState(TypedDict):
    messages: Annotated[List, add]
    current_request: Optional[str]
    alerts_data: Optional[Dict]
    trends_data: Optional[Dict]
    analysis_result: Optional[Dict]
    dashboard_summary: Optional[str]
    error_message: Optional[str]
    timestamp: str



class PublicHealthDashboardAgent:
    """LangGraph agent for public health dashboard generation"""
    
    def __init__(self):
        # Initialize MCP client
        self.mcp_client = None
        
        # Initialize Langfuse callback handler
        self.langfuse_handler = None

        # Initialize Langfuse tracing if configured
        self._setup_langfuse_tracing()
        # Load MCP configuration from environment variables
        self.mcp_host = settings.mcp_server_host if hasattr(settings, 'mcp_server_host') else os.getenv("MCP_SERVER_HOST", "localhost")
        self.mcp_port = int(settings.mcp_server_port if hasattr(settings, 'mcp_server_port') else os.getenv("MCP_SERVER_PORT", "8000"))
        
        # Get API keys from settings (keep both for future use)
        openai_key = settings.openai_api_key if settings.openai_api_key else None
        anthropic_key = settings.anthropic_api_key if settings.anthropic_api_key else None
        
        # Initialize with Anthropic/Claude
        self.llm = None
        if anthropic_key and anthropic_key.startswith('sk-ant-'):
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=1.0,
                max_tokens=64000,  # Must be greater than thinking.budget_tokens
                thinking={"type": "enabled", "budget_tokens": 8000},
                betas=["extended-cache-ttl-2025-04-11", "files-api-2025-04-14"],
                api_key=anthropic_key
            )
        else:
            print("⚠️  Anthropic API key not found or invalid. Agent will work in MCP-only mode.")
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _setup_langfuse_tracing(self):
        """Configure Langfuse tracing for workflow observability"""
        try:
            langfuse_secret_key = settings.langfuse_secret_key if hasattr(settings, 'langfuse_secret_key') else os.getenv("LANGFUSE_SECRET_KEY")
            langfuse_public_key = settings.langfuse_public_key if hasattr(settings, 'langfuse_public_key') else os.getenv("LANGFUSE_PUBLIC_KEY")
            langfuse_host = settings.langfuse_host if hasattr(settings, 'langfuse_host') else os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if langfuse_secret_key and langfuse_public_key and (settings.langfuse_tracing if hasattr(settings, 'langfuse_tracing') else os.getenv("LANGFUSE_TRACING", "true").lower() == "true"):
                self.langfuse_handler = CallbackHandler(
                    secret_key=langfuse_secret_key,
                    public_key=langfuse_public_key,
                    host=langfuse_host,
                    session_id=f"standard-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    user_id="public-health-system",
                    metadata={
                        "agent_type": "standard",
                        "project": settings.langfuse_project if hasattr(settings, 'langfuse_project') else "public-health-dashboard",
                        "environment": "production"
                    }
                )
                logger.info(f"✅ Langfuse tracing enabled for project: {settings.langfuse_project if hasattr(settings, 'langfuse_project') else 'public-health-dashboard'}")
            else:
                logger.info("ℹ️  Langfuse tracing disabled (missing keys or tracing disabled)")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup Langfuse tracing: {str(e)}")
            self.langfuse_handler = None
    
    async def _init_mcp_client(self):
        """Initialize MCP client connection"""
        if not self.mcp_client:
            client_config = {
                "public-health-fastmcp": {
                    "url": f"http://{self.mcp_host}:{self.mcp_port}/sse",
                    "transport": "sse",
                }
            }
            self.mcp_client = MultiServerMCPClient(client_config)
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(DashboardState)
        
        # Add nodes
        workflow.add_node("fetch_health_data", self._fetch_health_data_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("generate_summary", self._generate_summary_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow flow
        workflow.set_entry_point("fetch_health_data")
        
        workflow.add_conditional_edges(
            "fetch_health_data",
            self._should_handle_error,
            {
                "continue": "analyze_data",
                "error": "error_handler"
            }
        )
        workflow.add_edge("generate_summary", END)
        workflow.add_edge("error_handler", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "analyze_data",
            self._should_handle_error,
            {
                "continue": "generate_summary",
                "error": "error_handler"
            }
        )
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _should_handle_error(self, state: DashboardState) -> str:
        """Determine if we should handle an error"""
        if state.get("error_message"):
            return "error"
        return "continue"
    
    async def _fetch_health_data_node(self, state: DashboardState) -> DashboardState:
        """Fetch health alerts and trends from MCP server"""
        logger.debug("🚀 WORKFLOW NODE: Starting _fetch_health_data_node")
        logger.debug(f"Input state keys: {list(state.keys())}")
        
        try:
            logger.debug("Initializing MCP client connection...")
            await self._init_mcp_client()
            
            # Get available tools
            logger.debug("Fetching available MCP tools...")
            tools = await self.mcp_client.get_tools()
            logger.debug(f"Available tools: {[t.name for t in tools]}")
            
            # Note: The MCP server no longer provides get_public_health_alerts and get_health_risk_trends
            # We'll use mock data for basic functionality while the real focus is on epidemiological signals
            
            # Create basic mock data for demonstration purposes
            logger.info("🔍 Using mock health data for basic dashboard functionality...")
            
            alerts_data = {
                "total_alerts": 3,
                "alerts": [
                    {
                        "id": "alert_001",
                        "title": "Sample Health Alert - Monitor for Updates",
                        "description": "This is a sample alert for demonstration purposes. Real alerts would come from public health APIs.",
                        "severity": "MEDIUM",
                        "state": "CA",
                        "county": "Sample County",
                        "timestamp": "2021-01-15T14:30:00Z",
                        "alert_type": "MONITORING",
                        "affected_population": 10000,
                        "source": "Sample Health Department"
                    },
                    {
                        "id": "alert_002",
                        "title": "Health Surveillance Update",
                        "description": "Routine health surveillance data collection is ongoing. No immediate concerns identified.",
                        "severity": "LOW",
                        "state": "NY",
                        "county": "Sample County",
                        "timestamp": "2021-01-14T09:15:00Z",
                        "alert_type": "SURVEILLANCE",
                        "affected_population": 25000,
                        "source": "Sample Health Network"
                    },
                    {
                        "id": "alert_003",
                        "title": "Seasonal Health Advisory",
                        "description": "Standard seasonal health precautions recommended. Monitor epidemiological signals for changes.",
                        "severity": "LOW",
                        "state": "TX",
                        "county": "Sample County",
                        "timestamp": "2021-01-13T16:45:00Z",
                        "alert_type": "SEASONAL",
                        "affected_population": 15000,
                        "source": "Sample Health Services"
                    }
                ],
                "metadata": {
                    "note": "Mock data for demonstration. Real implementation would use epidemiological APIs.",
                    "data_source": "sample_data"
                }
            }
            
            trends_data = {
                "trends": {
                    "epidemiological_monitoring": {
                        "name": "Epidemiological Signal Monitoring",
                        "description": "Monitoring of epidemiological signals through API integration",
                        "unit": "signal_index",
                        "data_points": [
                            {"date": "2021-01-01", "value": 45.2, "change_percent": -2.3},
                            {"date": "2021-01-08", "value": 47.1, "change_percent": 4.2},
                            {"date": "2021-01-15", "value": 44.7, "change_percent": -5.1},
                            {"date": "2021-01-22", "value": 46.4, "change_percent": 3.8}
                        ]
                    }
                },
                "metadata": {
                    "note": "Sample trend data for basic dashboard functionality",
                    "total_trend_types": 1,
                    "data_source": "sample_data"
                }
            }
            
            logger.debug(f"Using sample alerts data - total alerts: {alerts_data.get('total_alerts', 'unknown')}")
            logger.debug(f"Using sample trends data - trend types: {trends_data.get('metadata', {}).get('total_trend_types', 'unknown')}")
            
            # Return new state instead of updating in place
            new_state = {
                **state,
                "alerts_data": alerts_data,
                "trends_data": trends_data,
                "timestamp": datetime.now().isoformat()
            }
            logger.debug(f"✅ _fetch_health_data_node completed - new state keys: {list(new_state.keys())}")
            return new_state
            
        except Exception as e:
            logger.error(f"❌ Error in _fetch_health_data_node: {str(e)}")
            error_state = {
                **state,
                "error_message": f"Failed to fetch health data: {str(e)}"
            }
            logger.debug(f"Error state keys: {list(error_state.keys())}")
            return error_state
    
    async def _analyze_data_node(self, state: DashboardState) -> DashboardState:
        """Analyze the fetched health data using LLM or basic analysis"""
        logger.debug("🚀 WORKFLOW NODE: Starting _analyze_data_node")
        logger.debug(f"Input state keys: {list(state.keys())}")
        
        try:
            alerts_data = state.get("alerts_data")
            trends_data = state.get("trends_data")
            
            logger.debug(f"Alerts data available: {alerts_data is not None}")
            logger.debug(f"Trends data available: {trends_data is not None}")
            
            if not alerts_data or not trends_data:
                logger.error("Missing required data for analysis")
                return {
                    **state,
                    "error_message": "No data available for analysis"
                }
            
            if self.llm:
                # LLM-powered analysis
                logger.info("🧠 Starting LLM-powered analysis...")
                logger.debug(f"LLM provider: {type(self.llm).__name__}")
                
                analysis_prompt = self._create_analysis_prompt(alerts_data, trends_data)
                logger.debug(f"Analysis prompt length: {len(analysis_prompt)} characters")
                
                logger.info("🧠 Analyzing health data with LLM...")
                messages = [
                    SystemMessage(content="""You are a public health data analyst expert specialized in epidemiological surveillance and trend analysis.
                    
                    Analyze the provided health alerts and trends data to identify:
                    1. Critical patterns and correlations between alerts and trend data
                    2. Emerging health threats and risk escalation patterns
                    3. Population groups and geographic areas at highest risk
                    4. Detailed trend analysis focusing on:
                       - Increasing/decreasing risk patterns
                       - Statistical significance of changes
                       - Rate of change and acceleration
                       - Geographic distribution of trends
                    5. Actionable insights and priority recommendations for public health officials
                    
                    Return your analysis in JSON format with these specific sections:
                    {
                        "critical_findings": ["list of most urgent findings"],
                        "risk_assessment": {
                            "overall_risk_level": "low|medium|high|critical",
                            "trending_up": ["metrics showing increasing risk"],
                            "trending_down": ["metrics showing decreasing risk"],
                            "states_affected": ["list of states with significant activity"],
                            "geographic_spread": "localized|regional|widespread"
                        },
                        "trend_analysis": {
                            "concerning_trends": ["specific trends requiring attention"],
                            "positive_trends": ["improving health indicators"],
                            "statistical_evidence": ["quantitative findings with numbers"]
                        },
                        "recommendations": ["5 specific actionable recommendations"]
                    }"""),
                    HumanMessage(content=analysis_prompt)
                ]
                
                logger.debug("Sending analysis request to LLM...")
                callbacks = [self.langfuse_handler] if self.langfuse_handler else []
                config = {"callbacks": callbacks} if callbacks else {}
                response = await self.llm.ainvoke(messages, config=config)
                logger.debug(f"LLM response received - length: {len(response.content)} characters")
                
                # Parse the analysis result
                try:
                    analysis_result = json.loads(response.content)
                    logger.debug("✅ Successfully parsed LLM response as JSON")
                    logger.debug(f"Analysis result keys: {list(analysis_result.keys())}")
                except json.JSONDecodeError:
                    logger.warning("⚠️ LLM response is not valid JSON, creating structured fallback")
                    # If not valid JSON, create a structured format
                    analysis_result = {
                        "analysis_text": response.content,
                        "critical_findings": ["Analysis completed but needs structured parsing"],
                        "recommendations": ["Review the full analysis text"]
                    }
            else:
                # Basic analysis without LLM
                logger.info("📊 Performing basic data analysis (no LLM)...")
                analysis_result = self._basic_data_analysis(alerts_data, trends_data)
                logger.debug(f"Basic analysis result keys: {list(analysis_result.keys())}")
            
            logger.info("✅ Data analysis completed")
            new_state = {
                **state,
                "analysis_result": analysis_result
            }
            logger.debug(f"New state keys: {list(new_state.keys())}")
            return new_state
            
        except Exception as e:
            logger.error(f"❌ Error in _analyze_data_node: {str(e)}")
            error_state = {
                **state,
                "error_message": f"Failed to analyze data: {str(e)}"
            }
            logger.debug(f"Error state keys: {list(error_state.keys())}")
            return error_state
    
    async def _generate_summary_node(self, state: DashboardState) -> DashboardState:
        """Assemble dashboard summary based on analysis"""
        logger.debug("🚀 WORKFLOW NODE: Starting _generate_summary_node")
        logger.debug(f"Input state keys: {list(state.keys())}")
        
        try:
            analysis_result = state.get("analysis_result")
            alerts_data = state.get("alerts_data")
            trends_data = state.get("trends_data")
            
            logger.debug(f"Analysis result available: {analysis_result is not None}")
            logger.debug(f"Alerts data available: {alerts_data is not None}")
            logger.debug(f"Trends data available: {trends_data is not None}")
            
            if not analysis_result or not alerts_data or not trends_data:
                logger.error("Missing required data for summary generation")
                return {
                    **state,
                    "error_message": "Missing data for summary generation"
                }
            
            if self.llm:
                # LLM-powered summary generation
                logger.info("📊 Starting LLM-powered summary generation...")
                logger.debug(f"LLM provider: {type(self.llm).__name__}")
                
                summary_prompt = self._create_summary_prompt(analysis_result, alerts_data, trends_data)
                logger.debug(f"Summary prompt length: {len(summary_prompt)} characters")
                
                logger.info("📊 Generating dashboard summary with LLM...")
                messages = [
                    SystemMessage(content="""You are creating a concise, actionable dashboard summary for public health officials.
                    Create a brief, executive-level summary that includes:
                    1. Current health situation overview (2-3 sentences)
                    2. Key alerts requiring immediate attention (bullet points)
                    3. Trend highlights (increasing/decreasing risks)
                    4. Priority recommendations (action items)
                    5. Summary statistics
                    
                    Keep it concise but comprehensive - suitable for a dashboard view."""),
                    HumanMessage(content=summary_prompt)
                ]
                
                logger.debug("Sending summary request to LLM...")
                callbacks = [self.langfuse_handler] if self.langfuse_handler else []
                config = {"callbacks": callbacks} if callbacks else {}
                response = await self.llm.ainvoke(messages, config=config)
                logger.debug(f"LLM summary response received - length: {len(response.content)} characters")
                dashboard_summary = response.content
            else:
                # Basic summary generation without LLM
                logger.info("📊 Generating basic dashboard summary...")
                dashboard_summary = self._create_basic_summary(analysis_result, alerts_data, trends_data)
                logger.debug(f"Basic summary length: {len(dashboard_summary)} characters")
            
            logger.info("✅ Dashboard summary generated")
            new_state = {
                **state,
                "dashboard_summary": dashboard_summary
            }
            logger.debug(f"Final state keys: {list(new_state.keys())}")
            return new_state
            
        except Exception as e:
            logger.error(f"❌ Error in _generate_summary_node: {str(e)}")
            error_state = {
                **state,
                "error_message": f"Failed to generate summary: {str(e)}"
            }
            logger.debug(f"Error state keys: {list(error_state.keys())}")
            return error_state
    
    async def _error_handler_node(self, state: DashboardState) -> DashboardState:
        """Handle errors in the workflow"""
        error_msg = state.get("error_message", "Unknown error occurred")
        
        dashboard_summary = f"""
        ⚠️ **Dashboard Generation Error**
        
        An error occurred while generating the health dashboard:
        {error_msg}
        
        **Recommended Actions:**
        - Check MCP server connectivity (http://{self.mcp_host}:{self.mcp_port})
        - Verify API credentials
        - Review system logs for detailed error information
        - Contact system administrator if issue persists
        """
        
        return {
            **state,
            "dashboard_summary": dashboard_summary
        }
    
    def _create_analysis_prompt(self, alerts_data: Dict, trends_data: Dict) -> str:
        """Create analysis prompt for the LLM"""
        prompt = f"""
        Please analyze the following public health data:

        **ALERTS DATA ({alerts_data.get('total_alerts', 0)} alerts):**
        {json.dumps(alerts_data, indent=2)}

        **TRENDS DATA ({len(trends_data.get('trends', {}))} categories):**
        {json.dumps(trends_data, indent=2)}

        Please provide a comprehensive analysis focusing on:
        1. Critical alerts by severity and type
        2. Geographic distribution of health threats  
        3. Trend analysis and correlations
        4. Risk assessment for different populations
        5. Emerging patterns that require attention
        """
        
        return prompt
    
    def _create_summary_prompt(self, analysis_result: Dict, alerts_data: Dict, trends_data: Dict) -> str:
        """Create summary prompt for dashboard generation"""
        
        # Extract key statistics
        total_alerts = alerts_data.get('total_alerts', 0)
        high_severity_alerts = len([a for a in alerts_data.get('alerts', []) if a.get('severity') == 'HIGH'])
        total_affected = sum(a.get('affected_population', 0) for a in alerts_data.get('alerts', []))
        trend_categories = len(trends_data.get('trends', {}))
        
        prompt = f"""
        Based on the analysis results, create a dashboard summary:

        **ANALYSIS RESULTS:**
        {json.dumps(analysis_result, indent=2)}

        **KEY STATISTICS:**
        - Total Active Alerts: {total_alerts}
        - High Severity Alerts: {high_severity_alerts}
        - Total Affected Population: {total_affected:,}
        - Trend Categories Monitored: {trend_categories}

        Create a concise, executive-level dashboard summary that public health officials can quickly scan and act upon.
        """
        
        return prompt
    
    def _basic_data_analysis(self, alerts_data: Dict, trends_data: Dict) -> Dict:
        """Perform basic data analysis without LLM"""
        alerts = alerts_data.get('alerts', [])
        trends = trends_data.get('trends', {})
        
        # Basic statistics
        high_severity_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
        medium_severity_alerts = [a for a in alerts if a.get('severity') == 'MEDIUM']
        
        # State distribution
        states_affected = {}
        for alert in alerts:
            state = alert.get('state', 'UNKNOWN')
            states_affected[state] = states_affected.get(state, 0) + 1
        
        # Population impact
        total_affected = sum(a.get('affected_population', 0) for a in alerts)
        
        # Basic trend analysis
        trending_up = []
        trending_down = []
        for trend_name, trend_data in trends.items():
            if trend_data.get('data_points'):
                recent_points = trend_data['data_points'][-3:]  # Last 3 points
                if len(recent_points) >= 2:
                    if recent_points[-1]['value'] > recent_points[0]['value']:
                        trending_up.append(trend_data.get('name', trend_name))
                    elif recent_points[-1]['value'] < recent_points[0]['value']:
                        trending_down.append(trend_data.get('name', trend_name))
        
        return {
            "critical_findings": [
                f"{len(high_severity_alerts)} high severity alerts detected",
                f"{len(medium_severity_alerts)} medium severity alerts active", 
                f"Total population affected: {total_affected:,}",
                f"States with alerts: {', '.join(states_affected.keys())}"
            ],
            "risk_assessment": {
                "high_severity_count": len(high_severity_alerts),
                "states_affected": list(states_affected.keys()),
                "trending_up": trending_up,
                "trending_down": trending_down
            },
            "recommendations": [
                "Monitor high severity alerts closely",
                "Coordinate response across affected states",
                "Track trending metrics for early intervention",
                "Prepare resources for affected populations"
            ]
        }
    
    def _create_basic_summary(self, analysis_result: Dict, alerts_data: Dict, trends_data: Dict) -> str:
        """Create basic dashboard summary without LLM"""
        
        # Extract key statistics
        total_alerts = alerts_data.get('total_alerts', 0)
        high_severity_alerts = len([a for a in alerts_data.get('alerts', []) if a.get('severity') == 'HIGH'])
        total_affected = sum(a.get('affected_population', 0) for a in alerts_data.get('alerts', []))
        
        # Get analysis insights
        critical_findings = analysis_result.get('critical_findings', [])
        risk_assessment = analysis_result.get('risk_assessment', {})
        recommendations = analysis_result.get('recommendations', [])
        
        # Create summary
        summary = f"""
📊 **PUBLIC HEALTH DASHBOARD SUMMARY**

🚨 **CURRENT SITUATION**
The public health system is monitoring {total_alerts} active alerts affecting {total_affected:,} people. 
{high_severity_alerts} alerts are classified as high severity requiring immediate attention.

🔥 **CRITICAL ALERTS**
{chr(10).join([f"• {finding}" for finding in critical_findings[:5]])}

📈 **TREND HIGHLIGHTS**
• Trends increasing: {', '.join(risk_assessment.get('trending_up', ['None']))}
• Trends decreasing: {', '.join(risk_assessment.get('trending_down', ['None']))}
• States affected: {', '.join(risk_assessment.get('states_affected', ['None']))}

✅ **PRIORITY RECOMMENDATIONS**
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations[:4])])}

📊 **STATISTICS**
• Total Active Alerts: {total_alerts}
• High Severity: {high_severity_alerts}
• Population Affected: {total_affected:,}
• Trend Categories: {len(trends_data.get('trends', {}))}

---
*Generated by Public Health Dashboard Agent (Basic Mode)*
        """.strip()
        
        return summary
    
    def _process_alerts_for_dashboard(self, alerts_data: Dict, analysis_result: Dict) -> List[Dict]:
        """Process alerts with analysis for dashboard response"""
        if not alerts_data or not alerts_data.get("alerts"):
            return []
        
        processed_alerts = []
        raw_alerts = alerts_data.get("alerts", [])
        
        # Get analysis insights if available
        critical_findings = analysis_result.get("critical_findings", [])
        
        for i, alert in enumerate(raw_alerts[:10]):  # Limit to top 10 alerts
            processed_alert = {
                "id": alert.get("id", f"alert_{i}"),
                "title": alert.get("title", "Unknown Alert"),
                "description": alert.get("description", ""),
                "severity": alert.get("severity", "UNKNOWN"),
                "state": alert.get("state", ""),
                "county": alert.get("county", ""),
                "alert_type": alert.get("alert_type", ""),
                "affected_population": alert.get("affected_population", 0),
                "timestamp": alert.get("timestamp", ""),
                "source": alert.get("source", ""),
                
                # Analysis enhancement
                "analysis": {
                    "priority_score": self._calculate_priority_score(alert),
                    "risk_level": self._assess_alert_risk(alert),
                    "related_findings": [f for f in critical_findings if alert.get("state", "").lower() in f.lower() or alert.get("alert_type", "").lower() in f.lower()][:2]
                }
            }
            processed_alerts.append(processed_alert)
        
        # Sort by priority score (highest first)
        processed_alerts.sort(key=lambda x: x["analysis"]["priority_score"], reverse=True)
        return processed_alerts
    
    def _extract_trend_analysis(self, trends_data: Dict, analysis_result: Dict) -> Dict:
        """Extract trend analysis for dashboard"""
        trend_analysis = {
            "rising_trends": [],
            "signals": []
        }
        
        if not trends_data or not trends_data.get("trends"):
            return trend_analysis
        
        trends = trends_data.get("trends", {})
        
        # Process each trend category
        for trend_name, trend_info in trends.items():
            if not trend_info.get("data_points"):
                continue
                
            data_points = trend_info["data_points"]
            if len(data_points) < 2:
                continue
            
            # Calculate trend direction
            recent_values = [point["value"] for point in data_points[-3:]]
            if len(recent_values) >= 2:
                trend_direction = "rising" if recent_values[-1] > recent_values[0] else "declining"
                change_percent = data_points[-1].get("change_percent", 0)
                
                trend_item = {
                    "signal_name": trend_name,
                    "description": trend_info.get("description", ""),
                    "current_value": data_points[-1]["value"],
                    "unit": trend_info.get("unit", ""),
                    "trend_direction": trend_direction,
                    "change_percent": change_percent,
                    "data_points": len(data_points),
                    "last_updated": data_points[-1]["date"],
                    "risk_level": "high" if abs(change_percent) > 15 else "medium" if abs(change_percent) > 5 else "low"
                }
                
                # Add to rising trends if significant increase
                if trend_direction == "rising" and change_percent > 5:
                    trend_analysis["rising_trends"].append(trend_item)
                
                # Add to signals regardless
                trend_analysis["signals"].append(trend_item)
        
        return trend_analysis
    
    def _calculate_priority_score(self, alert: Dict) -> int:
        """Calculate priority score for an alert (0-100)"""
        score = 0
        
        # Severity scoring
        severity_scores = {"HIGH": 40, "MEDIUM": 25, "LOW": 10}
        score += severity_scores.get(alert.get("severity"), 5)
        
        # Population impact scoring
        affected = alert.get("affected_population", 0)
        if affected > 100000:
            score += 30
        elif affected > 50000:
            score += 20
        elif affected > 10000:
            score += 15
        elif affected > 1000:
            score += 10
        else:
            score += 5
        
        # Alert type scoring
        type_scores = {"OUTBREAK": 20, "ENVIRONMENTAL": 15, "FOOD_SAFETY": 15, "SEASONAL": 10}
        score += type_scores.get(alert.get("alert_type"), 5)
        
        # Recency scoring (newer alerts get higher scores)
        try:
            alert_time = datetime.fromisoformat(alert.get("timestamp", "").replace('Z', '+00:00'))
            days_old = (datetime.now(alert_time.tzinfo) - alert_time).days
            if days_old < 1:
                score += 10
            elif days_old < 3:
                score += 5
        except:
            pass
        
        return min(score, 100)
    
    def _assess_alert_risk(self, alert: Dict) -> str:
        """Assess overall risk level for an alert"""
        priority_score = self._calculate_priority_score(alert)
        
        if priority_score >= 70:
            return "critical"
        elif priority_score >= 50:
            return "high"
        elif priority_score >= 30:
            return "medium"
        else:
            return "low"
    
    def _build_basic_risk_assessment(self, alerts_data: Dict, trends_data: Dict) -> Dict:
        """Build basic risk assessment when analysis is not available"""
        alerts = alerts_data.get("alerts", [])
        
        high_severity_count = len([a for a in alerts if a.get("severity") == "HIGH"])
        total_affected = sum(a.get("affected_population", 0) for a in alerts)
        states_affected = list(set(a.get("state") for a in alerts if a.get("state")))
        
        # Determine overall risk level
        if high_severity_count >= 3 or total_affected > 500000:
            overall_risk = "high"
        elif high_severity_count >= 1 or total_affected > 100000:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "overall_risk_level": overall_risk,
            "high_severity_alerts": high_severity_count,
            "total_population_affected": total_affected,
            "states_with_alerts": len(states_affected),
            "geographic_spread": "widespread" if len(states_affected) > 5 else "localized",
            "key_concerns": [a.get("alert_type") for a in alerts if a.get("severity") == "HIGH"][:3]
        }
    
    def _generate_basic_recommendations(self, alerts_data: Dict, trends_data: Dict) -> List[str]:
        """Assemble basic recommendations when analysis is not available"""
        recommendations = []
        alerts = alerts_data.get("alerts", [])
        
        high_severity_alerts = [a for a in alerts if a.get("severity") == "HIGH"]
        
        if high_severity_alerts:
            recommendations.append("Immediate attention required for high-severity alerts")
            recommendations.append("Activate emergency response protocols for affected areas")
        
        if any(a.get("alert_type") == "OUTBREAK" for a in alerts):
            recommendations.append("Implement enhanced surveillance and contact tracing")
        
        if any(a.get("alert_type") == "ENVIRONMENTAL" for a in alerts):
            recommendations.append("Monitor environmental conditions and issue public advisories")
        
        total_affected = sum(a.get("affected_population", 0) for a in alerts)
        if total_affected > 100000:
            recommendations.append("Coordinate regional response efforts")
        
        if not recommendations:
            recommendations.append("Continue routine monitoring and surveillance")
        
        return recommendations[:5]  # Limit to 5 recommendations

    async def assemble_dashboard(self, start_date: Optional[str] = "2020-02-01", end_date: Optional[str] = "2022-02-01") -> Dict:
        """Assemble a dashboard summary"""
        logger.info(f"🚀 LANGGRAPH WORKFLOW: Starting dashboard generation")
        logger.debug(f"Date range: {start_date} to {end_date}")
        logger.debug(f"Agent configuration - LLM: {type(self.llm).__name__ if self.llm else 'None'}")
        logger.debug(f"Agent configuration - MCP: {self.mcp_host}:{self.mcp_port}")
        
        # Build the dashboard generation request with date context
        dashboard_request = "Generate comprehensive public health dashboard"
        if start_date or end_date:
            date_context = f" focusing on data"
            if start_date:
                date_context += f" from {start_date}"
            if end_date:
                date_context += f" through {end_date}"
            else:
                date_context += " through current date"
            dashboard_request += date_context
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=dashboard_request)],
            "current_request": dashboard_request,
            "alerts_data": None,
            "trends_data": None,
            "analysis_result": None,
            "dashboard_summary": None,
            "error_message": None,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"Initial state keys: {list(initial_state.keys())}")
        logger.info(f"🚀 Starting dashboard generation: {dashboard_request}")
        logger.info("=" * 60)
        
        # Run the workflow with proper configuration and Langfuse tracing
        config = {
            "configurable": {"thread_id": "dashboard_session"},
            "tags": ["public-health", "standard-agent", "alert-analysis"],
            "metadata": {
                "agent_type": "standard",
                "date_range": f"{start_date} to {end_date}" if start_date or end_date else "default",
                "workflow_version": "v1.0",
                "data_sources": ["mcp_server", "alerts_api"]
            }
        }
        
        # Add Langfuse callback if available
        if self.langfuse_handler:
            config["callbacks"] = [self.langfuse_handler]
            
        logger.debug(f"Workflow config: {config}")
        logger.info("🔄 Executing LangGraph workflow...")
        
        try:
            final_state = await self.workflow.ainvoke(initial_state, config=config)
            logger.debug(f"Final state keys: {list(final_state.keys())}")
            logger.info("✅ LangGraph workflow completed successfully")
        except Exception as e:
            logger.error(f"❌ LangGraph workflow failed: {str(e)}")
            raise
        
        # MCP client will auto-cleanup when async loop exits
        
        alerts_data = final_state.get("alerts_data") or {}
        trends_data = final_state.get("trends_data") or {}
        analysis_result = final_state.get("analysis_result") or {}
        
        # Process alerts with analysis
        processed_alerts = self._process_alerts_for_dashboard(alerts_data, analysis_result)
        
        # Extract trend analysis (basic for now, will be enhanced with MCP trends later)
        trend_analysis = self._extract_trend_analysis(trends_data, analysis_result)
        
        # Build risk assessment
        risk_assessment = analysis_result.get("risk_assessment", {})
        if not risk_assessment and alerts_data:
            risk_assessment = self._build_basic_risk_assessment(alerts_data, trends_data)
        
        # Extract recommendations
        recommendations = analysis_result.get("recommendations", [])
        if not recommendations:
            recommendations = self._generate_basic_recommendations(alerts_data, trends_data)
        
        result = {
            "dashboard_summary": final_state.get("dashboard_summary", "No summary generated"),
            "timestamp": final_state.get("timestamp"),
            "success": not bool(final_state.get("error_message")),
            "error": final_state.get("error_message"),
            
            # Enhanced structured data
            "alerts": processed_alerts,
            "rising_trends": trend_analysis.get("rising_trends", []),
            "epidemiological_signals": trend_analysis.get("signals", []),
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "agent_type": "standard"
        }
        
        alerts_count = len(result.get('alerts', []))
        trends_count = len(result.get('rising_trends', []))
        logger.debug(f"Result summary - Success: {result['success']}, Alerts: {alerts_count}, Trends: {trends_count}")
        logger.info("🎉 Dashboard generation completed")
        
        return result

# Utility functions for testing and CLI usage
async def test_dashboard_agent():
    """Test the dashboard agent"""
    print("🏥 Public Health Dashboard Agent Test")
    print("=" * 50)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print("For testing without LLM, this will still demonstrate MCP integration.")
    
    try:
        # Create agent
        agent = PublicHealthDashboardAgent()
        
        # Generate dashboard
        result = await agent.assemble_dashboard()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 DASHBOARD SUMMARY")
        print("=" * 60)
        print(result["dashboard_summary"])
        print("\n" + "=" * 60)
        alerts_count = len(result.get('alerts', []))
        trends_count = len(result.get('rising_trends', []))
        print(f"📈 Statistics: {alerts_count} alerts, {trends_count} trend categories")
        print(f"⏰ Generated: {result['timestamp']}")
        print(f"✅ Success: {result['success']}")
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def run_interactive_dashboard():
    """Run an interactive dashboard session"""
    print("🏥 Interactive Public Health Dashboard")
    print("Type 'exit' to quit, 'help' for commands")
    print("=" * 50)
    
    agent = PublicHealthDashboardAgent()
    
    while True:
        try:
            user_input = input("\n💬 Enter dashboard request (or 'exit'): ").strip()
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- 'alerts only' - Focus on current alerts")
                print("- 'trends only' - Focus on risk trends")
                print("- 'high severity' - High severity issues only")
                print("- 'state [XX]' - Focus on specific state (e.g., 'state CA')")
                print("- 'exit' - Quit the session")
                continue
            elif not user_input:
                user_input = "Generate standard public health dashboard"
            
            result = await agent.assemble_dashboard()
            
            print("\n📊 Dashboard Result:")
            print("-" * 40)
            print(result["dashboard_summary"])
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(run_interactive_dashboard())
    else:
        asyncio.run(test_dashboard_agent()) 