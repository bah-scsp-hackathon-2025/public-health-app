# Langfuse Integration for Public Health Dashboard

This document explains how to enable Langfuse tracing for the Public Health Dashboard LangGraph workflows.

## Overview

Langfuse provides observability and debugging capabilities for LangChain/LangGraph applications. It captures detailed traces of workflow execution, tool calls, and LLM interactions using callback handlers.

## Setup

### 1. Get Langfuse API Keys

#### Cloud Version (Recommended)
1. Sign up at [https://cloud.langfuse.com/](https://cloud.langfuse.com/)
2. Create a new project
3. Go to Settings > API Keys
4. Generate a new key pair (Public Key & Secret Key)

#### Self-Hosted Version
1. Deploy Langfuse using their Docker setup
2. Access your instance web interface
3. Create a project and generate API keys

### 2. Environment Variables

Set these environment variables to enable tracing:

```bash
# Required for tracing
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_PUBLIC_KEY=pk-lf-...

# Optional configuration
export LANGFUSE_HOST=https://cloud.langfuse.com  # or your self-hosted URL
export LANGFUSE_PROJECT=public-health-dashboard
export LANGFUSE_TRACING=true
```

Or add them to your `.env` file:

```env
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROJECT=public-health-dashboard
LANGFUSE_TRACING=true
```

### 3. Callback Handler Integration

Unlike LangSmith's environment variable approach, Langfuse integrates through callback handlers. This is automatically configured in both agents when the environment variables are set.

## Features Traced

When Langfuse is enabled, the following are automatically traced:

### ReAct Agent Workflow
- **Reasoning Node**: LLM decision making and reasoning steps
- **Tool Execution**: MCP tool calls (fetch_epi_signal, detect_rising_trend)
- **Data Processing**: Tool output parsing and state updates
- **Final Analysis**: Dashboard generation with policy documents
- **File Operations**: Policy document retrieval and processing

### Standard Agent Workflow
- **Data Fetching**: Health alerts and trends collection
- **Analysis**: LLM-powered data analysis
- **Summary Generation**: Dashboard summary creation
- **Error Handling**: Workflow error recovery

### Trace Metadata

Each trace includes:
- **Session ID**: Unique identifier for each agent run
- **User ID**: "public-health-system" for system identification
- **Agent Type**: "react" or "standard"
- **Project**: Configurable project name
- **Environment**: "production" or custom
- **Date Range**: Analysis time period
- **Data Sources**: APIs and services used

## Testing Langfuse Integration

Run the test script to verify tracing:

```bash
# Set your API keys
export LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
export LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
export LANGFUSE_TRACING=true

# Run the test
python test_langfuse_integration.py
```

## Viewing Traces

1. Go to [https://cloud.langfuse.com/](https://cloud.langfuse.com/) (or your self-hosted URL)
2. Navigate to your project
3. View traces in real-time as workflows execute

### Trace Structure

Typical trace hierarchy:
```
📊 Dashboard Generation (Session)
├── 🧠 Reasoning Node
│   └── 💭 Claude LLM Call
│       ├── Input: System + Human messages
│       ├── Output: Decision/reasoning
│       └── Metadata: Temperature, model, tokens
├── 🔧 Tool Execution
│   ├── 📡 fetch_epi_signal
│   │   ├── Input: Signal parameters
│   │   ├── Output: Epidemiological data
│   │   └── Execution time
│   └── 📈 detect_rising_trend
│       ├── Input: Time series data
│       ├── Output: Trend analysis
│       └── Statistical results
├── 🔄 Data Processing
│   ├── Signal parsing
│   └── State updates
└── 📋 Final Analysis
    ├── 📄 Policy Document Retrieval
    │   └── File IDs and attachments
    └── 💭 Dashboard Summary Generation
        ├── Input: Structured data + policies
        ├── Output: Complete dashboard
        └── Performance metrics
```

## Configuration Options

### Project Settings

Configure in `backend/app/config.py`:

```python
class Settings(BaseSettings):
    # Langfuse Configuration
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_project: str = "public-health-dashboard"
    langfuse_tracing: bool = True
```

### Runtime Configuration

Both agents automatically configure Langfuse with:

```python
def _setup_langfuse_tracing(self):
    """Configure Langfuse tracing for workflow observability"""
    if langfuse_secret_key and langfuse_public_key and settings.langfuse_tracing:
        self.langfuse_handler = CallbackHandler(
            secret_key=langfuse_secret_key,
            public_key=langfuse_public_key,
            host=langfuse_host,
            session_id=f"react-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            user_id="public-health-system",
            metadata={
                "agent_type": "react",
                "project": settings.langfuse_project,
                "environment": "production"
            }
        )
```

### LLM Call Integration

LLM calls automatically include the callback:

```python
# Automatically adds Langfuse callback if available
callbacks = [self.langfuse_handler] if self.langfuse_handler else []
config = {"callbacks": callbacks} if callbacks else {}
response = await self.llm.ainvoke(messages, config=config)
```

### Workflow Integration

LangGraph workflows include the callback in configuration:

```python
config = {
    "configurable": {"thread_id": "react_dashboard_session"},
    "tags": ["public-health", "react-agent", "epidemiological-analysis"],
    "metadata": { ... }
}

# Add Langfuse callback if available
if self.langfuse_handler:
    config["callbacks"] = [self.langfuse_handler]
```

## Advanced Features

### Custom Spans

For detailed tracing, create custom spans:

```python
from langfuse.decorators import observe

@observe(name="custom_analysis")
async def custom_analysis_function():
    # Your analysis code here
    pass
```

### User Feedback

Collect feedback on generated dashboards:

```python
# In the callback handler, you can add user feedback
self.langfuse_handler.score(
    name="dashboard_quality",
    value=5,
    comment="Excellent epidemiological analysis"
)
```

### Session Management

Each agent run creates a unique session:

```python
session_id = f"react-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
```

## Troubleshooting

### Common Issues

1. **No traces appearing**
   - Verify `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` are set
   - Check keys are valid and project exists
   - Ensure `LANGFUSE_TRACING=true`
   - Verify network connectivity to Langfuse host

2. **Partial traces missing**
   - Check that MCP server is running for tool traces
   - Verify agent workflows are executing successfully
   - Look for callback handler initialization errors in logs

3. **Performance impact**
   - Langfuse callbacks add minimal overhead (~2-3% latency)
   - Can be disabled by setting `LANGFUSE_TRACING=false`
   - Use batching for high-throughput scenarios

4. **Authentication errors**
   - Verify secret key starts with `sk-lf-`
   - Verify public key starts with `pk-lf-`
   - Check project permissions in Langfuse dashboard

### Debug Mode

Enable debug logging for more details:

```python
import logging
logging.getLogger("langfuse").setLevel(logging.DEBUG)
```

### Testing Connection

Test your Langfuse connection:

```python
from langfuse import Langfuse

langfuse = Langfuse(
    secret_key="your-secret-key",
    public_key="your-public-key",
    host="https://cloud.langfuse.com"
)

# Test connection
try:
    langfuse.get_project()
    print("✅ Langfuse connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Benefits

### Development
- **Debug Workflows**: See exact execution flow with detailed spans
- **Optimize Performance**: Identify bottlenecks and slow operations
- **Error Tracking**: Detailed error context and stack traces
- **Model Comparison**: Compare different LLM responses and strategies

### Production
- **Monitor Performance**: Track latency, token usage, and success rates
- **Audit Trail**: Complete workflow execution history
- **Quality Assurance**: Validate LLM outputs and tool call results
- **Cost Analysis**: Track token usage and API costs per workflow

### Analytics
- **Usage Patterns**: Understand how dashboards are being generated
- **Success Metrics**: Track workflow completion rates
- **User Behavior**: Analyze which features are most used
- **Data Sources**: Monitor API performance and reliability

## Security Notes

- API keys are sensitive - never commit to version control
- Use environment variables or secure secret management
- Langfuse traces may contain sensitive health data - review data governance policies
- Consider data retention policies for compliance
- Use self-hosted Langfuse for maximum data control

## Migration from LangSmith

If migrating from LangSmith:

1. Remove LangSmith environment variables:
   ```bash
   unset LANGCHAIN_TRACING_V2
   unset LANGCHAIN_API_KEY
   unset LANGCHAIN_PROJECT
   ```

2. Set Langfuse environment variables as shown above

3. Traces will automatically start flowing to Langfuse

4. Historical LangSmith traces remain accessible in LangSmith

## Additional Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [LangChain Integration Guide](https://langfuse.com/docs/integrations/langchain)
- [LangGraph Observability](https://langfuse.com/docs/tracing-features/sessions)
- [Self-Hosting Guide](https://langfuse.com/docs/deployment/self-host) 