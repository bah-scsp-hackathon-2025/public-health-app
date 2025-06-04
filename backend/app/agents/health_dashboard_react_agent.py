#!/usr/bin/env python3
"""
Public Health Dashboard ReAct Agent using LangGraph

This agent uses a ReAct (Reasoning + Acting) pattern to:
Phase 1: Fetch and analyze epidemiological data using real APIs
Phase 2: Generate comprehensive dashboard summaries with actionable insights

The agent demonstrates modern LLM workflows with tool integration for public health analysis.
"""

import anthropic
import asyncio
import certifi
import httpx
import logging
import os
import ssl
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolNode  # Not using separate tool node anymore
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field
from operator import add
from typing import Dict, List, Optional, Annotated, Any, TypedDict

# Langfuse imports
from langfuse.callback import CallbackHandler


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
    
    # Date constraints
    start_date: str  # Format: YYYY-MM-DD
    end_date: str    # Format: YYYY-MM-DD
    
    # Tool data storage
    epi_signals: Annotated[List[Dict[str, Any]], add]  # Store as dicts for JSON compatibility
    trend_analyses: Annotated[List[Dict[str, Any]], add]  # Store as dicts for JSON compatibility
    fetch_epi_signal_data: Annotated[List[Dict[str, Any]], add]  # Store raw fetch_epi_signal results for trends output
    
    # Tool execution state
    tool_results: List[Dict[str, Any]]  # Raw tool results from reasoning node (don't accumulate, always replace)
    has_tool_results: bool  # Flag to indicate if tool results need processing
    
    # Analysis state
    reasoning_steps: Annotated[List[str], add]
    tools_used: Annotated[List[str], add]
    tool_call_counts: Dict[str, int]  # Track how many times each tool has been called
    analysis_complete: bool
    
    # Final outputs
    dashboard_summary: Optional[str]
    risk_assessment: Dict[str, Any]
    recommendations: Annotated[List[Dict[str, Any]], add]
    error_message: Optional[str]
    timestamp: str


class PublicHealthReActAgent:
    """LangGraph ReAct agent for public health dashboard generation using epidemiological data"""
    
    def __init__(self):
        # Initialize MCP client and tools
        self.mcp_client = None
        self.tools = []
        
        # Initialize the workflow
        self.workflow = None
        
        # Initialize Langfuse callback handler
        self.langfuse_handler = None

        # Initialize Langfuse tracing if configured
        self._setup_langfuse_tracing()
        # Load MCP configuration from environment variables
        self.mcp_host = settings.mcp_server_host if hasattr(settings, 'mcp_server_host') else os.getenv("MCP_SERVER_HOST", "localhost")
        self.mcp_port = int(settings.mcp_server_port if hasattr(settings, 'mcp_server_port') else os.getenv("MCP_SERVER_PORT", "8000"))
        
        # Get API keys from settings (keep both for future use)
        # openai_key = settings.openai_api_key if settings.openai_api_key else None
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
                betas=["files-api-2025-04-14"],
                api_key=anthropic_key
            )
            # Initialize direct Anthropic client for Files API with SSL configuration
            # Create custom httpx client with proper SSL configuration
            ssl_verify = settings.ssl_verify if hasattr(settings, 'ssl_verify') else True
            if ssl_verify:
                # Use certifi CA bundle for SSL verification
                ca_bundle = settings.ssl_ca_bundle if hasattr(settings, 'ssl_ca_bundle') and settings.ssl_ca_bundle else certifi.where()
                ssl_context = ssl.create_default_context(cafile=ca_bundle)
                verify_setting = ssl_context
                logger.debug(f"🔒 SSL verification enabled with CA bundle: {ca_bundle}")
            else:
                verify_setting = False
                logger.warning("⚠️ SSL verification disabled - this is not recommended for production")
            
            custom_httpx_client = httpx.Client(
                verify=verify_setting,
                timeout=httpx.Timeout(60.0, read=60.0, write=60.0, connect=10.0)
            )
            self.anthropic_client = anthropic.Anthropic(
                api_key=anthropic_key,
                http_client=custom_httpx_client
            )
        else:
            print("⚠️  Anthropic API key not found or invalid. ReAct agent requires valid Anthropic API key.")
            raise ValueError("ReAct agent requires valid Anthropic API key")

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
                    session_id=f"react-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    user_id="public-health-system",
                    metadata={
                        "agent_type": "react",
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
        """Build the custom LangGraph ReAct workflow with unified reasoning+tools node"""
        workflow = StateGraph(ReActState)
        
        # Add nodes (reasoning now handles tools directly)
        workflow.add_node("reasoning", self._reasoning_node)
        workflow.add_node("process_tool_output", self._process_tool_output_node)
        workflow.add_node("final_analysis", self._final_analysis_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow flow
        workflow.set_entry_point("reasoning")
        
        # Reasoning node decides whether to process tool output, finish, or handle error
        workflow.add_conditional_edges(
            "reasoning",
            self._should_continue_or_finish,
            {
                "process_tools": "process_tool_output",
                "final_analysis": "final_analysis",
                "error": "error_handler"
            }
        )
        
        # After processing tool output, go back to reasoning
        workflow.add_edge("process_tool_output", "reasoning")
        
        # Final nodes
        workflow.add_edge("final_analysis", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _reasoning_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Unified reasoning node - LLM decides what to do next and executes tools directly"""
        logger.debug("🧠 REASONING NODE: Analyzing situation and deciding next action")
        
        try:
            # Create system message for reasoning
            system_msg = SystemMessage(content="""You are a Public Health Data Analyst AI Agent specializing in epidemiological surveillance and compiling data from external sources for dashboards.

Your mission is to assemble a comprehensive public health dashboard from the external sources and their epidemiological analysis, including:
- Executive situation overview with key metrics and trends
- Risk assessment based on the acquired epidemiological data and trend analysis  
- Evidence-based recommendations for public health officials
- Policy-compliant guidance aligned with official guidelines

Available tools:
- fetch_epi_signal: Get epidemiological data (for various signals and date ranges)
- detect_rising_trend: Analyze time series data for rising trends

CRITICAL DATE CONSTRAINTS:
- Analysis period: {start_date} to {end_date}
- ALL tool calls must use these exact dates as start_time and end_time parameters
- Date format for tools: YYYYMMDD (e.g., "20200201" for 2020-02-01)
- Do NOT request data outside this date range under any circumstances

Analysis approach:
1. Start by fetching key epidemiological signals (described by the fetch_epi_signal tool)
2. Analyze trends using detect_rising_trend for concerning patterns  
3. Once you have sufficient data obtained, provide comprehensive final dashboard analysis

Current state analysis:
- Analysis period: {start_date} to {end_date}
- Required date format for tools: {start_date_tool} to {end_date_tool} (YYYYMMDD)
- Epidemiological signals collected: {signal_count}
- Trend analyses completed: {trend_count}
- Tools used so far: {tools_used}
- Tool call limits: fetch_epi_signal ({fetch_calls}/6), detect_rising_trend ({trend_calls}/6)

Decision rules:
- If no data collected yet, start with fetch_epi_signal for key indicators (max 6 calls)
- If you have signal data but no trend analysis, use detect_rising_trend (max 6 calls)
- If you have both signals and trends, proceed to final analysis
- If analysis_complete is True, proceed to final analysis
- If tool call limits reached (6 each), proceed to final analysis with available data
- ALWAYS use start_time={start_date_tool} and end_time={end_date_tool} in ALL tool calls
- DO NOT generate or create any data, MUST only rely on the tools to get any signals and trends and data points
- You MUST use the tools, and ONLY the tools as a data source for signals and trends and data points

EXAMPLE TOOL CALL (with correct date format):
fetch_epi_signal(signal="confirmed_7dav_incidence_prop", time_type="day", geo_type="state", start_time="{start_date_tool}", end_time="{end_date_tool}")

Respond with either:
1. Tool calls to gather initial or more data (respecting call limits and date constraints)
2. "ANALYSIS_COMPLETE" if ready for final synthesis""".format(
                start_date=state.get("start_date", "2020-02-01"),
                end_date=state.get("end_date", "2022-02-01"),
                start_date_tool=state.get("start_date", "2020-02-01").replace("-", ""),
                end_date_tool=state.get("end_date", "2022-02-01").replace("-", ""),
                signal_count=len(state.get("epi_signals", [])),
                trend_count=len(state.get("trend_analyses", [])),
                tools_used=", ".join(state.get("tools_used", [])) if state.get("tools_used") else "none",
                fetch_calls=state.get("tool_call_counts", {}).get("fetch_epi_signal", 0),
                trend_calls=state.get("tool_call_counts", {}).get("detect_rising_trend", 0)
            ))
            
            # Add conversation context
            messages = [system_msg] + state["messages"]
            
            # Bind tools to the LLM and get response with Langfuse callback if available
            llm_with_tools = self.llm.bind_tools(self.tools)
            callbacks = [self.langfuse_handler] if self.langfuse_handler else []
            config = {"callbacks": callbacks} if callbacks else {}
            response = await llm_with_tools.ainvoke(messages, config=config)
            
            # Prepare state updates
            reasoning_step = f"Reasoning step: {response.content[:100]}..."
            
            # Check if the LLM made tool calls
            if response.tool_calls:
                logger.debug(f"🔧 LLM requested {len(response.tool_calls)} tool calls")
                
                # Check current limits for informational purposes
                current_counts = state.get("tool_call_counts", {})
                
                # Execute all requested tools first, then count only successful ones
                tool_results = []
                tool_messages = []
                successful_calls_by_tool = {}  # Track successful calls per tool type
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    current_count = current_counts.get(tool_name, 0)
                    
                    # Check if we're already at limit for this tool
                    if current_count >= 6:
                        logger.warning(f"⚠️ Skipping {tool_name} call - limit reached (6/6)")
                        # Create an error message for the skipped call
                        error_result = f"Tool call skipped: {tool_name} limit reached (6/6)"
                        tool_result = {
                            "tool_call_id": tool_call.get('id', f"call_{tool_call['name']}"),
                            "tool_name": tool_name,
                            "tool_args": tool_call['args'],
                            "result": error_result,
                            "skipped": True
                        }
                        tool_results.append(tool_result)
                        
                        tool_message = ToolMessage(
                            content=error_result,
                            tool_call_id=tool_call.get('id', f"call_{tool_call['name']}"),
                            name=tool_name
                        )
                        tool_messages.append(tool_message)
                        continue
                    
                    logger.debug(f"Executing tool: {tool_name} with args: {tool_call['args']}")
                    
                    # Validate date parameters for tools that use dates
                    if tool_name in ["fetch_epi_signal", "detect_rising_trend"]:
                        expected_start = state.get("start_date", "2020-02-01").replace("-", "")
                        expected_end = state.get("end_date", "2022-02-01").replace("-", "")
                        
                        tool_args = tool_call['args']
                        if 'start_time' in tool_args and tool_args['start_time'] != expected_start:
                            logger.warning(f"⚠️ Tool {tool_name} using start_time {tool_args['start_time']}, expected {expected_start}")
                        if 'end_time' in tool_args and tool_args['end_time'] != expected_end:
                            logger.warning(f"⚠️ Tool {tool_name} using end_time {tool_args['end_time']}, expected {expected_end}")
                    
                    # Find the tool by name
                    tool = next((t for t in self.tools if t.name == tool_call['name']), None)
                    if tool:
                        try:
                            # Execute the tool
                            result = await tool.ainvoke(tool_call['args'])
                            
                            # Check if the result contains useful data
                            has_useful_data = self._check_tool_result_has_data(tool_name, result)
                            
                            tool_result = {
                                "tool_call_id": tool_call.get('id', f"call_{tool_call['name']}"),
                                "tool_name": tool_name,
                                "tool_args": tool_call['args'],
                                "result": result,
                                "has_data": has_useful_data
                            }
                            tool_results.append(tool_result)
                            
                            # Create ToolMessage for the conversation
                            tool_message = ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call.get('id', f"call_{tool_call['name']}"),
                                name=tool_name
                            )
                            tool_messages.append(tool_message)
                            
                            # Only count successful calls with data against the limit
                            if has_useful_data:
                                successful_calls_by_tool[tool_name] = successful_calls_by_tool.get(tool_name, 0) + 1
                                logger.debug(f"✅ Tool {tool_name} executed successfully with data (counted)")
                            else:
                                logger.debug(f"⚠️ Tool {tool_name} executed but returned no useful data (not counted)")
                        except Exception as e:
                            logger.error(f"❌ Tool {tool_name} failed: {str(e)}")
                            error_result = f"Error: {str(e)}"
                            tool_result = {
                                "tool_call_id": tool_call.get('id', f"call_{tool_call['name']}"),
                                "tool_name": tool_name,
                                "tool_args": tool_call['args'],
                                "result": error_result,
                                "has_data": False  # Failed calls don't count
                            }
                            tool_results.append(tool_result)
                            
                            # Create ToolMessage for the error
                            tool_message = ToolMessage(
                                content=error_result,
                                tool_call_id=tool_call.get('id', f"call_{tool_call['name']}"),
                                name=tool_name
                            )
                            tool_messages.append(tool_message)
                            # Failed calls don't count against the limit
                    else:
                        logger.error(f"❌ Tool {tool_name} not found")
                        error_result = f"Error: Tool {tool_name} not found"
                        tool_result = {
                            "tool_call_id": tool_call.get('id', f"call_{tool_call['name']}"),
                            "tool_name": tool_name,
                            "tool_args": tool_call['args'],
                            "result": error_result,
                            "has_data": False  # Tool not found doesn't count
                        }
                        tool_results.append(tool_result)
                        
                        # Create ToolMessage for the error
                        tool_message = ToolMessage(
                            content=error_result,
                            tool_call_id=tool_call.get('id', f"call_{tool_call['name']}"),
                            name=tool_name
                        )
                        tool_messages.append(tool_message)
                
                # Update tool call counts only for successful calls with data
                updated_counts = current_counts.copy()
                for tool_name, success_count in successful_calls_by_tool.items():
                    updated_counts[tool_name] = updated_counts.get(tool_name, 0) + success_count
                
                # Return partial state update - LangGraph will merge automatically
                successful_count = sum(successful_calls_by_tool.values())
                logger.debug(f"✅ Stored {len(tool_results)} tool results ({successful_count} successful with data)")
                logger.debug(f"📊 Updated tool call counts: {updated_counts}")
                return {
                    "messages": [response] + tool_messages,
                    "tool_results": tool_results,
                    "has_tool_results": True,
                    "reasoning_steps": [reasoning_step],
                    "tool_call_counts": updated_counts
                }
            else:
                # No tool calls made, just add the response
                logger.debug("💭 No tool calls made, proceeding with reasoning only")
                return {
                    "messages": [response],
                    "has_tool_results": False,
                    "reasoning_steps": [reasoning_step]
                }
            
        except Exception as e:
            logger.error(f"❌ Error in reasoning node: {str(e)}")
            return {"error_message": f"Reasoning failed: {str(e)}"}
    
    def _should_continue_or_finish(self, state: Dict[str, Any]) -> str:
        """Determine whether to process tool results, finish, or handle error"""
        if state.get("error_message"):
            return "error"
        
        # Check if we have tool results to process
        if state.get("has_tool_results"):
            return "process_tools"
            
        # Check if we should finish analysis
        if state.get("analysis_complete") or "ANALYSIS_COMPLETE" in str(state["messages"][-1].content):
            return "final_analysis"
        
        # Check tool call limits
        tool_counts = state.get("tool_call_counts", {})
        fetch_count = tool_counts.get("fetch_epi_signal", 0)
        trend_count = tool_counts.get("detect_rising_trend", 0)
        
        # If all tool limits reached, proceed to final analysis
        if fetch_count >= 6 and trend_count >= 6:
            logger.warning("⚠️ All tool call limits reached, proceeding to final analysis")
            return "final_analysis"
        
        # Check for sufficient data to conclude
        if len(state.get("epi_signals", [])) >= 2 and len(state.get("trend_analyses", [])) >= 1:
            return "final_analysis"
        
        # If we have some signals but no trends, and trend tool not maxed out, continue reasoning
        if (len(state.get("epi_signals", [])) > 0 and 
            len(state.get("trend_analyses", [])) == 0 and
            trend_count < 6):
            # Continue reasoning to analyze trends (will trigger tool calls)
            return "final_analysis"  # Let reasoning decide if more tools needed
        
        # Default to final analysis
        return "final_analysis"
    
    def _check_tool_result_has_data(self, tool_name: str, result: Any) -> bool:
        """Check if a tool result contains useful data that should count against limits"""
        try:
            result_str = str(result).lower()
            
            # Check for common error patterns
            error_patterns = [
                "error",
                "failed",
                "no data",
                "empty",
                "null",
                "none",
                "not found",
                "unavailable",
                "timeout",
                "connection",
                "exception"
            ]
            
            # If result contains error patterns, it's not useful data
            for pattern in error_patterns:
                if pattern in result_str:
                    return False
            
            # Tool-specific checks
            if tool_name == "fetch_epi_signal":
                # Check if we got actual signal data
                if isinstance(result, dict):
                    # Look for data indicators in the response
                    has_data_keys = any(key in result for key in ["data", "values", "time_value", "geo_value"])
                    has_records = len(str(result)) > 50  # Reasonable response size
                    return has_data_keys or has_records  # Either data keys OR substantial content
                elif isinstance(result, str):
                    # Look for JSON-like structure indicators or data fields
                    has_json_structure = "{" in result_str and "}" in result_str
                    has_data_fields = any(field in result_str for field in ["time_value", "geo_value", "value"])
                    return (has_json_structure or has_data_fields) and len(result_str) > 50
                    
            elif tool_name == "detect_rising_trend":
                # Check if we got trend analysis data
                if isinstance(result, dict):
                    has_trend_keys = any(key in result for key in ["rising_periods", "total_periods", "status"])
                    return has_trend_keys and result.get("status") == "success"
                elif isinstance(result, str):
                    return "rising_periods" in result_str and "success" in result_str
            
            # Default: if result is substantial (>50 chars) and not just error message
            return len(result_str) > 50 and not any(pattern in result_str for pattern in error_patterns)
            
        except Exception as e:
            logger.debug(f"Error checking tool result data: {e}")
            return False
    
    async def _process_tool_output_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process tool outputs and store structured data in state"""
        logger.debug("🔧 PROCESSING TOOL OUTPUT: Extracting and storing structured data")
        
        try:
            # Process tool results from the reasoning node
            tool_results = state.get("tool_results", [])
            if not tool_results:
                logger.debug("No tool results to process")
                return {"has_tool_results": False}
            
            logger.debug(f"Processing {len(tool_results)} tool results")
            
            # Collect updates to return
            new_tools_used = []
            new_epi_signals = []
            new_trend_analyses = []
            new_fetch_epi_signal_data = []
            
            for tool_result in tool_results:
                tool_name = tool_result.get("tool_name", "unknown")
                tool_content = str(tool_result.get("result", ""))
                has_data = tool_result.get("has_data", False)
                
                logger.debug(f"Processing output from tool: {tool_name}")
                
                # Track new tools used
                if tool_name not in state.get("tools_used", []):
                    new_tools_used.append(tool_name)
                
                # Process fetch_epi_signal outputs
                if tool_name == "fetch_epi_signal":
                    signal_data = self._parse_epi_signal_output(tool_content, tool_result.get("tool_args", {}))
                    if signal_data:
                        new_epi_signals.append(signal_data.dict())
                        logger.debug(f"Stored epidemiological signal: {signal_data.signal_name}")
                    
                    # Store raw fetch_epi_signal data if it has useful data (for trends output)
                    if has_data:
                        raw_result = tool_result.get("result")
                        if raw_result:
                            new_fetch_epi_signal_data.append({
                                "tool_args": tool_result.get("tool_args", {}),
                                "result": raw_result,
                                "timestamp": datetime.now().isoformat()
                            })
                            logger.debug(f"Stored raw fetch_epi_signal data for trends output")
                        else:
                            logger.debug(f"fetch_epi_signal has_data=True but raw_result is empty")
                    else:
                        logger.debug(f"fetch_epi_signal call has_data=False, not storing for trends")
                
                # Process detect_rising_trend outputs
                elif tool_name == "detect_rising_trend":
                    trend_data = self._parse_trend_analysis_output(tool_content, tool_result.get("tool_args", {}))
                    if trend_data:
                        new_trend_analyses.append(trend_data.dict())
                        logger.debug(f"Stored trend analysis: {trend_data.signal_name}")
            
            logger.debug(f"✅ Processed all tool results. New signals: {len(new_epi_signals)}, New trends: {len(new_trend_analyses)}, New fetch data: {len(new_fetch_epi_signal_data)}")
            
            # Return partial state update
            return {
                "tool_results": [],  # Clear tool results after processing
                "has_tool_results": False,
                "tools_used": new_tools_used,  # LangGraph will append to existing list
                "epi_signals": new_epi_signals,  # LangGraph will append to existing list
                "trend_analyses": new_trend_analyses,  # LangGraph will append to existing list
                "fetch_epi_signal_data": new_fetch_epi_signal_data  # LangGraph will append to existing list
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing tool output: {str(e)}")
            return {"error_message": f"Tool output processing failed: {str(e)}"}
    
    def _parse_epi_signal_output(self, content: str, tool_args: Dict[str, Any] = None) -> Optional[EpiSignalData]:
        """Parse epidemiological signal data from tool output"""
        try:
            # Try to extract signal information from content and tool args
            import json
            import re
            
            if tool_args is None:
                tool_args = {}
            
            # Get signal name from tool arguments first (most reliable)
            signal_name = tool_args.get("signal", "unknown_signal")
            
            # If not in tool args, look in content
            if signal_name == "unknown_signal":
                known_signals = [
                    "confirmed_7dav_incidence_prop", 
                    "smoothed_wcli", 
                    "smoothed_adj_cli",
                    "smoothed_whh_cmnty_cli"
                ]
                for known_signal in known_signals:
                    if known_signal in content.lower():
                        signal_name = known_signal
                        break
            
            # Map signal names to display names
            signal_display_names = {
                "confirmed_7dav_incidence_prop": "COVID-19 Case Rates",
                "smoothed_wcli": "COVID-Like Symptoms",
                "smoothed_adj_cli": "COVID-Related Doctor Visits",
                "smoothed_whh_cmnty_cli": "Weekly Hospital Admissions (CLI)",
            }
            
            # Extract geographic info from tool args
            geo_areas = []
            if tool_args.get("geo_value"):
                geo_areas.append(tool_args["geo_value"].upper())
            
            logger.debug(f"✅ Parsed epi signal: {signal_name} for {geo_areas or ['US']}")
            
            return EpiSignalData(
                signal_name=signal_name,
                display_name=signal_display_names.get(signal_name, signal_name),
                description=f"Epidemiological data for {signal_display_names.get(signal_name, signal_name)}",
                geographic_areas=geo_areas or ["US"],  # Use from args or default
                data_points=[],  # Could extract from content if needed
                trend_direction="unknown",
                data_quality="high",
                fetch_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse epi signal output: {str(e)}")
            return None
    
    def _parse_trend_analysis_output(self, content: str, tool_args: Dict[str, Any] = None) -> Optional[TrendAnalysisData]:
        """Parse trend analysis data from tool output"""
        try:
            import json
            import re
            
            # Try to extract trend information
            rising_periods = 0
            total_periods = 0
            signal_name = "unknown_signal"
            trend_strength = "medium"
            
            logger.debug(f"🔍 Parsing trend analysis content: {content[:200]}...")
            
            # First try to parse the entire content as JSON (if it's a JSON response)
            try:
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    trend_data = json.loads(content)
                    rising_periods = trend_data.get("rising_periods", 0)
                    total_periods = trend_data.get("total_periods", 0)
                    signal_name = trend_data.get("signal", trend_data.get("signal_name", "unknown_signal"))
                    if "status" in trend_data and trend_data["status"] == "success":
                        logger.debug(f"✅ Parsed complete JSON: {rising_periods}/{total_periods} rising periods")
                else:
                    raise json.JSONDecodeError("Not a complete JSON", content, 0)
                    
            except json.JSONDecodeError:
                # Try to find JSON patterns in the content
                json_patterns = [
                    r'\{[^{}]*"rising_periods"[^{}]*"total_periods"[^{}]*\}',  # Most specific
                    r'\{[^{}]*"rising_periods"[^{}]*\}',  # Less specific
                    r'\{.*?"rising_periods".*?\}',  # Even more flexible
                ]
                
                for pattern in json_patterns:
                    json_match = re.search(pattern, content, re.DOTALL)
                    if json_match:
                        try:
                            trend_data = json.loads(json_match.group())
                            rising_periods = trend_data.get("rising_periods", 0)
                            total_periods = trend_data.get("total_periods", 0)
                            signal_name = trend_data.get("signal", trend_data.get("signal_name", "unknown_signal"))
                            logger.debug(f"✅ Extracted from JSON pattern: {rising_periods}/{total_periods} rising periods")
                            break
                        except json.JSONDecodeError:
                            continue
                
                # If JSON parsing fails, try to extract numbers from text
                if rising_periods == 0 and total_periods == 0:
                    rising_match = re.search(r'rising[_\s]*periods?[:\s]*(\d+)', content, re.IGNORECASE)
                    total_match = re.search(r'total[_\s]*periods?[:\s]*(\d+)', content, re.IGNORECASE)
                    
                    if rising_match:
                        rising_periods = int(rising_match.group(1))
                    if total_match:
                        total_periods = int(total_match.group(1))
                    
                    logger.debug(f"✅ Extracted from text patterns: {rising_periods}/{total_periods} periods")
            
            # Try to extract signal name from tool arguments first, then content
            if tool_args is None:
                tool_args = {}
                
            # Get signal name from tool args (most reliable source)
            signal_name = tool_args.get("signal", signal_name)
            
            # If still unknown, try to extract from content patterns
            if signal_name == "unknown_signal":
                signal_patterns = [
                    "confirmed_7dav_incidence_prop",
                    "smoothed_wcli", 
                    "smoothed_adj_cli",
                    "smoothed_whh_cmnty_cli"
                ]
                for pattern in signal_patterns:
                    if pattern in content.lower():
                        signal_name = pattern
                        break
            
            # Determine risk level and trend strength
            if total_periods > 0:
                rise_ratio = rising_periods / total_periods
                if rise_ratio > 0.7:
                    risk_level = "high"
                    trend_strength = "strong"
                elif rise_ratio > 0.4:
                    risk_level = "medium"
                    trend_strength = "moderate"
                else:
                    risk_level = "low"
                    trend_strength = "weak"
            else:
                risk_level = "unknown"
                trend_strength = "unknown"
            
            logger.debug(f"✅ Parsed trend analysis: signal={signal_name}, rising={rising_periods}, total={total_periods}, risk={risk_level}")
            
            return TrendAnalysisData(
                signal_name=signal_name,
                rising_periods=rising_periods,
                total_periods=total_periods,
                trend_strength=trend_strength,
                risk_level=risk_level,
                analysis_timestamp=datetime.now().isoformat(),
                statistical_evidence={
                    "rising_ratio": rising_periods / max(total_periods, 1),
                    "raw_content_sample": content[:100] + "..." if len(content) > 100 else content
                }
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse trend analysis output: {str(e)}")
            logger.debug(f"🔍 Content that failed to parse: {content[:200]}...")
            return None
    
    async def _final_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble final dashboard analysis from collected structured data"""
        logger.debug("📊 FINAL ANALYSIS: Generating dashboard from structured data")
        
        try:
            # Get policy document file IDs
            policy_file_ids = await self._get_policy_file_ids()
            
            # Build comprehensive prompt using structured data
            analysis_prompt = self._build_final_analysis_prompt(state, policy_file_ids)
            
            # Assemble final dashboard summary
            system_content = """Assemble a public health dashboard summary based on the structured epidemiological data collected.

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
                callbacks = [self.langfuse_handler] if self.langfuse_handler else []
                config = {"callbacks": callbacks} if callbacks else {}
                response = await self.llm.ainvoke(messages, config=config)
            
            # Build structured outputs from state data
            
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
            
            logger.debug("✅ Final analysis completed successfully")
            return {
                "dashboard_summary": dashboard_text,
                "risk_assessment": self._build_risk_assessment_from_state(state),
                "recommendations": self._build_recommendations_from_state(state),
                "analysis_complete": True,
                "messages": [response]  # LangGraph will handle accumulation with 'add' annotation
            }
            
        except Exception as e:
            logger.error(f"❌ Error in final analysis: {str(e)}")
            return {"error_message": f"Final analysis failed: {str(e)}"}
    
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
                max_tokens=64000,
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
        
        return {
            "dashboard_summary": f"""
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
        }

    async def assemble_dashboard(self, start_date: Optional[str] = "2020-02-01", end_date: Optional[str] = "2022-02-01") -> Dict:
        """Generate a dashboard summary using LangGraph ReAct workflow with typed data storage"""
        logger.info(f"🚀 LANGGRAPH REACT WORKFLOW: Starting epidemiological dashboard generation")
        logger.debug(f"Date range: {start_date} to {end_date}")
        logger.debug(f"Agent configuration - LLM: {type(self.llm).__name__ if self.llm else 'None'}")
        logger.debug(f"Agent configuration - MCP: {self.mcp_host}:{self.mcp_port}")
        
        # Build the dashboard generation request with date context
        dashboard_request = "Assemble a public health dashboard"
        if start_date or end_date:
            date_context = f" on data from external datasets"
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
                "start_date": start_date,
                "end_date": end_date,
                "epi_signals": [],
                "trend_analyses": [],
                "fetch_epi_signal_data": [],
                "tool_results": [],
                "has_tool_results": False,
                "reasoning_steps": [],
                "tools_used": [],
                "tool_call_counts": {},
                "analysis_complete": False,
                "dashboard_summary": None,
                "risk_assessment": {},
                "recommendations": [],
                "error_message": None,
                "timestamp": end_date if end_date else datetime.now().isoformat()
            }
            
            logger.info("🔄 Starting LangGraph ReAct workflow...")
            
            # Run the workflow with enhanced config for Langfuse tracing
            config = {
                "configurable": {"thread_id": "react_dashboard_session"},
                "tags": ["public-health", "react-agent", "epidemiological-analysis"],
                "metadata": {
                    "agent_type": "react",
                    "date_range": f"{start_date} to {end_date}" if start_date or end_date else "default",
                    "workflow_version": "v1.0",
                    "data_sources": ["delphi_epidata", "policy_documents"]
                }
            }
            
            # Add Langfuse callback if available
            if self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                
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
                "recommendations": final_state.get("recommendations", []),
                
                # Add trends list with TrendResponse objects
                "trends": self._format_trends_from_fetch_data(final_state)
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
                "recommendations": [],
                "trends": []  # Empty trends list on error
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

    def _format_trends_from_fetch_data(self, state: Dict) -> List[Dict]:
        """Format trends from raw fetch_epi_signal data with flattened structure and parsed result"""
        trends = []
        
        fetch_data_list = state.get("fetch_epi_signal_data", [])
        logger.debug(f"🔍 Processing {len(fetch_data_list)} fetch_epi_signal results for trends output")
        
        for fetch_data in fetch_data_list:
            try:
                # Extract the basic structure (flattened, no "data" wrapper)
                trend_item = {
                    "tool_args": fetch_data.get("tool_args", {}),
                    "result": fetch_data.get("result"),
                    "timestamp": fetch_data.get("timestamp")
                }
                
                # Parse the JSON string in the "result" field
                result_str = trend_item.get("result")
                if isinstance(result_str, str):
                    try:
                        import json
                        parsed_result = json.loads(result_str)
                        trend_item["result"] = parsed_result
                        logger.debug(f"Parsed JSON result with {len(parsed_result) if isinstance(parsed_result, list) else 1} data points")
                    except json.JSONDecodeError as json_err:
                        logger.warning(f"⚠️ Could not parse result JSON: {json_err}")
                        # Keep the original string if parsing fails
                
                trends.append(trend_item)
                logger.debug(f"Created flattened trend data from {fetch_data.get('timestamp', 'unknown')}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not format fetch data: {str(e)}")
                continue
        
        logger.debug(f"✅ Formatted {len(trends)} flattened trends from {len(fetch_data_list)} fetch_epi_signal results")
        return trends


# Convenience functions for testing and usage
async def test_react_agent():
    """Test the ReAct agent with a sample request"""
    print("🧪 Testing Public Health ReAct Agent...")
    
    agent = PublicHealthReActAgent()
    
    result = await agent.assemble_dashboard()
    
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
            print(f"\n🔄 Processing:")
            print("-" * 40)
            
            result = await agent.assemble_dashboard()
            
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