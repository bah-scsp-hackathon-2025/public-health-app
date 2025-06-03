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
from typing import Dict, List, Optional, Annotated, Any, TypedDict
from operator import add

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field
import anthropic


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


# Typed data models for graph state
class EpiSignalData(BaseModel):
    """Epidemiological signal data from fetch_epi_signal tool"""
    signal_name: str
    display_name: str
    description: str
    geographic_areas: List[str] = Field(default_factory=list)
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    current_value: Optional[float] = None
    trend_direction: str = "unknown"
    data_quality: str = "unknown"
    fetch_timestamp: str
    

class TrendAnalysisData(BaseModel):
    """Trend analysis data from detect_rising_trend tool"""
    signal_name: str
    rising_periods: int
    total_periods: int
    trend_strength: str = "medium"
    risk_level: str = "medium"
    analysis_timestamp: str
    statistical_evidence: Dict[str, Any] = Field(default_factory=dict)


class ReActState(TypedDict):
    """State for the ReAct workflow"""
    messages: Annotated[List[BaseMessage], add]
    current_request: str
    
    # Tool data storage
    epi_signals: List[Dict[str, Any]]  # Store as dicts for JSON compatibility
    trend_analyses: List[Dict[str, Any]]  # Store as dicts for JSON compatibility
    
    # Analysis state
    reasoning_steps: List[str]
    tools_used: List[str]
    analysis_complete: bool
    
    # Final outputs
    dashboard_summary: Optional[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    error_message: Optional[str]
    timestamp: str


class PublicHealthReActAgent:
    """LangGraph ReAct agent for public health dashboard generation using epidemiological data"""
    
    def __init__(self):
        # Load MCP configuration from environment variables
        self.mcp_host = settings.mcp_server_host if hasattr(settings, 'mcp_server_host') else os.getenv("MCP_SERVER_HOST", "localhost")
        self.mcp_port = int(settings.mcp_server_port if hasattr(settings, 'mcp_server_port') else os.getenv("MCP_SERVER_PORT", "8000"))
        
        # Get API keys from settings (keep both for future use)
        openai_key = settings.openai_api_key if settings.openai_api_key else None
        anthropic_key = settings.anthropic_api_key if settings.anthropic_api_key else None
        
        # Initialize with Anthropic/Claude (required for ReAct mode)
        self.llm = None
        self.anthropic_client = None
        if anthropic_key and anthropic_key.startswith('sk-ant-'):
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=1.0,
                max_tokens=64000,  # Must be greater than thinking.budget_tokens
                thinking={"type": "enabled", "budget_tokens": 8000},
                betas=["extended-cache-ttl-2025-04-11", "files-api-2025-04-14"],
                api_key=anthropic_key
            )
            # Initialize direct Anthropic client for Files API
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        else:
            print("⚠️  Anthropic API key not found or invalid. ReAct agent requires valid Anthropic API key.")
            raise ValueError("ReAct agent requires valid Anthropic API key")
        
        # Initialize MCP client and tools
        self.mcp_client = None
        self.tools = []
        
        # Initialize the workflow
        self.workflow = None
        
    async def _init_mcp_client_and_workflow(self):
        """Initialize MCP client connection, tools, and workflow"""
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
        
        # Build the workflow if not already built
        if not self.workflow:
            self.workflow = self._build_react_workflow()
            logger.debug("✅ LangGraph ReAct workflow created")
        
    def _build_react_workflow(self) -> StateGraph:
        """Build the custom LangGraph ReAct workflow"""
        workflow = StateGraph(ReActState)
        
        # Add nodes
        workflow.add_node("reasoning", self._reasoning_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("process_tool_output", self._process_tool_output_node)
        workflow.add_node("final_analysis", self._final_analysis_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow flow
        workflow.set_entry_point("reasoning")
        
        # Reasoning node decides whether to use tools or finish
        workflow.add_conditional_edges(
            "reasoning",
            self._should_continue_or_finish,
            {
                "tools": "tools",
                "final_analysis": "final_analysis",
                "error": "error_handler"
            }
        )
        
        # After tool execution, process the output
        workflow.add_edge("tools", "process_tool_output")
        
        # After processing tool output, go back to reasoning
        workflow.add_edge("process_tool_output", "reasoning")
        
        # Final nodes
        workflow.add_edge("final_analysis", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _reasoning_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Reasoning node - LLM decides what to do next"""
        logger.debug("🧠 REASONING NODE: Analyzing situation and deciding next action")
        
        try:
            # Create system message for reasoning
            system_msg = SystemMessage(content="""You are a Public Health Data Analyst AI Agent specializing in epidemiological surveillance and dashboard generation.

Your mission is to generate a comprehensive public health dashboard with current epidemiological analysis, including:
- Executive situation overview with key metrics and trends
- Risk assessment based on epidemiological data and trend analysis  
- Evidence-based recommendations for public health officials
- Policy-compliant guidance aligned with official guidelines

Available tools:
- fetch_epi_signal: Get epidemiological data (COVID cases, symptoms, doctor visits, etc.)
- detect_rising_trend: Analyze time series data for rising trends

Analysis approach:
1. Start by fetching key epidemiological signals (COVID cases, symptoms, healthcare utilization)
2. Analyze trends using detect_rising_trend for concerning patterns
3. Once you have sufficient data, provide comprehensive final dashboard analysis

Current state analysis:
- Epidemiological signals collected: {signal_count}
- Trend analyses completed: {trend_count}
- Tools used so far: {tools_used}

Decision rules:
- If no data collected yet, start with fetch_epi_signal for key indicators
- If you have signal data but no trend analysis, use detect_rising_trend
- If you have both signals and trends, proceed to final analysis
- If analysis_complete is True, proceed to final analysis

Respond with either:
1. Tool calls to gather more data
2. "ANALYSIS_COMPLETE" if ready for final synthesis""".format(
                signal_count=len(state.get("epi_signals", [])),
                trend_count=len(state.get("trend_analyses", [])),
                tools_used=", ".join(state.get("tools_used", [])) if state.get("tools_used") else "none"
            ))
            
            # Add conversation context
            messages = [system_msg] + state["messages"]
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            
            # Update state with reasoning
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [response]
            new_state["reasoning_steps"] = state.get("reasoning_steps", []) + [f"Reasoning step: {response.content[:100]}..."]
            
            logger.debug(f"Reasoning response: {response.content[:200]}...")
            return new_state
            
        except Exception as e:
            logger.error(f"❌ Error in reasoning node: {str(e)}")
            error_state = state.copy()
            error_state["error_message"] = f"Reasoning failed: {str(e)}"
            return error_state
    
    def _should_continue_or_finish(self, state: Dict[str, Any]) -> str:
        """Determine whether to continue with tools, finish, or handle error"""
        if state.get("error_message"):
            return "error"
        
        # Check if we should finish analysis
        if state.get("analysis_complete") or "ANALYSIS_COMPLETE" in str(state["messages"][-1].content):
            return "final_analysis"
        
        # Check if the last message contains tool calls
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Check for sufficient data to conclude
        if len(state.get("epi_signals", [])) >= 2 and len(state.get("trend_analyses", [])) >= 1:
            return "final_analysis"
        
        # If reasoning suggests tool use, continue with tools
        last_content = str(last_message.content).lower()
        if any(tool_name in last_content for tool_name in ["fetch_epi_signal", "detect_rising_trend"]):
            return "tools"
        
        # Default to final analysis if unclear
        return "final_analysis"
    
    async def _process_tool_output_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process tool outputs and store structured data in state"""
        logger.debug("🔧 PROCESSING TOOL OUTPUT: Extracting and storing structured data")
        
        try:
            new_state = state.copy()
            
            # Get the last tool message
            tool_messages = [msg for msg in state["messages"] if hasattr(msg, 'name')]
            if not tool_messages:
                return new_state
            
            last_tool_message = tool_messages[-1]
            tool_name = getattr(last_tool_message, 'name', 'unknown')
            tool_content = str(last_tool_message.content)
            
            logger.debug(f"Processing output from tool: {tool_name}")
            
            # Update tools used
            if tool_name not in new_state.get("tools_used", []):
                new_state["tools_used"] = new_state.get("tools_used", []) + [tool_name]
            
            # Process fetch_epi_signal outputs
            if tool_name == "fetch_epi_signal":
                signal_data = self._parse_epi_signal_output(tool_content)
                if signal_data:
                    new_state["epi_signals"] = new_state.get("epi_signals", []) + [signal_data.dict()]
                    logger.debug(f"Stored epidemiological signal: {signal_data.signal_name}")
            
            # Process detect_rising_trend outputs
            elif tool_name == "detect_rising_trend":
                trend_data = self._parse_trend_analysis_output(tool_content)
                if trend_data:
                    new_state["trend_analyses"] = new_state.get("trend_analyses", []) + [trend_data.dict()]
                    logger.debug(f"Stored trend analysis: {trend_data.signal_name}")
            
            return new_state
            
        except Exception as e:
            logger.error(f"❌ Error processing tool output: {str(e)}")
            error_state = state.copy()
            error_state["error_message"] = f"Tool output processing failed: {str(e)}"
            return error_state
    
    def _parse_epi_signal_output(self, content: str) -> Optional[EpiSignalData]:
        """Parse epidemiological signal data from tool output"""
        try:
            # Try to extract signal information from content
            import json
            import re
            
            # Look for signal name
            signal_name = "unknown_signal"
            for known_signal in ["confirmed_7dav_incidence_prop", "smoothed_wcli", "smoothed_adj_cli", "deaths_7dav_incidence_prop"]:
                if known_signal in content:
                    signal_name = known_signal
                    break
            
            # Map signal names to display names
            signal_display_names = {
                "confirmed_7dav_incidence_prop": "COVID-19 Case Rates",
                "smoothed_wcli": "COVID-Like Symptoms",
                "smoothed_adj_cli": "COVID-Related Doctor Visits",
                "deaths_7dav_incidence_prop": "COVID-19 Death Rates"
            }
            
            return EpiSignalData(
                signal_name=signal_name,
                display_name=signal_display_names.get(signal_name, signal_name),
                description=f"Epidemiological data for {signal_display_names.get(signal_name, signal_name)}",
                geographic_areas=["US"],  # Default for Delphi data
                data_points=[],  # Could extract from content if needed
                trend_direction="unknown",
                data_quality="high",
                fetch_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse epi signal output: {str(e)}")
            return None
    
    def _parse_trend_analysis_output(self, content: str) -> Optional[TrendAnalysisData]:
        """Parse trend analysis data from tool output"""
        try:
            import json
            import re
            
            # Try to extract trend information
            rising_periods = 0
            total_periods = 0
            signal_name = "unknown_signal"
            
            # Look for JSON patterns
            json_match = re.search(r'\{[^{}]*"rising_periods"[^{}]*\}', content)
            if json_match:
                trend_data = json.loads(json_match.group())
                rising_periods = trend_data.get("rising_periods", 0)
                total_periods = trend_data.get("total_periods", 0)
            
            # Determine risk level
            if total_periods > 0:
                rise_ratio = rising_periods / total_periods
                if rise_ratio > 0.7:
                    risk_level = "high"
                elif rise_ratio > 0.4:
                    risk_level = "medium"
                else:
                    risk_level = "low"
            else:
                risk_level = "unknown"
            
            return TrendAnalysisData(
                signal_name=signal_name,
                rising_periods=rising_periods,
                total_periods=total_periods,
                risk_level=risk_level,
                analysis_timestamp=datetime.now().isoformat(),
                statistical_evidence={"rising_ratio": rising_periods / max(total_periods, 1)}
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse trend analysis output: {str(e)}")
            return None
    
    async def _final_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final dashboard analysis from collected structured data"""
        logger.debug("📊 FINAL ANALYSIS: Generating dashboard from structured data")
        
        try:
            # Get policy document file IDs
            policy_file_ids = await self._get_policy_file_ids()
            
            # Build comprehensive prompt using structured data
            analysis_prompt = self._build_final_analysis_prompt(state, policy_file_ids)
            
            # Generate final dashboard summary
            system_content = """Generate a comprehensive public health dashboard summary based on the structured epidemiological data collected.

Focus on:
- Executive situation overview
- Key epidemiological findings with specific metrics
- Risk assessment based on trend analysis
- Actionable recommendations for public health officials

IMPORTANT: You have access to policy documents that contain official public health guidelines. Use these policy documents to:
1. Ensure recommendations align with official public health protocols
2. Reference specific policy guidelines when making recommendations
3. Cross-reference epidemiological findings with established policy frameworks
4. Provide policy-compliant actionable guidance

Use the structured data provided to create specific, evidence-based insights that are grounded in official public health policy."""
            
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=analysis_prompt)
            ]
            
            # Add policy files to the message if available
            if policy_file_ids:
                logger.debug(f"📄 Including {len(policy_file_ids)} policy documents in analysis")
                # Use direct Anthropic client for file-enabled message
                response = await self._invoke_with_files(messages, policy_file_ids)
            else:
                logger.debug("📄 No policy documents found, proceeding without files")
                response = await self.llm.ainvoke(messages)
            
            # Build structured outputs from state data
            final_state = state.copy()
            
            # Extract text content from Claude response (handle thinking + text format)
            dashboard_text = ""
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    # Handle Claude thinking format - extract just the text parts
                    for item in response.content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            dashboard_text += item.get('text', '')
                        elif hasattr(item, 'text'):
                            dashboard_text += item.text
                else:
                    dashboard_text = str(response.content)
            else:
                dashboard_text = str(response)
            
            final_state["dashboard_summary"] = dashboard_text
            final_state["risk_assessment"] = self._build_risk_assessment_from_state(state)
            final_state["recommendations"] = self._build_recommendations_from_state(state)
            final_state["analysis_complete"] = True
            final_state["messages"] = state["messages"] + [response]
            
            logger.debug("✅ Final analysis completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Error in final analysis: {str(e)}")
            error_state = state.copy()
            error_state["error_message"] = f"Final analysis failed: {str(e)}"
            return error_state
    
    async def _get_policy_file_ids(self) -> List[str]:
        """Get file IDs for policy documents from Anthropic Files API"""
        if not self.anthropic_client:
            logger.warning("⚠️ Anthropic client not initialized, cannot fetch policy files")
            return []
        
        try:
            logger.debug("📋 Fetching uploaded files from Anthropic...")
            files_response = self.anthropic_client.beta.files.list()
            
            if not hasattr(files_response, 'data') or not files_response.data:
                logger.debug("📭 No files found in Anthropic account")
                return []
            
            # Filter for policy brief files
            policy_files = []
            for file_obj in files_response.data:
                filename = getattr(file_obj, 'filename', getattr(file_obj, 'id', ''))
                if filename.startswith('policy-brief_covid-19'):
                    policy_files.append(file_obj.id)
                    logger.debug(f"📄 Found policy document: {filename} (ID: {file_obj.id})")
            
            logger.debug(f"✅ Found {len(policy_files)} policy documents")
            return policy_files
            
        except Exception as e:
            logger.error(f"❌ Error fetching policy files: {str(e)}")
            return []
    
    async def _invoke_with_files(self, messages: List[BaseMessage], file_ids: List[str]) -> BaseMessage:
        """Invoke Claude with file attachments using LangChain ChatAnthropic"""
        try:
            logger.debug(f"🤖 Using LangChain ChatAnthropic with {len(file_ids)} policy documents...")
            
            # Create a ChatAnthropic instance with files API enabled
            files_llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=1.0,
                max_tokens=4000,
                betas=["files-api-2025-04-14"],
                api_key=self.anthropic_client.api_key
            )
            
            # Convert LangChain messages to the proper format with file attachments
            converted_messages = []
            
            for msg in messages:
                if isinstance(msg, SystemMessage):
                    # Keep system messages as-is
                    converted_messages.append(msg)
                elif isinstance(msg, HumanMessage):
                    # Build content list with text and document attachments
                    content = [{"type": "text", "text": msg.content}]
                    
                    # Add each policy document
                    for file_id in file_ids:
                        content.append({
                            "type": "document", 
                            "source": {"type": "file", "file_id": file_id}
                        })
                    
                    # Create a new HumanMessage with the file content structure
                    from langchain_core.messages import HumanMessage as LCHumanMessage
                    file_message = LCHumanMessage(content=content)
                    converted_messages.append(file_message)
                else:
                    converted_messages.append(msg)
            
            # Invoke with file attachments
            response = await files_llm.ainvoke(converted_messages)
            logger.debug(f"✅ Successfully invoked Claude with {len(file_ids)} policy documents")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error invoking Claude with files: {str(e)}")
            # Fallback to regular LangChain call without files
            logger.debug("🔄 Falling back to regular LangChain call without files")
            return await self.llm.ainvoke(messages)

    def _build_final_analysis_prompt(self, state: Dict[str, Any], policy_file_ids: Optional[List[str]] = None) -> str:
        """Build comprehensive analysis prompt from structured state data"""
        prompt_parts = [
            "Generate a comprehensive public health dashboard based on the following structured data:\n"
        ]
        
        # Add policy document information if available
        if policy_file_ids:
            prompt_parts.append(f"POLICY DOCUMENTS AVAILABLE: {len(policy_file_ids)} COVID-19 policy briefs are attached to this message.")
            prompt_parts.append("Please reference these policy documents to ensure your recommendations align with official public health guidelines.")
            prompt_parts.append("")
        
        # Epidemiological signals summary
        if state.get("epi_signals"):
            prompt_parts.append("EPIDEMIOLOGICAL SIGNALS:")
            for signal in state["epi_signals"]:
                prompt_parts.append(f"- {signal.get('display_name')} ({signal.get('signal_name')})")
                prompt_parts.append(f"  Data quality: {signal.get('data_quality')}")
                prompt_parts.append(f"  Fetched: {signal.get('fetch_timestamp')}")
            prompt_parts.append("")
        
        # Trend analyses summary
        if state.get("trend_analyses"):
            prompt_parts.append("TREND ANALYSES:")
            for trend in state["trend_analyses"]:
                prompt_parts.append(f"- Signal: {trend.get('signal_name')}")
                prompt_parts.append(f"  Rising periods: {trend.get('rising_periods')}/{trend.get('total_periods')}")
                prompt_parts.append(f"  Risk level: {trend.get('risk_level')}")
            prompt_parts.append("")
        
        # Analysis context
        prompt_parts.append(f"Tools used: {', '.join(state.get('tools_used', []))}")
        prompt_parts.append(f"Analysis timestamp: {state.get('timestamp')}")
        
        return "\n".join(prompt_parts)
    
    def _build_risk_assessment_from_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Build risk assessment from structured state data"""
        # Calculate overall risk based on trend analyses
        trend_analyses = state.get("trend_analyses", [])
        high_risk_trends = [t for t in trend_analyses if t.get("risk_level") == "high"]
        medium_risk_trends = [t for t in trend_analyses if t.get("risk_level") == "medium"]
        
        if len(high_risk_trends) >= 2:
            overall_risk = "high"
        elif len(high_risk_trends) >= 1 or len(medium_risk_trends) >= 2:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        epi_signals = state.get("epi_signals", [])
        return {
            "overall_risk_level": overall_risk,
            "confidence_level": "high" if len(epi_signals) >= 2 else "medium",
            "key_risk_factors": [t.get("signal_name") for t in high_risk_trends],
            "geographic_distribution": "national",  # Delphi data is national
            "trend_trajectory": "rising" if high_risk_trends else "stable",
            "priority_signals": [s.get("signal_name") for s in epi_signals[:3]]
        }
    
    def _build_recommendations_from_state(self, state: Dict[str, Any]) -> List[str]:
        """Build recommendations from structured state data"""
        recommendations = []
        
        # Generate recommendations based on findings
        trend_analyses = state.get("trend_analyses", [])
        epi_signals = state.get("epi_signals", [])
        
        if len(trend_analyses) > 0:
            high_risk_trends = [t for t in trend_analyses if t.get("risk_level") == "high"]
            
            if high_risk_trends:
                trend_names = ', '.join(t.get('signal_name', 'unknown') for t in high_risk_trends)
                recommendations.append(
                    f"HIGH PRIORITY: Enhanced surveillance for rising epidemiological trends. "
                    f"Multiple signals showing concerning upward trends: {trend_names}. "
                    f"Target: Public Health Officials. Timeframe: Immediate."
                )
        
        if len(epi_signals) > 0:
            recommendations.append(
                f"MEDIUM PRIORITY: Continue monitoring epidemiological indicators. "
                f"Active monitoring of {len(epi_signals)} epidemiological signals. "
                f"Target: Epidemiologists. Timeframe: Ongoing."
            )
        
        # Ensure we have at least one recommendation
        if not recommendations:
            recommendations.append(
                "LOW PRIORITY: Maintain routine epidemiological surveillance. "
                "Continue standard public health monitoring protocols. "
                "Target: Public Health Officials. Timeframe: Ongoing."
            )
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def _error_handler_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors in the workflow"""
        error_msg = state.get("error_message") or "Unknown error occurred"
        
        error_state = state.copy()
        error_state["dashboard_summary"] = f"""
⚠️ **Dashboard Generation Error**

An error occurred while generating the epidemiological dashboard:
{error_msg}

**Partial Data Collected:**
- Epidemiological signals: {len(state.get("epi_signals", []))}
- Trend analyses: {len(state.get("trend_analyses", []))}
- Tools used: {', '.join(state.get("tools_used", [])) if state.get("tools_used") else 'none'}

**Recommended Actions:**
- Check MCP server connectivity (http://{self.mcp_host}:{self.mcp_port})
- Verify API credentials
- Review system logs for detailed error information
"""
        
        return error_state

    async def generate_dashboard(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Generate a dashboard summary using LangGraph ReAct workflow with typed data storage"""
        logger.info(f"🚀 LANGGRAPH REACT WORKFLOW: Starting epidemiological dashboard generation")
        logger.debug(f"Date range: {start_date} to {end_date}")
        logger.debug(f"Agent configuration - LLM: {type(self.llm).__name__ if self.llm else 'None'}")
        logger.debug(f"Agent configuration - MCP: {self.mcp_host}:{self.mcp_port}")
        
        # Build the dashboard generation request with date context
        dashboard_request = "Generate comprehensive public health dashboard with current epidemiological analysis"
        if start_date or end_date:
            date_context = f" focusing on data"
            if start_date:
                date_context += f" from {start_date}"
            if end_date:
                date_context += f" through {end_date}"
            else:
                date_context += " through current date"
            dashboard_request += date_context
        
        try:
            # Initialize MCP client and workflow
            await self._init_mcp_client_and_workflow()
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=dashboard_request)],
                "current_request": dashboard_request,
                "epi_signals": [],
                "trend_analyses": [],
                "reasoning_steps": [],
                "tools_used": [],
                "analysis_complete": False,
                "dashboard_summary": None,
                "risk_assessment": {},
                "recommendations": [],
                "error_message": None,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("🔄 Starting LangGraph ReAct workflow...")
            
            # Run the workflow
            config = {"configurable": {"thread_id": "react_dashboard_session"}}
            final_state = await self.workflow.ainvoke(initial_state, config=config)
            
            logger.info("✅ LangGraph ReAct workflow completed")
            
            # MCP client will auto-cleanup when async loop exits
            
            # Build final result from typed state data
            final_result = {
                "dashboard_summary": final_state.get("dashboard_summary", "No summary generated"),
                "timestamp": final_state.get("timestamp"),
                "success": not bool(final_state.get("error_message")),
                "error": final_state.get("error_message"),
                "agent_type": "react",
                "tools_used": final_state.get("tools_used", []),
                
                # Enhanced structured data directly from typed state
                "alerts": [],  # ReAct agent focuses on epidemiological data, not alerts
                "rising_trends": self._format_rising_trends_from_state(final_state),
                "epidemiological_signals": self._format_epi_signals_from_state(final_state),
                "risk_assessment": final_state.get("risk_assessment", {}),
                "recommendations": final_state.get("recommendations", [])
            }
            
            logger.info("🎉 LangGraph ReAct dashboard generation completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ LangGraph ReAct dashboard generation failed: {str(e)}")
            
            # MCP client will auto-cleanup when async loop exits
            
            return {
                "dashboard_summary": f"⚠️ ReAct dashboard generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e),
                "agent_type": "react",
                "tools_used": [],
                "alerts": [],
                "rising_trends": [],
                "epidemiological_signals": [],
                "risk_assessment": {"overall_risk_level": "unknown", "error": str(e)},
                "recommendations": []
            }
    
    def _format_rising_trends_from_state(self, state: Dict) -> List[Dict]:
        """Format rising trends from typed state data"""
        formatted_trends = []
        
        for trend in state.get("trend_analyses", []):
            formatted_trends.append({
                "signal_name": trend.get("signal_name", "unknown"),
                "trend_direction": "rising" if trend.get("rising_periods", 0) > 0 else "stable",
                "rising_periods": trend.get("rising_periods", 0),
                "total_periods": trend.get("total_periods", 0),
                "risk_level": trend.get("risk_level", "unknown"),
                "statistical_evidence": trend.get("statistical_evidence", {}),
                "detected_via": "detect_rising_trend_tool",
                "analysis_timestamp": trend.get("analysis_timestamp")
            })
        
        return formatted_trends
    
    def _format_epi_signals_from_state(self, state: Dict) -> List[Dict]:
        """Format epidemiological signals from typed state data"""
        formatted_signals = []
        
        for signal in state.get("epi_signals", []):
            formatted_signals.append({
                "signal_name": signal.get("signal_name", "unknown"),
                "display_name": signal.get("display_name", "Unknown Signal"),
                "description": signal.get("description", ""),
                "data_source": "delphi_epidata_api",
                "geographic_areas": signal.get("geographic_areas", []),
                "current_value": signal.get("current_value"),
                "trend_direction": signal.get("trend_direction", "unknown"),
                "data_quality": signal.get("data_quality", "unknown"),
                "fetch_timestamp": signal.get("fetch_timestamp"),
                "status": "analyzed"
            })
        
        return formatted_signals


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