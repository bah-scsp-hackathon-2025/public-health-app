# Dashboard API Endpoints

The Dashboard API provides HTTP endpoints to generate public health dashboards using the LangGraph agent. This allows web applications, mobile apps, and other services to access intelligent dashboard summaries via REST API calls.

## 🚀 Endpoints Overview

### Main Dashboard Generation

#### `POST /dashboard/generate`
Generate a custom dashboard based on natural language requirements.

**Request Body:**
```json
{
  "query": "Generate comprehensive public health dashboard for current situation",
  "llm_provider": "auto",  // optional: "openai", "anthropic", "auto"
  "mcp_host": "localhost", // optional: override MCP server host
  "mcp_port": 8000        // optional: override MCP server port
}
```

**Response:**
```json
{
  "success": true,
  "dashboard_summary": "📊 PUBLIC HEALTH DASHBOARD SUMMARY...",
  "alerts_count": 15,
  "trends_count": 6,
  "timestamp": "2024-01-15T14:30:00Z",
  "error": null,
  "generation_time_seconds": 4.23
}
```

### Status & Health Checks

#### `GET /dashboard/status`
Check the availability of the dashboard agent and its dependencies.

**Response:**
```json
{
  "agent_available": true,
  "mcp_server_accessible": true,
  "llm_providers": {
    "openai": true,
    "anthropic": false
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Pre-configured Dashboards

#### `GET /dashboard/alerts-summary`
Generate a dashboard focused on current public health alerts.

#### `GET /dashboard/trends-summary`
Generate a dashboard focused on health risk trends and patterns.

#### `GET /dashboard/emergency-summary`
Generate an emergency response dashboard with high-severity alerts.

All return the same response format as `/dashboard/generate`.

### Async Generation

#### `POST /dashboard/generate/async`
Start dashboard generation as a background task for long-running requests.

**Response:**
```json
{
  "message": "Dashboard generation started in background",
  "task_id": "dashboard_20240115_143000",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

## 🛠️ Usage Examples

### Python with requests

```python
import requests

# Generate custom dashboard
response = requests.post("http://localhost:8001/dashboard/generate", json={
    "query": "Focus on respiratory illness trends in California",
    "llm_provider": "openai"
})

result = response.json()
if result["success"]:
    print(result["dashboard_summary"])
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8001/dashboard/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Emergency response dashboard for Texas',
    llm_provider: 'auto'
  })
});

const result = await response.json();
console.log(result.dashboard_summary);
```

### cURL

```bash
curl -X POST "http://localhost:8001/dashboard/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate dashboard for high-severity alerts only",
    "llm_provider": "auto"
  }'
```

## 🔧 Configuration

### Environment Variables

The dashboard API uses these environment variables:

```bash
# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# LLM API Keys (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **500 Internal Server Error**: Agent or MCP server errors
- **Timeout**: Long-running dashboard generation

Error responses include detailed information:
```json
{
  "detail": {
    "error": "Dashboard generation failed: MCP server connection timeout",
    "generation_time_seconds": 10.0,
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

## 🧪 Testing

Use the provided test script to verify all endpoints:

```bash
cd backend
python3 test_dashboard_api.py
```

Or test individual endpoints:

```bash
# Check status
curl http://localhost:8001/dashboard/status

# Quick alerts summary
curl http://localhost:8001/dashboard/alerts-summary

# Custom dashboard
curl -X POST http://localhost:8001/dashboard/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "Focus on COVID-19 trends"}'
```

## 🔄 Integration Patterns

### Web Dashboard Integration

```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/api/health-dashboard")
async def get_health_dashboard(region: str = None):
    query = f"Generate health dashboard for {region}" if region else "Generate comprehensive health dashboard"
    
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8001/dashboard/generate", json={
            "query": query
        })
        return response.json()
```

### Scheduled Reports

```python
import asyncio
import httpx
from datetime import datetime

async def daily_dashboard_report():
    async with httpx.AsyncClient() as client:
        # Generate different types of reports
        reports = [
            ("alerts", "/dashboard/alerts-summary"),
            ("trends", "/dashboard/trends-summary"),
            ("emergency", "/dashboard/emergency-summary")
        ]
        
        for report_name, endpoint in reports:
            response = await client.get(f"http://localhost:8001{endpoint}")
            result = response.json()
            
            if result["success"]:
                # Save or send the dashboard
                filename = f"reports/{report_name}_{datetime.now().strftime('%Y%m%d')}.md"
                with open(filename, 'w') as f:
                    f.write(result["dashboard_summary"])

# Schedule with cron or run periodically
asyncio.run(daily_dashboard_report())
```

### Real-time Updates

```javascript
// Polling for updates
async function getDashboardUpdates() {
  const response = await fetch('/dashboard/alerts-summary');
  const data = await response.json();
  
  if (data.success) {
    updateDashboardUI(data.dashboard_summary);
  }
  
  // Poll every 5 minutes
  setTimeout(getDashboardUpdates, 5 * 60 * 1000);
}
```

## 📊 Response Format Details

### Dashboard Summary Structure

The `dashboard_summary` field contains markdown-formatted text with these sections:

- **🚨 CURRENT SITUATION**: Overall health landscape overview
- **🔥 CRITICAL ALERTS**: High-priority alerts requiring attention  
- **📈 TREND HIGHLIGHTS**: Key patterns and changes in health data
- **✅ PRIORITY RECOMMENDATIONS**: Actionable next steps
- **📊 STATISTICS**: Numerical summary of processed data

### Example Output

```markdown
📊 PUBLIC HEALTH DASHBOARD SUMMARY

🚨 CURRENT SITUATION
The public health landscape shows elevated activity with 12 active alerts 
affecting 1.8M people. Respiratory illnesses trending upward in urban areas.

🔥 CRITICAL ALERTS
• HIGH: COVID-19 outbreak in nursing facilities (CA) - 35,000 affected
• HIGH: Foodborne illness cluster (TX) - 8,000 affected

📈 TREND HIGHLIGHTS  
• Respiratory emergency visits ↗️ +18% (concerning)
• COVID-19 cases ↘️ -3% (improving)

✅ PRIORITY RECOMMENDATIONS
1. Deploy additional testing resources to affected facilities
2. Investigate food supply chain in Texas regions

📊 STATISTICS
• Total Active Alerts: 12
• High Severity: 3
• Population Affected: 1,800,000
```

## 🚨 Production Considerations

### Security
- Add API authentication and rate limiting
- Validate and sanitize all input parameters
- Use HTTPS in production environments

### Performance
- Implement request caching for frequently accessed dashboards
- Use a proper task queue (Redis/Celery) for async operations
- Monitor API response times and set appropriate timeouts

### Reliability
- Add retry logic for MCP server communication
- Implement circuit breakers for external dependencies
- Log all requests and responses for debugging

### Scalability
- Consider horizontal scaling with load balancers
- Cache dashboard results for common queries
- Implement request deduplication for identical queries 