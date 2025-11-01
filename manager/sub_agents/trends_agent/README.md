# Google Trends Agent

A microservice that analyzes Google Trends data for keywords using Google ADK and Gemini AI.

## Features

- Fetches Google Trends data for any keyword
- Analyzes trend patterns (rising, falling, stable)
- Identifies peak interest periods
- Provides comprehensive trend analysis
- RESTful API interface

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "trends_agent"
}
```

### Analyze Trends
```bash
POST /run
Content-Type: application/json

{
  "keyword": "artificial intelligence"
}
```

Response:
```json
{
  "keyword": "artificial intelligence",
  "trend_analysis": {
    "keyword": "artificial intelligence",
    "analysis": "Detailed trend analysis...",
    "status": "completed",
    "trend_direction": "rising"
  },
  "raw_response": "Full AI-generated analysis..."
}
```

## Running the Service

### Prerequisites
- Python 3.9+
- Google API Key with ADK access

### Installation
```bash
cd manager/sub_agents/trends_agent
pip install -r requirements.txt
```

### Start the Server
```bash
export GOOGLE_API_KEY="your-api-key-here"
uvicorn server:app --host 0.0.0.0 --port 8003 --reload
```

The service will be available at `http://localhost:8003`

## Integration with Manager

The Trends Agent is integrated into the Manager Agent and can be called via:

```python
from manager.agent import root_agent

# Run with trends analysis
result = root_agent.run_with_trends("Tesla")

# Access trends data
trends = result.get("trends_analysis", {})
```

## Example Usage

### Using curl
```bash
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"keyword": "ChatGPT"}'
```

### Using Python
```python
import httpx

response = httpx.post(
    "http://localhost:8003/run",
    json={"keyword": "ChatGPT"}
)
result = response.json()
print(result["trend_analysis"]["analysis"])
```

## Trend Analysis Output

The agent provides:

1. **Trend Direction**: Rising, falling, or stable
2. **Peak Periods**: When interest was highest
3. **Pattern Analysis**: Seasonal or event-driven trends
4. **Overall Summary**: Comprehensive trend interpretation

## Error Handling

The service includes:
- Automatic retries (3 attempts)
- Exponential backoff
- Detailed error logging
- Graceful degradation

## Port Configuration

Default port: **8003**

Can be changed in:
- `server.py` (if running standalone)
- `manager/agent.py` (TRENDS_SERVICE_URL)

## Dependencies

- FastAPI
- Google ADK
- Google Generative AI
- Uvicorn
- Pydantic

## Monitoring

Health check endpoint available at:
```bash
curl http://localhost:8003/health
```

## Notes

- Trends analysis may take 5-10 seconds depending on keyword complexity
- Results are based on AI interpretation of trends data
- For best results, use specific, well-defined keywords
