# Public Health Application

A comprehensive public health monitoring and analysis system built with FastAPI, LangGraph agents, and MCP (Model Context Protocol) servers.

## 🏗️ Project Structure

```
public-health-app/
├── .vscode/                    # VS Code workspace configuration
│   ├── launch.json            # Debug configurations for all components
│   ├── tasks.json             # Build and run tasks
│   ├── settings.json          # Workspace settings
│   └── extensions.json        # Recommended extensions
├── backend/
│   ├── app/                   # Main FastAPI application
│   │   ├── agents/           # LangGraph intelligent agents
│   │   │   ├── health_dashboard_agent.py
│   │   │   ├── test_dashboard_agent.py
│   │   │   ├── demo_dashboard_agent.py
│   │   │   └── README_LANGGRAPH_AGENT.md
│   │   ├── routers/          # FastAPI route handlers
│   │   ├── models/           # Data models
│   │   └── main.py           # FastAPI application entry point
│   └── mcp/                   # MCP servers and infrastructure
│       ├── fastmcp_server.py  # FastMCP public health server
│       ├── venv/              # Python virtual environment
│       └── requirements.txt   # Python dependencies
├── .env-template              # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env-template .env

# Edit .env with your configuration
# Add API keys for OpenAI/Anthropic if desired

# Activate virtual environment
cd backend/mcp
source venv/bin/activate
```

### 2. Start Services

**Option A: Using VS Code Tasks (Recommended)**
- Open Command Palette (`Cmd+Shift+P`)
- Run `Tasks: Run Task`
- Select "Start FastMCP Server"
- Optionally run "Start FastAPI App"

**Option B: Command Line**
```bash
# Start FastMCP server (terminal 1)
cd backend/mcp
source venv/bin/activate
python3 -m uvicorn fastmcp_server:app --host 0.0.0.0 --port 8000

# Start FastAPI app (terminal 2) 
cd backend
source mcp/venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Test the Agents

```bash
# Navigate to agents directory
cd backend/app/agents

# Run the dashboard agent tests
PYTHONPATH=../../mcp:../.. python3 test_dashboard_agent.py

# Try the example usage
PYTHONPATH=../../mcp:../.. python3 example_usage.py
```

## 🔧 VS Code Integration

The workspace includes comprehensive VS Code configurations:

### Debug Configurations
- **Debug FastMCP Server**: Debug the MCP server
- **Debug Dashboard Agent**: Debug the LangGraph agent interactively
- **Debug Dashboard Agent Tests**: Debug the test suite
- **Debug FastAPI App**: Debug the main web application

### Tasks
- **Start FastMCP Server**: Launch the MCP server
- **Start FastAPI App**: Launch the web application  
- **Run Dashboard Agent Tests**: Execute agent test suite
- **Install Dependencies**: Install Python packages

### Usage
1. Open the workspace in VS Code
2. Press `F5` to see debug options
3. Use `Cmd+Shift+P` → "Tasks: Run Task" for build tasks
4. Recommended extensions will be suggested automatically

## 🧪 Development Workflow

### 1. Agent Development
```bash
cd backend/app/agents
PYTHONPATH=../../mcp:../.. python3 health_dashboard_agent.py interactive
```

### 2. MCP Server Development  
```bash
cd backend/mcp
source venv/bin/activate
python3 fastmcp_server.py
```

### 3. Web API Development
```bash
cd backend
source mcp/venv/bin/activate
python3 -m uvicorn app.main:app --reload
```

## 📚 Key Components

### LangGraph Agents (`backend/app/agents/`)
Intelligent agents built with LangGraph for health data analysis:
- **PublicHealthDashboardAgent**: Generates executive dashboards
- Supports OpenAI GPT-4 and Anthropic Claude
- Comprehensive test suite and demo examples

### FastMCP Server (`backend/mcp/`)
Model Context Protocol server providing health data tools:
- Public health alerts retrieval
- Health risk trends analysis  
- RESTful API with SSE transport

### FastAPI Application (`backend/app/`)
Web application providing REST APIs:
- Health data endpoints
- Agent integration APIs
- Modern async Python architecture

## 🔌 API Endpoints

- **FastMCP Server**: `http://localhost:8000`
  - SSE endpoint: `http://localhost:8000/sse`
  - Health check: `http://localhost:8000/health`

- **FastAPI App**: `http://localhost:8001`
  - API docs: `http://localhost:8001/docs`
  - Health check: `http://localhost:8001/health`

## 🌟 Features

- **Multi-LLM Support**: OpenAI GPT-4, Anthropic Claude
- **Real-time Data**: Live health alerts and trends
- **Intelligent Analysis**: AI-powered pattern recognition
- **Modern Architecture**: FastAPI, LangGraph, MCP protocol
- **Developer Experience**: VS Code integration, comprehensive testing

## 📖 Documentation

- [LangGraph Agent Documentation](backend/app/agents/README_LANGGRAPH_AGENT.md)
- [FastMCP Server Documentation](backend/mcp/README_FastMCP.md)
- [MCP Protocol Documentation](backend/mcp/README.md)

## 🤝 Contributing

1. Use the VS Code workspace for development
2. Follow the established project structure
3. Add tests for new features
4. Update documentation as needed

## 📄 License

See project license for details. 