# Google ADK Microservices Architecture

A microservices-based implementation of a news search and sentiment analysis system using Google ADK (Agent Development Kit).

## Architecture Overview

This project consists of three main components:

1. **Search Agent Service** (Port 8001) - Fetches news headlines using Google Search
2. **Sentiment Agent Service** (Port 8002) - Analyzes sentiment of news headlines
3. **Manager Agent** - Orchestrates the workflow by calling the microservices via HTTP

```
┌─────────────────┐
│  Manager Agent  │
│  (Orchestrator) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Search  │ │  Sentiment   │
│ Service │ │   Service    │
│ :8001   │ │   :8002      │
└─────────┘ └──────────────┘
```

## Features

- **Microservices Architecture**: Independent, scalable services
- **HTTP-based Communication**: RESTful APIs with JSON payloads
- **Retry Logic**: Automatic retries with exponential backoff (max 3 attempts)
- **Timeout Handling**: 10-second timeout for all HTTP requests
- **Health Checks**: Built-in health endpoints for monitoring
- **Docker Support**: Containerized services with Docker Compose
- **Error Handling**: Comprehensive error handling and logging

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Google ADK credentials (if required by your setup)

## Project Structure

```
gh/
├── manager/
│   ├── agent.py                          # Manager orchestrator
│   ├── requirements.txt                  # Manager dependencies
│   ├── Dockerfile                        # Manager container
│   └── sub_agents/
│       ├── search_agent/
│       │   ├── agent.py                  # Search agent definition
│       │   ├── server.py                 # FastAPI server
│       │   ├── requirements.txt          # Service dependencies
│       │   └── Dockerfile                # Service container
│       └── sentiment_agent/
│           ├── agent.py                  # Sentiment agent definition
│           ├── server.py                 # FastAPI server
│           ├── requirements.txt          # Service dependencies
│           └── Dockerfile                # Service container
├── docker-compose.yml                    # Multi-service orchestration
└── README.md                             # This file
```

## Installation & Setup

### Option 1: Local Development (without Docker)

#### 1. Install Search Agent Service

```bash
cd manager/sub_agents/search_agent
pip install -r requirements.txt
```

#### 2. Install Sentiment Agent Service

```bash
cd manager/sub_agents/sentiment_agent
pip install -r requirements.txt
python -m textblob.download_corpora  # Download TextBlob data
```

#### 3. Install Manager Agent

```bash
cd manager
pip install -r requirements.txt
```

### Option 2: Docker Deployment (Recommended)

Simply run:

```bash
docker compose up --build
```

This will:
- Build all three services
- Create a shared network (`google-adk-network`)
- Start services with health checks
- Expose ports 8001 and 8002 to your host

## Running the Services

### Local Run (Development)

#### Terminal 1: Start Search Agent Service
```bash
cd manager/sub_agents/search_agent
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2: Start Sentiment Agent Service
```bash
cd manager/sub_agents/sentiment_agent
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

#### Terminal 3: Use Manager Agent
```bash
cd manager
python -c "from agent import root_agent; import json; result = root_agent.run('OpenAI'); print(json.dumps(result, indent=2))"
```

### Docker Run (Production)

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild and restart
docker compose up --build -d
```

## API Documentation

### Search Agent Service (Port 8001)

#### Health Check
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "search_agent"
}
```

#### Run Search
```bash
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenAI latest news"}'
```

**Response:**
```json
{
  "headlines": [
    {
      "title": "OpenAI announces new model",
      "source": "TechCrunch",
      "date": "2024-01-15"
    }
  ],
  "meta": {
    "query": "OpenAI latest news",
    "count": 1,
    "status": "success"
  }
}
```

### Sentiment Agent Service (Port 8002)

#### Health Check
```bash
curl http://localhost:8002/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "sentiment_agent"
}
```

#### Run Sentiment Analysis
```bash
curl -X POST http://localhost:8002/run \
  -H "Content-Type: application/json" \
  -d '{
    "headlines": [
      "OpenAI announces breakthrough in AI research",
      "Tech stocks decline amid market uncertainty",
      "New regulations proposed for AI industry"
    ]
  }'
```

**Response:**
```json
{
  "sentiment_summary": {
    "overall": "mixed",
    "positive_count": 1,
    "negative_count": 1,
    "neutral_count": 1,
    "total_analyzed": 3
  },
  "per_item": [
    {
      "headline": "OpenAI announces breakthrough in AI research",
      "sentiment": "positive",
      "analysis": "..."
    }
  ]
}
```

## Testing the Pipeline

### End-to-End Test

1. **Test Search Service:**
```bash
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"query":"OpenAI"}' | jq .
```

2. **Extract headlines and test Sentiment Service:**
```bash
# Save search results
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"query":"OpenAI"}' > search_results.json

# Extract headlines (manual or with jq)
# Then test sentiment
curl -X POST http://localhost:8002/run \
  -H "Content-Type: application/json" \
  -d '{
    "headlines": [
      "OpenAI releases new AI model",
      "AI industry faces new challenges"
    ]
  }' | jq .
```

3. **Test Manager Orchestration:**
```python
from manager.agent import root_agent
import json

# Run full pipeline
result = root_agent.run("OpenAI")
print(json.dumps(result, indent=2))

# Check service health
health = root_agent.check_services_health()
print(f"Services health: {health}")
```

## Configuration

### Environment Variables

You can configure the services using environment variables:

#### Manager Agent
- `SEARCH_SERVICE_URL` - Search service URL (default: `http://localhost:8001`)
- `SENTIMENT_SERVICE_URL` - Sentiment service URL (default: `http://localhost:8002`)

#### Docker Compose
When using Docker Compose, services communicate via the internal network:
- Search Agent: `http://search-agent:8001`
- Sentiment Agent: `http://sentiment-agent:8002`

### Timeouts and Retries

Configured in `manager/agent.py`:
- **Request Timeout**: 10 seconds
- **Max Retries**: 3 attempts
- **Retry Strategy**: Exponential backoff (2s, 4s, 8s)

### Ports

- **8001**: Search Agent Service
- **8002**: Sentiment Agent Service
- Manager Agent doesn't expose a port (client only)

## Monitoring & Debugging

### Check Service Health

```bash
# Search service
curl http://localhost:8001/health

# Sentiment service
curl http://localhost:8002/health
```

### View Logs

**Local:**
Check terminal output where services are running

**Docker:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f search-agent
docker compose logs -f sentiment-agent
docker compose logs -f manager-agent
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- Search Agent: http://localhost:8001/docs
- Sentiment Agent: http://localhost:8002/docs

## Troubleshooting

### Services Not Starting

1. **Check if ports are already in use:**
```bash
lsof -i :8001
lsof -i :8002
```

2. **Kill existing processes:**
```bash
kill -9 <PID>
```

### Connection Refused Errors

- Ensure services are running: `curl http://localhost:8001/health`
- Check Docker network: `docker network ls`
- Verify container status: `docker compose ps`

### Timeout Errors

- Increase timeout in `manager/agent.py`: `REQUEST_TIMEOUT = 30.0`
- Check service logs for performance issues

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.11+)

## Development

### Adding New Features

1. **Add new endpoints** to service `server.py` files
2. **Update Pydantic models** for request/response validation
3. **Modify manager** to call new endpoints
4. **Update tests** and documentation

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test files as needed)
pytest tests/
```

## Production Considerations

1. **Security:**
   - Add authentication (API keys, OAuth)
   - Use HTTPS/TLS
   - Implement rate limiting

2. **Scalability:**
   - Use load balancers
   - Deploy multiple instances
   - Add caching (Redis)

3. **Monitoring:**
   - Add Prometheus metrics
   - Set up alerting
   - Use distributed tracing (Jaeger)

4. **Reliability:**
   - Implement circuit breakers
   - Add request queuing
   - Set up database for persistence

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

## Support

For issues and questions, please [open an issue](https://github.com/yourusername/yourrepo/issues).
