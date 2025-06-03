# LangSmith Integration for Public Health Dashboard

This document explains how to enable LangSmith tracing for the Public Health Dashboard LangGraph workflows.

## Overview

LangSmith provides observability and debugging capabilities for LangChain/LangGraph applications. It captures detailed traces of workflow execution, tool calls, and LLM interactions.

## Setup

### 1. Get LangSmith API Key

1. Sign up at [https://smith.langchain.com/](https://smith.langchain.com/)
2. Create a new project or use the default
3. Get your API key from the settings page

### 2. Environment Variables

Set these environment variables to enable tracing:

```bash
# Required for tracing
export LANGCHAIN_TRACING_V2=true
export LANGSMITH_API_KEY=your_api_key_here

# Optional configuration
export LANGCHAIN_PROJECT=public-health-dashboard
```

Or add them to your `.env` file:

```env
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_api_key_here
LANGCHAIN_PROJECT=public-health-dashboard
```

### 3. No Code Changes Required

Once the environment variables are set, tracing happens automatically. No additional imports or code changes are needed.

## Features Traced

When LangSmith is enabled, the following are automatically traced:

### ReAct Agent Workflow
- **Reasoning Node**: LLM decision making
- **Tool Execution**: MCP tool calls (fetch_epi_signal, detect_rising_trend)
- **Data Processing**: Tool output parsing and state updates
- **Final Analysis**: Dashboard generation with policy documents

### Standard Agent Workflow
- **Data Fetching**: Health alerts and trends collection
- **Analysis**: LLM-powered data analysis
- **Summary Generation**: Dashboard summary creation

### Trace Metadata

Each trace includes:
- Agent type (react/standard)
- Date range parameters
- Data sources used
- Workflow version
- Custom tags for filtering

## Testing LangSmith Integration

Run the test script to verify tracing:

```bash
# Set your API key
export LANGSMITH_API_KEY=your_key_here
export LANGCHAIN_TRACING_V2=true

# Run the test
python test_langsmith_integration.py
```

## Viewing Traces

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Navigate to your project (default: "public-health-dashboard")
3. View traces in real-time as workflows execute

### Trace Structure

Typical trace hierarchy:
```
📊 Dashboard Generation (Root)
├── 🧠 Reasoning Node
│   └── 💭 Claude LLM Call
├── 🔧 Tool Execution
│   ├── 📡 fetch_epi_signal
│   └── 📈 detect_rising_trend
├── 🔄 Data Processing
└── 📋 Final Analysis
    ├── 📄 Policy Document Retrieval
    └── 💭 Dashboard Summary Generation
```

## Configuration Options

### Project Settings

Configure in `backend/app/config.py`:

```python
class Settings(BaseSettings):
    # LangSmith Configuration
    langsmith_api_key: str = ""
    langsmith_project: str = "public-health-dashboard"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_tracing: bool = True
```

### Runtime Configuration

Both agents automatically configure LangSmith with:

```python
def _setup_langsmith_tracing(self):
    """Configure LangSmith tracing for workflow observability"""
    if langsmith_api_key and settings.langsmith_tracing:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        # ... etc
```

## Troubleshooting

### Common Issues

1. **No traces appearing**
   - Verify `LANGCHAIN_TRACING_V2=true` is set
   - Check API key is valid
   - Ensure network connectivity to smith.langchain.com

2. **Traces missing data**
   - Check that MCP server is running for tool traces
   - Verify agent workflows are executing successfully

3. **Performance impact**
   - Tracing adds minimal overhead (~1-2% latency)
   - Can be disabled by setting `LANGCHAIN_TRACING_V2=false`

### Debug Mode

Enable debug logging for more details:

```python
import logging
logging.getLogger("langchain").setLevel(logging.DEBUG)
```

## Benefits

### Development
- **Debug Workflows**: See exact execution flow
- **Optimize Performance**: Identify bottlenecks
- **Error Tracking**: Detailed error context

### Production
- **Monitor Performance**: Track latency and success rates
- **Audit Trail**: Complete workflow execution history
- **Quality Assurance**: Validate LLM outputs and tool calls

## Security Notes

- API keys are sensitive - never commit to version control
- Use environment variables or secure secret management
- LangSmith traces may contain sensitive data - review data governance policies

## Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangGraph Observability](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
- [Tracing Best Practices](https://docs.smith.langchain.com/tracing) 