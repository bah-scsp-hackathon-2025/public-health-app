# MCP Public Health Server - Debugging Guide

This guide explains how to debug the MCP servers using the VS Code launch configurations.

## 🚀 Quick Start

1. **Open VS Code** in the `mcp` directory
2. **Install recommended extensions** when prompted
3. **Select the Python interpreter** (should auto-detect `./venv/bin/python`)
4. **Press F5** or go to Run and Debug view
5. **Select a debug configuration** from the dropdown

## 🐛 Available Debug Configurations

### 1. **Debug Current File** (Recommended)
- **Use case**: Debug whatever file you currently have open
- **How to use**: Open any Python file and press `F5`
- **Features**: 
  - Automatically uses the virtual environment
  - Sets proper PYTHONPATH
  - Allows debugging through external libraries

### 2. **Debug FastMCP Server**
- **Use case**: Debug the FastMCP server with SSE transport
- **Port**: 8000
- **Features**:
  - Sets `MCP_DEBUG=1` environment variable
  - Enables breakpoints in FastMCP tools
  - Full stack debugging

### 3. **Debug Raw MCP Server**
- **Use case**: Debug the original raw MCP implementation
- **Features**:
  - Compare FastMCP vs Raw MCP behavior
  - Debug stdio transport issues
  - Full protocol debugging

### 4. **Debug LangChain MCP Test**
- **Use case**: Debug the LangChain adapter integration
- **Features**:
  - Step through tool invocations
  - Debug JSON parsing
  - Trace HTTP requests to MCP server

### 5. **Debug Raw MCP Test**
- **Use case**: Debug the original stdio-based tests
- **Features**:
  - Debug MCP protocol messages
  - Trace JSON-RPC communication

### 6. **Debug FastMCP with Development Mode**
- **Use case**: Use FastMCP's built-in development tools
- **Features**:
  - MCP Inspector web interface
  - Hot reloading
  - Enhanced debugging output

### 7. **Debug FastMCP with Specific Tool**
- **Use case**: Focus debugging on specific tools
- **Environment**: `MCP_TOOL_BREAKPOINT=fetch_epi_signal`
- **Features**:
  - Automatic breakpoints on tool calls
  - Tool-specific debugging

### 8. **Debug with Args**
- **Use case**: Debug with custom command-line arguments
- **Default args**: `--debug --port 8001`
- **Features**:
  - Custom port debugging
  - Additional debug flags

## 🔧 Advanced Debugging Features

### Compound Configuration
- **Debug FastMCP Server + Test**: Runs both server and test simultaneously
- **Use case**: End-to-end debugging of client-server interaction

### Environment Variables
- `MCP_DEBUG=1`: Enables enhanced MCP debugging
- `MCP_TOOL_BREAKPOINT=tool_name`: Auto-break on specific tool
- `PYTHONPATH`: Properly set for module imports

### Debugging Tips

#### 1. **Setting Breakpoints**
```python
# In your code, add breakpoints on:
@mcp.tool()
def get_public_health_alerts(...):
    # <- Set breakpoint here
    filtered_alerts = MOCK_ALERTS.copy()
    # <- Or here to debug filtering logic
```

#### 2. **Debug Variables**
- Use the **Variables** panel to inspect:
  - `filtered_alerts` - See filtering results
  - `server_info` - Check server state
  - `tools` - Examine available tools

#### 3. **Debug Console**
```python
# In the debug console, try:
len(MOCK_ALERTS)
filtered_alerts[0]['title']
server_info.get('version')
```

#### 4. **Network Debugging**
- Use **Debug Console** to check HTTP requests:
```python
import requests
response = requests.get('http://localhost:8000/sse')
print(response.status_code)
```

## 🛠️ VS Code Tasks

Use **Terminal > Run Task** or `Ctrl+Shift+P` > "Tasks: Run Task":

### Server Tasks
- **Start FastMCP Server**: Background server on port 8000
- **Start Raw MCP Server**: Background stdio server
- **FastMCP Development Mode**: Server with MCP Inspector

### Test Tasks
- **Run LangChain MCP Test**: Full integration test
- **Run Raw MCP Test**: Original protocol test
- **Check MCP Server Health**: Quick server status

### Maintenance Tasks
- **Setup MCP Environment**: Run setup.sh
- **Install Dependencies**: pip install requirements
- **Format Python Code**: Black formatter
- **Lint Python Code**: Flake8 linting

## 🎯 Common Debugging Scenarios

### 1. **Tool Not Working**
1. Use **Debug FastMCP Server**
2. Set breakpoint in the tool function
3. Use **Debug LangChain MCP Test** to trigger tool
4. Step through tool logic

### 2. **LangChain Integration Issues**
1. Use **Debug LangChain MCP Test**
2. Set breakpoint in `parse_tool_result()`
3. Check JSON parsing and tool invocation

### 3. **Server Startup Issues**
1. Use **Debug FastMCP Server**
2. Check virtual environment activation
3. Verify port availability (8000)

### 4. **Protocol Debugging**
1. Use **Debug Raw MCP Server**
2. Enable MCP_DEBUG environment variable
3. Check JSON-RPC message flow

## 📊 Performance Debugging

### Memory Usage
```python
# Add to debug console:
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Request Timing
```python
# Add timing to tools:
import time
start_time = time.time()
# ... your tool logic ...
print(f"Tool execution time: {time.time() - start_time:.3f}s")
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Python Interpreter Not Found**
- **Solution**: `Ctrl+Shift+P` > "Python: Select Interpreter" > Choose `./venv/bin/python`

#### 2. **Debugger Won't Start**
- **Check**: Virtual environment is activated
- **Check**: Python extension is installed
- **Solution**: Restart VS Code

#### 3. **Breakpoints Not Hit**
- **Check**: `"justMyCode": false` in launch.json
- **Check**: File path matches exactly
- **Solution**: Set breakpoint after server startup

#### 4. **Port Already in Use**
- **Check**: `lsof -i :8000`
- **Solution**: Kill existing process or use different port

#### 5. **Module Import Errors**
- **Check**: PYTHONPATH includes workspace
- **Check**: Virtual environment is activated
- **Solution**: Restart debug session

### Debug Log Analysis

Enable logging in your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@mcp.tool()
def get_public_health_alerts(...):
    logger.debug(f"Called with states={states}, severity={severity}")
    # ... rest of tool logic
```

## 📝 Debug Session Workflow

1. **Start Debugging**:
   - Select configuration
   - Press F5 or click "Start Debugging"

2. **Set Strategic Breakpoints**:
   - Tool entry points
   - Data transformation logic
   - Error handling code

3. **Use Debug Features**:
   - **Step Over** (F10): Next line in current function
   - **Step Into** (F11): Enter function calls
   - **Step Out** (Shift+F11): Exit current function
   - **Continue** (F5): Run to next breakpoint

4. **Inspect State**:
   - **Variables panel**: See all local/global vars
   - **Watch panel**: Monitor specific expressions
   - **Call Stack**: See execution path
   - **Debug Console**: Run Python expressions

5. **Test Integration**:
   - Use compound configurations
   - Debug both client and server simultaneously
   - Trace request/response flow

## 🎉 Happy Debugging!

With this configuration, you have professional-grade debugging capabilities for your MCP servers. The setup supports both FastMCP and raw MCP implementations, with full LangChain integration testing.

**Pro Tips**:
- Use conditional breakpoints for specific data
- Leverage the debug console for quick testing
- Combine multiple debug sessions for end-to-end testing
- Monitor both memory and network in complex scenarios 