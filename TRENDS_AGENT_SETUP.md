# Google Trends Agent - Setup & Integration Guide

## 🎯 Overview

The Google Trends Agent is a new microservice that analyzes Google search trends for keywords. It's integrated into your existing news analysis system.

## 📁 Files Created

```
manager/sub_agents/trends_agent/
├── __init__.py          # Package initialization
├── agent.py             # Google ADK agent definition
├── server.py            # FastAPI server
└── README.md            # Documentation
```

## 🏗️ Architecture Update

Your system now has **4 microservices**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Manager Web UI (Port 8000)               │
│                    • run(query) - Standard pipeline         │
│                    • run_with_trends(query) - With trends   │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────────┐
        ▼          ▼          ▼              ▼
   ┌────────┐ ┌────────┐ ┌────────┐    ┌────────┐
   │ Search │ │Sentiment│ │ Trends │    │ Future │
   │  8001  │ │  8002  │ │  8003  │    │ Agents │
   └────────┘ └────────┘ └────────┘    └────────┘
```

## 🚀 Quick Start

### 1. Start the Trends Service

Open a new terminal:

```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/trends_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8003 --reload
```

### 2. Test the Service

```bash
# Health check
curl http://localhost:8003/health

# Analyze trends
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"keyword": "Tesla"}'
```

### 3. Use in Manager

The Manager Agent now has two methods:

**Standard Pipeline** (Search + Sentiment):
```python
from manager.agent import root_agent

result = root_agent.run("Tesla")
# Returns: search_results, sentiment_analysis, summary
```

**Enhanced Pipeline** (Search + Sentiment + Trends):
```python
from manager.agent import root_agent

result = root_agent.run_with_trends("Tesla")
# Returns: search_results, sentiment_analysis, summary, trends_analysis
```

## 📊 Response Format

### Standard Response
```json
{
  "query": "Tesla",
  "search_results": {...},
  "sentiment_analysis": {...},
  "summary": {...}
}
```

### With Trends Response
```json
{
  "query": "Tesla",
  "search_results": {...},
  "sentiment_analysis": {...},
  "summary": {...},
  "trends_analysis": {
    "keyword": "Tesla",
    "trend_analysis": {
      "keyword": "Tesla",
      "analysis": "Detailed trend analysis...",
      "status": "completed",
      "trend_direction": "rising"
    },
    "raw_response": "Full AI analysis..."
  }
}
```

## 🔧 Manager Agent Updates

### New Configuration
```python
TRENDS_SERVICE_URL = "http://localhost:8003"
```

### New Methods

1. **`_call_trends_service(keyword)`**
   - Calls the trends microservice
   - Includes retry logic (3 attempts)
   - Returns trend analysis

2. **`run_with_trends(query)`**
   - Runs full pipeline including trends
   - Gracefully handles trends failures
   - Returns comprehensive report

3. **`check_services_health()`**
   - Now checks all 3 services
   - Includes trends_service status

## 🎨 Web UI Integration (Optional)

To add trends to the web UI, update `manager/server.py`:

```python
@app.post("/run-with-trends")
async def run_with_trends(request: QueryRequest) -> Dict[str, Any]:
    """Run pipeline with trends analysis."""
    try:
        result = root_agent.run_with_trends(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Then add a button in the HTML:
```html
<button onclick="searchWithTrends()">Search with Trends</button>
```

## 📈 Use Cases

### 1. News + Trends Analysis
```python
# Get news sentiment AND search trends
result = root_agent.run_with_trends("OpenAI")

# Check if topic is trending
trends = result["trends_analysis"]["trend_analysis"]
if trends["trend_direction"] == "rising":
    print("This topic is gaining popularity!")
```

### 2. Comparative Analysis
```python
# Compare news sentiment with search interest
sentiment = result["summary"]["sentiment_overview"]
trend = result["trends_analysis"]["trend_analysis"]["trend_direction"]

print(f"Sentiment: {sentiment}, Trend: {trend}")
```

### 3. Historical Context
```python
# Understand if current news matches search interest
trends_analysis = result["trends_analysis"]["trend_analysis"]["analysis"]
print(f"Trend Context: {trends_analysis}")
```

## 🔄 Running All Services

To run the complete system with trends:

### Terminal 1 - Search Agent
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/search_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2 - Sentiment Agent
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/sentiment_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

### Terminal 3 - Trends Agent (NEW!)
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/trends_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8003 --reload
```

### Terminal 4 - Manager Web UI
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager
../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## ✅ Health Check All Services

```bash
# Check all services
curl http://localhost:8001/health  # Search
curl http://localhost:8002/health  # Sentiment
curl http://localhost:8003/health  # Trends (NEW!)
curl http://localhost:8000/health  # Manager
```

## 🧪 Testing

### Test Trends Service Directly
```bash
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence"}'
```

### Test via Manager
```python
from manager.agent import root_agent

# Test with trends
result = root_agent.run_with_trends("ChatGPT")

# Check results
print("Query:", result["query"])
print("Sentiment:", result["summary"]["sentiment_overview"])
print("Trend Direction:", result["trends_analysis"]["trend_analysis"]["trend_direction"])
print("Trend Analysis:", result["trends_analysis"]["trend_analysis"]["analysis"])
```

## 📊 Performance

- **Response Time**: 5-10 seconds (trends analysis)
- **Caching**: Can be added to cache trends results
- **Graceful Degradation**: If trends fails, standard pipeline continues

## 🔮 Future Enhancements

1. **Cache trends results** (1 hour TTL)
2. **Add trends visualization** (charts/graphs)
3. **Compare multiple keywords**
4. **Historical trend comparison**
5. **Trend predictions**

## 🎉 Summary

You now have a complete 4-service architecture:

✅ **Search Agent** - Fetches news headlines
✅ **Sentiment Agent** - Analyzes sentiment
✅ **Trends Agent** - Analyzes search trends (NEW!)
✅ **Manager** - Orchestrates everything

The system is modular and can easily add more agents in the future!
