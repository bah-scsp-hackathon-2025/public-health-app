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
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Annotated
from operator import add

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
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

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
    
    def __init__(self, llm_provider: str = "auto", mcp_host: str = None, mcp_port: int = None):
        # Load MCP configuration
        self.mcp_host = mcp_host or settings.mcp_server_host if hasattr(settings, 'mcp_server_host') else os.getenv("MCP_SERVER_HOST", "localhost")
        self.mcp_port = mcp_port or int(settings.mcp_server_port if hasattr(settings, 'mcp_server_port') else os.getenv("MCP_SERVER_PORT", "8000"))
        self.llm_provider = llm_provider
        
        # Get API keys from settings
        openai_key = settings.openai_api_key if settings.openai_api_key else None
        anthropic_key = settings.anthropic_api_key if settings.anthropic_api_key else None
        
        # Initialize LLM with error handling
        self.llm = None
        if llm_provider == "auto":
            # Auto-detect available provider
            if openai_key and openai_key.startswith('sk-'):
                llm_provider = "openai"
            elif anthropic_key and anthropic_key.startswith('sk-ant-'):
                llm_provider = "anthropic"
            else:
                print("⚠️  No valid LLM API keys found. Agent will work in MCP-only mode.")
                llm_provider = None
        
        if llm_provider == "openai" and openai_key and openai_key.startswith('sk-'):
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=openai_key
            )
        elif llm_provider == "anthropic" and anthropic_key and anthropic_key.startswith('sk-ant-'):
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.1,
                api_key=anthropic_key
            )
        elif llm_provider and llm_provider not in ["auto", None]:
            print(f"⚠️  {llm_provider} API key not found or invalid. Agent will work in MCP-only mode.")
        
        # Initialize MCP client
        self.mcp_client = None
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
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
            
            alerts_tool = next((t for t in tools if t.name == "get_public_health_alerts"), None)
            trends_tool = next((t for t in tools if t.name == "get_health_risk_trends"), None)
            
            if not alerts_tool or not trends_tool:
                raise Exception("Required MCP tools not available")
            
            # Fetch recent alerts (temporarily without date filtering due to timezone issue)
            logger.info("🔍 Fetching public health alerts...")
            alerts_params = {"limit": 20}
            logger.debug(f"Alerts tool parameters: {alerts_params}")
            alerts_result = await alerts_tool.ainvoke(alerts_params)
            logger.debug(f"Alerts result type: {type(alerts_result)}")
            
            # Fetch all available trends
            logger.info("📈 Fetching health risk trends...")
            trends_params = {}
            logger.debug(f"Trends tool parameters: {trends_params}")
            trends_result = await trends_tool.ainvoke(trends_params)
            logger.debug(f"Trends result type: {type(trends_result)}")
            
            # Parse results (they come as JSON strings)
            alerts_data = json.loads(alerts_result) if isinstance(alerts_result, str) else alerts_result
            trends_data = json.loads(trends_result) if isinstance(trends_result, str) else trends_result
            
            logger.debug(f"Parsed alerts data - total alerts: {alerts_data.get('total_alerts', 'unknown')}")
            logger.debug(f"Parsed trends data - trend types: {trends_data.get('metadata', {}).get('total_trend_types', 'unknown')}")
            
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
                    SystemMessage(content="""You are a public health data analyst expert. 
                    Analyze the provided health alerts and trends data to identify:
                    1. Critical patterns and correlations
                    2. Emerging health threats
                    3. Population groups at risk
                    4. Trend analysis (increasing/decreasing risks)
                    5. Actionable insights for public health officials
                    
                    Provide your analysis in JSON format with clear categories and severity levels."""),
                    HumanMessage(content=analysis_prompt)
                ]
                
                logger.debug("Sending analysis request to LLM...")
                response = await self.llm.ainvoke(messages)
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
        """Generate dashboard summary based on analysis"""
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
                response = await self.llm.ainvoke(messages)
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
    
    async def generate_dashboard(self, request: str = "Generate comprehensive public health dashboard") -> Dict:
        """Generate a dashboard summary"""
        logger.info(f"🚀 LANGGRAPH WORKFLOW: Starting dashboard generation")
        logger.debug(f"Request: {request}")
        logger.debug(f"Agent configuration - LLM: {type(self.llm).__name__ if self.llm else 'None'}")
        logger.debug(f"Agent configuration - MCP: {self.mcp_host}:{self.mcp_port}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=request)],
            "current_request": request,
            "alerts_data": None,
            "trends_data": None,
            "analysis_result": None,
            "dashboard_summary": None,
            "error_message": None,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"Initial state keys: {list(initial_state.keys())}")
        logger.info(f"🚀 Starting dashboard generation: {request}")
        logger.info("=" * 60)
        
        # Run the workflow with proper configuration
        config = {"configurable": {"thread_id": "dashboard_session"}}
        logger.debug(f"Workflow config: {config}")
        logger.info("🔄 Executing LangGraph workflow...")
        
        try:
            final_state = await self.workflow.ainvoke(initial_state, config=config)
            logger.debug(f"Final state keys: {list(final_state.keys())}")
            logger.info("✅ LangGraph workflow completed successfully")
        except Exception as e:
            logger.error(f"❌ LangGraph workflow failed: {str(e)}")
            raise
        
        # Clean up MCP connection
        if self.mcp_client:
            try:
                logger.debug("Closing MCP client connection...")
                await self.mcp_client.close()
                logger.debug("✅ MCP client closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing MCP client: {str(e)}")
        
        alerts_data = final_state.get("alerts_data") or {}
        trends_data = final_state.get("trends_data") or {}
        
        result = {
            "dashboard_summary": final_state.get("dashboard_summary", "No summary generated"),
            "alerts_count": alerts_data.get("total_alerts", 0),
            "trends_count": len(trends_data.get("trends", {})),
            "timestamp": final_state.get("timestamp"),
            "success": not bool(final_state.get("error_message")),
            "error": final_state.get("error_message")
        }
        
        logger.debug(f"Result summary - Success: {result['success']}, Alerts: {result['alerts_count']}, Trends: {result['trends_count']}")
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
    
    # Determine LLM provider
    llm_provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    
    try:
        # Create agent
        agent = PublicHealthDashboardAgent(llm_provider=llm_provider)
        
        # Generate dashboard
        result = await agent.generate_dashboard(
            "Generate a comprehensive public health dashboard focusing on current alerts and risk trends"
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 DASHBOARD SUMMARY")
        print("=" * 60)
        print(result["dashboard_summary"])
        print("\n" + "=" * 60)
        print(f"📈 Statistics: {result['alerts_count']} alerts, {result['trends_count']} trend categories")
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
    
    llm_provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    agent = PublicHealthDashboardAgent(llm_provider=llm_provider)
    
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
            
            result = await agent.generate_dashboard(user_input)
            
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