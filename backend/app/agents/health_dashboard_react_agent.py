#!/usr/bin/env python3
"""
Public Health Dashboard ReAct Agent using LangGraph

This agent uses a ReAct (Reasoning + Acting) pattern to:
Phase 1: Fetch and analyze epidemiological data using real APIs
Phase 2: Generate comprehensive dashboard summaries with actionable insights

The agent demonstrates modern LLM workflows with tool integration for public health analysis.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


# Load configuration from settings
try:
    from ..config import settings
except ImportError:
    # If running directly, try absolute import
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config import settings

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
    
    logger.debug("🔧 Debug logging enabled for LangGraph ReAct workflow")
    return logger

# Setup logging and get logger
logger = setup_debug_logging()


class PublicHealthReActAgent:
    """ReAct agent for public health dashboard generation using epidemiological data"""
    
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
                print("⚠️  No valid LLM API keys found. Agent cannot operate without LLM in ReAct mode.")
                raise ValueError("ReAct agent requires valid LLM API key")
        
        if llm_provider == "openai" and openai_key and openai_key.startswith('sk-'):
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=openai_key
            )
        elif llm_provider == "anthropic" and anthropic_key and anthropic_key.startswith('sk-ant-'):
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=1.0,
                max_tokens=64000,  # Must be greater than thinking.budget_tokens
                thinking={"type": "enabled", "budget_tokens": 8000},
                betas=["extended-cache-ttl-2025-04-11"],
                api_key=anthropic_key
            )
        else:
            raise ValueError(f"Invalid LLM provider: {llm_provider}")
        
        # Initialize MCP client
        self.mcp_client = None
        self.tools = []
        
        # Initialize the agent
        self.agent = None
        
    async def _init_mcp_client(self):
        """Initialize MCP client connection and tools"""
        if not self.mcp_client:
            client_config = {
                "public-health-fastmcp": {
                    "url": f"http://{self.mcp_host}:{self.mcp_port}/sse",
                    "transport": "sse",
                }
            }
            self.mcp_client = MultiServerMCPClient(client_config)
            
        # Get MCP tools and wrap them for LangChain
        logger.debug("🔧 Fetching MCP tools...")
        mcp_tools = await self.mcp_client.get_tools()
        logger.debug(f"Available MCP tools: {[t.name for t in mcp_tools]}")
        
        # Filter for only fetch_epi_signal and detect_rising_trend tools
        self.tools = [t for t in mcp_tools if t.name in ["fetch_epi_signal", "detect_rising_trend"]]

        logger.debug(f"✅ Initialized {len(self.tools)} LangChain tools: {[t.name for t in self.tools]}")
        
    async def _create_agent(self):
        """Create the ReAct agent with system prompt"""
        if not self.agent:
            await self._init_mcp_client()
            
            # Create comprehensive system prompt for the ReAct agent
            system_prompt = """You are a Public Health Data Analyst AI Agent specializing in epidemiological surveillance and health trend analysis.

Your mission is to provide comprehensive public health intelligence through a two-phase analytical process:

🔬 **PHASE 1: DATA ACQUISITION & ANALYSIS**
- Fetch real-time epidemiological data using the Delphi Epidata API
- Analyze multiple health signals (COVID cases, symptoms, vaccinations, doctor visits, etc.)
- Detect statistical trends and patterns using rolling regression analysis
- Cross-reference with current health alerts and advisories
- Focus on signals that show concerning trends or patterns

📊 **PHASE 2: SYNTHESIS & DASHBOARD GENERATION**
- Synthesize findings into actionable public health intelligence
- Generate executive-level dashboard summaries
- Provide clear risk assessments and priority recommendations
- Highlight emerging threats and population health trends
- Present data in formats suitable for public health decision-making

**Available Epidemiological Signals:**
- smoothed_wcli: COVID-like symptoms prevalence
- smoothed_adj_cli: COVID-related doctor visits  
- confirmed_7dav_incidence_prop: COVID case rates
- confirmed_admissions_covid_1d_prop_7dav: COVID hospitalizations
- deaths_7dav_incidence_prop: COVID death rates
- smoothed_wwearing_mask_7d: Mask wearing behavior
- smoothed_wcovid_vaccinated_appointment_or_accept: Vaccine acceptance
- sum_anosmia_ageusia_smoothed_search: COVID symptom searches
- smoothed_whh_cmnty_cli: Community COVID symptoms

**Analytical Approach:**
1. Start by fetching key health signals (focus on recent data - last 30-60 days)
2. Analyze trends for concerning patterns (rising cases, symptoms, hospitalizations)
3. Cross-reference with public health alerts for context
4. Synthesize findings into clear, actionable intelligence

**Output Format:**
Provide comprehensive dashboard summaries that include:
- Executive situation overview
- Critical alerts and emerging threats  
- Statistical trend analysis with specific metrics
- Geographic distribution of health threats
- Risk-based recommendations for public health action
- Supporting data and confidence levels

**Structured Recommendations Section:**
Always end your analysis with a clear "RECOMMENDATIONS" section listing 3-5 specific, actionable recommendations for public health officials.

**Data Citation:**
Reference specific tool outputs, numbers, and statistical findings from your analysis. When you detect rising trends, clearly state which signals are trending upward and provide the statistical evidence.

Always ground your analysis in the real data you fetch. Be specific about numbers, trends, and timeframes. Focus on actionable insights that public health officials can use for decision-making."""

            # Create the ReAct agent
            self.agent = create_react_agent(
                model=self.llm,
                tools=self.tools,
                prompt=system_prompt,
                debug=True
            )
            
            logger.debug("✅ ReAct agent created with system prompt and tools")
    
    def _extract_structured_data_from_conversation(self, result: Dict) -> Dict:
        """Extract structured data from ReAct agent conversation"""
        structured_data = {
            "alerts": [],
            "rising_trends": [],
            "epidemiological_signals": [],
            "risk_assessment": {},
            "recommendations": []
        }
        
        try:
            # Extract conversation messages to analyze tool outputs
            messages = result.get("messages", [])
            
            rising_trends = []
            epi_signals = []
            recommendations = []
            
            for message in messages:
                content = str(message.content) if hasattr(message, 'content') else str(message)
                
                # Look for detect_rising_trend tool outputs
                if "rising_periods" in content and "total_periods" in content:
                    try:
                        # Try to extract trend information
                        import re
                        import json as json_lib
                        
                        # Look for JSON-like patterns in the content
                        json_match = re.search(r'\{[^{}]*"rising_periods"[^{}]*\}', content)
                        if json_match:
                            trend_data = json_lib.loads(json_match.group())
                            if trend_data.get("rising_periods"):
                                rising_trends.append({
                                    "signal_name": "epidemiological_signal",
                                    "trend_direction": "rising",
                                    "rising_periods": trend_data["rising_periods"],
                                    "total_periods": trend_data.get("total_periods", 0),
                                    "risk_level": "high" if trend_data.get("total_periods", 0) > 3 else "medium",
                                    "detected_via": "detect_rising_trend_tool"
                                })
                    except:
                        # If parsing fails, create a basic trend entry
                        if "rising_periods" in content:
                            rising_trends.append({
                                "signal_name": "epidemiological_data",
                                "trend_direction": "rising", 
                                "description": "Rising trend detected in epidemiological analysis",
                                "risk_level": "medium",
                                "detected_via": "react_analysis"
                            })
                
                # Look for fetch_epi_signal tool outputs
                if any(signal in content for signal in ["confirmed_7dav_incidence_prop", "smoothed_wcli", "smoothed_adj_cli"]):
                    # Extract signal information
                    for signal in ["confirmed_7dav_incidence_prop", "smoothed_wcli", "smoothed_adj_cli", "deaths_7dav_incidence_prop"]:
                        if signal in content:
                            signal_descriptions = {
                                "confirmed_7dav_incidence_prop": "COVID-19 Case Rates",
                                "smoothed_wcli": "COVID-Like Symptoms",
                                "smoothed_adj_cli": "COVID-Related Doctor Visits",
                                "deaths_7dav_incidence_prop": "COVID-19 Death Rates"
                            }
                            
                            epi_signals.append({
                                "signal_name": signal,
                                "description": signal_descriptions.get(signal, signal),
                                "data_source": "delphi_epidata_api",
                                "last_analyzed": datetime.now().isoformat(),
                                "status": "analyzed"
                            })
                
                # Extract recommendations from final summary
                if any(keyword in content.lower() for keyword in ["recommend", "should", "action", "priority"]):
                    # Try to extract bullet points or numbered recommendations
                    import re
                    rec_patterns = [
                        r'(?:^|\n)\s*[\d\-\*•]\s*(.+?)(?=\n|$)',  # Numbered or bulleted lists
                        r'(?:recommend|suggest|should)([^.]+)',  # Recommendation statements
                    ]
                    
                    for pattern in rec_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                        for match in matches[:3]:  # Limit to 3 recommendations per pattern
                            if len(match.strip()) > 10:  # Only meaningful recommendations
                                recommendations.append(match.strip())
            
            # Build risk assessment based on findings
            risk_assessment = {
                "overall_risk_level": "medium",  # Default
                "epidemiological_signals_analyzed": len(set(s["signal_name"] for s in epi_signals)),
                "rising_trends_detected": len(rising_trends),
                "analysis_method": "react_agent_with_epi_tools",
                "confidence_level": "high" if len(epi_signals) > 2 else "medium"
            }
            
            # Adjust risk level based on findings
            if len(rising_trends) > 2:
                risk_assessment["overall_risk_level"] = "high"
            elif len(rising_trends) == 0 and len(epi_signals) > 0:
                risk_assessment["overall_risk_level"] = "low"
            
            structured_data = {
                "alerts": [],  # ReAct agent doesn't have access to alerts currently
                "rising_trends": rising_trends[:5],  # Limit to top 5
                "epidemiological_signals": epi_signals[:10],  # Limit to top 10
                "risk_assessment": risk_assessment,
                "recommendations": list(set(recommendations))[:5]  # Deduplicate and limit
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting structured data from conversation: {str(e)}")
            # Return basic structure with error note
            structured_data["risk_assessment"] = {
                "overall_risk_level": "unknown",
                "analysis_method": "react_agent_with_parsing_error",
                "error": str(e)
            }
        
        return structured_data

    async def generate_dashboard(self, request: str = "Generate comprehensive public health dashboard with current epidemiological analysis") -> Dict:
        """Generate a dashboard summary using ReAct agent"""
        logger.info(f"🚀 REACT AGENT: Starting dashboard generation")
        logger.debug(f"Request: {request}")
        logger.debug(f"Agent configuration - LLM: {type(self.llm).__name__ if self.llm else 'None'}")
        logger.debug(f"Agent configuration - MCP: {self.mcp_host}:{self.mcp_port}")
        
        try:
            # Initialize agent if not already done
            await self._create_agent()
            
            # Create enhanced request with specific instructions
            enhanced_request = f"""
{request}

Please follow this analytical workflow:

PHASE 1 - Data Acquisition:
1. Fetch recent COVID case data (confirmed_7dav_incidence_prop) for the US
2. Fetch COVID symptoms data (smoothed_wcli) to analyze symptom prevalence  
3. Fetch doctor visits for COVID (smoothed_adj_cli) to assess healthcare utilization
4. Get current public health alerts for contextual awareness

PHASE 2 - Analysis & Trends:
5. Analyze trends for each signal using detect_rising_trend tool
6. Look for concerning patterns, rising trends, or geographic hotspots
7. Cross-reference findings with public health alerts

PHASE 3 - Dashboard Synthesis:
8. Create a comprehensive dashboard summary with:
   - Current epidemiological situation
   - Key trends and alerts
   - Risk assessment and geographic distribution
   - Actionable recommendations for public health response
   - Supporting statistical evidence

Focus on recent data (last 30-60 days) and provide specific metrics and trends.
"""
            
            logger.info("🔄 Invoking ReAct agent with enhanced analytical request...")
            
            # Execute the ReAct agent
            config = {"configurable": {"thread_id": "react_dashboard_session"}}
            
            # Create input in the format expected by ReAct agent
            messages = [HumanMessage(content=enhanced_request)]
            
            result = await self.agent.ainvoke(
                {"messages": messages},
                config=config
            )
            
            logger.debug(f"ReAct agent result type: {type(result)}")
            
            # Extract the final response
            if "messages" in result:
                final_message = result["messages"][-1]
                if hasattr(final_message, 'content'):
                    dashboard_summary = final_message.content
                else:
                    dashboard_summary = str(final_message)
            else:
                dashboard_summary = str(result)
            
            logger.info("✅ ReAct agent completed successfully")
            
            # Extract structured data from the conversation (attempt to parse trends and signals)
            structured_data = self._extract_structured_data_from_conversation(result)
            
            # Format the response with enhanced structured data
            response = {
                "dashboard_summary": dashboard_summary,
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "agent_type": "ReAct",
                "llm_provider": type(self.llm).__name__,
                "tools_used": [t.name for t in self.tools],
                "error": None,
                
                # Enhanced structured data from ReAct analysis
                "alerts": structured_data.get("alerts", []),
                "rising_trends": structured_data.get("rising_trends", []),
                "epidemiological_signals": structured_data.get("epidemiological_signals", []),
                "risk_assessment": structured_data.get("risk_assessment", {}),
                "recommendations": structured_data.get("recommendations", [])
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ ReAct agent failed: {str(e)}")
            
            # Return error response
            error_response = {
                "dashboard_summary": f"""
⚠️ **Dashboard Generation Error**

An error occurred while generating the health dashboard using ReAct agent:
{str(e)}

**Recommended Actions:**
- Check MCP server connectivity (http://{self.mcp_host}:{self.mcp_port})
- Verify LLM API credentials  
- Review system logs for detailed error information
- Contact system administrator if issue persists

**Agent Configuration:**
- LLM Provider: {type(self.llm).__name__ if self.llm else 'None'}
- Tools Available: {len(self.tools)}
                """,
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent_type": "ReAct",
                "error": str(e)
            }
            
            return error_response
        
        finally:
            # Clean up MCP connection
            if self.mcp_client:
                try:
                    logger.debug("Closing MCP client connection...")
                    await self.mcp_client.close()
                    logger.debug("✅ MCP client closed")
                except Exception as e:
                    logger.warning(f"⚠️ Error closing MCP client: {str(e)}")


# Convenience functions for testing and usage
async def test_react_agent():
    """Test the ReAct agent with a sample request"""
    print("🧪 Testing Public Health ReAct Agent...")
    
    agent = PublicHealthReActAgent()
    
    result = await agent.generate_dashboard(
        "Analyze current COVID-19 trends and generate a public health dashboard for the United States"
    )
    
    print("\n" + "="*80)
    print("📊 REACT AGENT DASHBOARD RESULT")
    print("="*80)
    print(result["dashboard_summary"])
    print("\n" + "="*80)
    print(f"Success: {result['success']}")
    print(f"Agent Type: {result.get('agent_type', 'Unknown')}")
    print(f"Tools Used: {result.get('tools_used', [])}")
    print(f"Timestamp: {result.get('timestamp', 'Unknown')}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")


async def run_interactive_react_dashboard():
    """Interactive ReAct dashboard generator"""
    print("🏥 Interactive Public Health ReAct Dashboard Agent")
    print("=" * 60)
    print("Enter requests to generate health dashboards using real epidemiological data.")
    print("Type 'exit' to quit.\n")
    
    agent = PublicHealthReActAgent()
    
    while True:
        try:
            request = input("📝 Enter your dashboard request: ").strip()
            
            if request.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not request:
                print("Please enter a request.")
                continue
            
            print(f"\n🔄 Processing: {request}")
            print("-" * 40)
            
            result = await agent.generate_dashboard(request)
            
            print("\n" + "="*60)
            print("📊 REACT DASHBOARD RESULT")  
            print("="*60)
            print(result["dashboard_summary"])
            print("\n" + "="*60)
            print(f"✅ Success: {result['success']}")
            if result.get('tools_used'):
                print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
            print(f"⏰ Generated: {result.get('timestamp', 'Unknown')}")
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(run_interactive_react_dashboard())
    else:
        asyncio.run(test_react_agent()) 