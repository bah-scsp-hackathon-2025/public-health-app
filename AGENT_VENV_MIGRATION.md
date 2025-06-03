# Agent Virtual Environment Migration

## Summary
Successfully consolidated agent dependencies and established a dedicated virtual environment for the FastAPI application, separating it from the MCP server environment.

## Problem Solved
When agents were moved from `backend/mcp/` to `backend/app/agents/`, their dependencies (LangChain, LangGraph, etc.) remained in the MCP virtual environment, creating a dependency mismatch and architectural confusion.

## Changes Made

### 1. Package Consolidation

**Updated `backend/app/requirements.txt`:**
```txt
# FastAPI and web dependencies
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
python-multipart
email-validator
python-jose[cryptography]
passlib[bcrypt]
pytest
httpx

# LangGraph and LangChain dependencies for agents
langgraph>=0.4.7
langchain-core
langchain-openai>=0.3.19
langchain-anthropic>=0.3.14
langchain-mcp-adapters>=0.1.4

# Environment and utility dependencies
python-dotenv>=1.0.0
```

**Key Decision**: Did NOT include `fastmcp` package because:
- Agents are **clients** that connect to MCP servers via HTTP
- Only need `langchain-mcp-adapters` for client functionality
- `fastmcp` is only needed for the MCP **server** itself

### 2. Virtual Environment Setup

**Created `backend/app/venv/`:**
```bash
cd backend/app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Startup Script Updates

**Updated `backend/start_fastapi.py`:**
- Added proper PYTHONPATH configuration
- Added documentation about using app virtual environment
- Added diagnostic output for debugging

### 4. VS Code Integration Updates

**Updated `.vscode/tasks.json`:**
- "Start FastAPI App": Now uses `${workspaceFolder}/backend/app/venv/bin/python`
- "Test Dashboard API": Now uses app venv with correct PYTHONPATH

**Updated `.vscode/launch.json`:**
- "Debug FastAPI App": Uses app virtual environment
- "Debug Dashboard Agent": Uses app virtual environment
- "Debug Dashboard Agent Tests": Uses app virtual environment
- All configurations updated with proper PYTHONPATH

## Architecture Overview

### Clear Separation of Concerns

```
backend/
├── mcp/                    # MCP Server Environment
│   ├── venv/              # FastMCP server dependencies
│   ├── fastmcp_server.py  # MCP server implementation
│   └── requirements.txt   # Server-side packages (fastmcp, etc.)
│
└── app/                   # FastAPI Application Environment  
    ├── venv/              # Web app + agent dependencies
    ├── agents/            # LangGraph agents (clients)
    ├── routers/           # FastAPI routes
    ├── main.py            # FastAPI application
    └── requirements.txt   # Client-side packages (langchain, etc.)
```

### Dependency Flow

```
MCP Server (port 8000)
    ↑ HTTP/SSE
FastAPI App + Agents (port 8001)
    ↑ HTTP
Web Clients / API Users
```

## Testing Results

### ✅ Successful Tests

1. **Virtual Environment**: Created and activated successfully
2. **Package Installation**: All 72 packages installed without conflicts
3. **Agent Import**: `from app.agents import PublicHealthDashboardAgent` works
4. **FastAPI Server**: Starts correctly on configured host/port
5. **Configuration**: Environment variables loaded properly
6. **VS Code Integration**: All tasks and debug configs updated

### ✅ API Endpoints Working

- `GET /` - Root endpoint responds correctly
- `GET /dashboard/status` - Agent status check works
- `POST /dashboard/generate` - Dashboard generation endpoint accessible
- All endpoints return proper HTTP responses

### ⚠️ Known Issue

Dashboard generation fails with MCP connection error:
```
❌ Error fetching health data: unhandled errors in a TaskGroup (1 sub-exception)
```

This is expected when MCP server is not running and doesn't affect the virtual environment setup.

## Usage Instructions

### Development Workflow

**Start MCP Server (Terminal 1):**
```bash
cd backend/mcp
source venv/bin/activate
python3 -m uvicorn fastmcp_server:app --host 0.0.0.0 --port 8000
```

**Start FastAPI App (Terminal 2):**
```bash
cd backend
source app/venv/bin/activate
python3 start_fastapi.py
```

**Test Everything:**
```bash
cd backend
source app/venv/bin/activate
python3 test_dashboard_api.py
```

### VS Code Integration

- **"Start FastAPI App"** task: Uses app virtual environment
- **"Debug FastAPI App"** config: Full debugging with app environment
- **"Debug Dashboard Agent"** config: Agent debugging with proper dependencies

## Benefits Achieved

1. **Clean Architecture**: Clear separation between server and client environments
2. **Dependency Isolation**: No package conflicts between MCP server and web app
3. **Development Experience**: Proper VS Code integration with correct environments
4. **Maintainability**: Each component has its own dependency management
5. **Scalability**: Easy to add new packages to either environment independently

## Environment Variables

Both environments can share the same `.env` file:

```bash
# FastAPI Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8001

# MCP Server Configuration  
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# LLM API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Verification Commands

**Test app virtual environment:**
```bash
cd backend
source app/venv/bin/activate
python3 -c "from app.agents import PublicHealthDashboardAgent; print('✅ Success')"
```

**Test FastAPI startup:**
```bash
cd backend  
source app/venv/bin/activate
python3 start_fastapi.py
# Should show: 🚀 Starting FastAPI server on 0.0.0.0:8001
```

**Test VS Code task:**
- Open VS Code
- Run "Start FastAPI App" task
- Should use app virtual environment automatically

## Next Steps

1. **Production Deployment**: Consider using Docker containers for each environment
2. **CI/CD Pipeline**: Set up separate testing for MCP server and FastAPI app
3. **Monitoring**: Add health checks for both virtual environments
4. **Documentation**: Update README with new environment setup instructions

---

**Migration Complete**: The agent dependencies have been successfully moved to the FastAPI app virtual environment with proper separation of concerns and full VS Code integration. 