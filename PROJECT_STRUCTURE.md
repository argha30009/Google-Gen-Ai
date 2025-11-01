# Project Structure

## Complete File Tree

```
gh/
├── .gitignore                              # Git ignore patterns
├── README.md                               # Comprehensive documentation
├── QUICKSTART.md                           # Quick start guide
├── CHANGES.md                              # Summary of all changes
├── PROJECT_STRUCTURE.md                    # This file
├── docker-compose.yml                      # Multi-service orchestration
├── test_services.sh                        # Bash test script
├── test_services.py                        # Python test script
│
├── manager/                                # Manager Agent (Orchestrator)
│   ├── agent.py                           # ✨ HTTP-based orchestration logic
│   ├── requirements.txt                   # ✨ httpx, tenacity, google-adk
│   ├── Dockerfile                         # ✨ Manager container
│   ├── __init__.py                        # Package initialization
│   ├── .env                               # Environment variables
│   └── root_agent.yaml                    # Original agent config (legacy)
│
└── manager/sub_agents/
    │
    ├── search_agent/                      # Search Microservice (Port 8001)
    │   ├── agent.py                       # Google ADK search agent definition
    │   ├── server.py                      # ✨ FastAPI server wrapper
    │   ├── requirements.txt               # ✨ fastapi, uvicorn, google-adk
    │   ├── Dockerfile                     # ✨ Service container
    │   └── __init__.py                    # Package initialization
    │
    └── sentiment_agent/                   # Sentiment Microservice (Port 8002)
        ├── agent.py                       # Google ADK sentiment agent definition
        ├── server.py                      # ✨ FastAPI server wrapper
        ├── requirements.txt               # ✨ fastapi, uvicorn, textblob
        ├── Dockerfile                     # ✨ Service container
        └── __init__.py                    # Package initialization
```

✨ = New or significantly modified files

## File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation with architecture, setup, API docs, troubleshooting |
| `QUICKSTART.md` | Fast-track setup guide for getting started quickly |
| `CHANGES.md` | Detailed summary of all changes made during migration |
| `PROJECT_STRUCTURE.md` | This file - visual overview of project structure |
| `docker-compose.yml` | Orchestrates all services with networking and health checks |
| `test_services.sh` | Bash script for testing all services |
| `test_services.py` | Python script for comprehensive service testing |
| `.gitignore` | Git ignore patterns for Python, Docker, IDE files |

### Manager Agent (`manager/`)

| File | Purpose |
|------|---------|
| `agent.py` | **Modified** - Now implements HTTP-based orchestration with retry logic |
| `requirements.txt` | **New** - Dependencies: httpx, tenacity, google-adk |
| `Dockerfile` | **New** - Container for manager agent |
| `__init__.py` | Package initialization |
| `.env` | Environment variables (API keys, etc.) |

### Search Agent Service (`manager/sub_agents/search_agent/`)

| File | Purpose |
|------|---------|
| `agent.py` | Original Google ADK search agent definition |
| `server.py` | **New** - FastAPI server exposing search agent via HTTP |
| `requirements.txt` | **New** - Service dependencies |
| `Dockerfile` | **New** - Container for search service |
| `__init__.py` | Package initialization |

**Endpoints:**
- `GET /health` - Health check
- `POST /run` - Execute search (body: `{"query": str}`)

### Sentiment Agent Service (`manager/sub_agents/sentiment_agent/`)

| File | Purpose |
|------|---------|
| `agent.py` | Original Google ADK sentiment agent definition |
| `server.py` | **New** - FastAPI server exposing sentiment agent via HTTP |
| `requirements.txt` | **New** - Service dependencies |
| `Dockerfile` | **New** - Container for sentiment service |
| `__init__.py` | Package initialization |

**Endpoints:**
- `GET /health` - Health check
- `POST /run` - Analyze sentiment (body: `{"headlines": [str]}`)

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                  (google-adk-network)                       │
│                                                             │
│  ┌──────────────────┐                                      │
│  │  Manager Agent   │                                      │
│  │  (Orchestrator)  │                                      │
│  └────────┬─────────┘                                      │
│           │                                                 │
│           │ HTTP Requests                                  │
│           │ (with retry & timeout)                         │
│           │                                                 │
│      ┌────┴─────┐                                          │
│      │          │                                          │
│      ▼          ▼                                          │
│  ┌─────────┐ ┌──────────────┐                            │
│  │ Search  │ │  Sentiment   │                            │
│  │ Service │ │   Service    │                            │
│  │ :8001   │ │   :8002      │                            │
│  └─────────┘ └──────────────┘                            │
│      │              │                                      │
└──────┼──────────────┼──────────────────────────────────────┘
       │              │
       ▼              ▼
   localhost:8001  localhost:8002
```

## Data Flow

### 1. Search Request
```
User → Manager.run("query")
  → HTTP POST localhost:8001/run {"query": "..."}
  → Search Agent executes google_search
  → Returns {"headlines": [...], "meta": {...}}
```

### 2. Sentiment Analysis
```
Manager receives headlines
  → HTTP POST localhost:8002/run {"headlines": [...]}
  → Sentiment Agent analyzes each headline
  → Returns {"sentiment_summary": {...}, "per_item": [...]}
```

### 3. Final Report
```
Manager combines results
  → Generates comprehensive report
  → Includes fact check, bias check, forensic analysis notes
  → Returns complete JSON response
```

## Port Mapping

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Search Agent | 8001 | HTTP | News search API |
| Sentiment Agent | 8002 | HTTP | Sentiment analysis API |
| Manager | - | - | Client only (no server) |

## Network Configuration

### Local Development
- Services: `http://localhost:PORT`
- Direct host network access

### Docker Deployment
- Services: `http://service-name:PORT`
- Internal Docker network: `google-adk-network`
- Bridge driver for inter-container communication

## Dependencies

### Manager Agent
```
httpx==0.25.1          # HTTP client with timeout support
tenacity==8.2.3        # Retry logic with exponential backoff
google-adk==0.1.0      # Google Agent Development Kit
```

### Search Agent Service
```
fastapi==0.104.1       # Web framework
uvicorn[standard]==0.24.0  # ASGI server
pydantic==2.5.0        # Data validation
google-adk==0.1.0      # Agent framework
httpx==0.25.1          # HTTP client (for health checks)
```

### Sentiment Agent Service
```
fastapi==0.104.1       # Web framework
uvicorn[standard]==0.24.0  # ASGI server
pydantic==2.5.0        # Data validation
google-adk==0.1.0      # Agent framework
textblob==0.17.1       # Sentiment analysis
httpx==0.25.1          # HTTP client (for health checks)
```

## Configuration Files

### docker-compose.yml
- Defines 3 services: search-agent, sentiment-agent, manager-agent
- Creates shared network
- Configures health checks
- Sets up dependencies
- Maps ports to host

### Dockerfiles
Each service has its own Dockerfile:
- Based on `python:3.11-slim`
- Installs dependencies from requirements.txt
- Copies application code
- Exposes appropriate ports
- Defines health checks
- Runs with uvicorn (for services) or python (for manager)

## Testing Structure

### test_services.sh
Bash script that:
1. Checks service health
2. Tests search endpoint
3. Tests sentiment endpoint
4. Provides usage examples

### test_services.py
Python script that:
1. Validates service health
2. Tests each service independently
3. Tests manager orchestration
4. Provides detailed output with colors

## Quick Reference

### Start Services
```bash
# Docker
docker compose up --build

# Local
# Terminal 1: cd manager/sub_agents/search_agent && uvicorn server:app --port 8001
# Terminal 2: cd manager/sub_agents/sentiment_agent && uvicorn server:app --port 8002
```

### Test Services
```bash
# Automated
python3 test_services.py

# Manual
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Use Manager
```python
from manager.agent import root_agent
result = root_agent.run("OpenAI")
```

### View Logs
```bash
# Docker
docker compose logs -f

# Local
# Check terminal output where services are running
```

### Stop Services
```bash
# Docker
docker compose down

# Local
# Ctrl+C in each terminal
```

## Development Workflow

1. **Make changes** to agent code or server files
2. **Test locally** with `--reload` flag for auto-reload
3. **Run tests** with `python3 test_services.py`
4. **Build Docker** with `docker compose build`
5. **Deploy** with `docker compose up`

## Production Checklist

- [ ] Add authentication (JWT, API keys)
- [ ] Implement rate limiting
- [ ] Set up HTTPS/TLS
- [ ] Add monitoring (Prometheus, Grafana)
- [ ] Configure logging aggregation
- [ ] Set up CI/CD pipeline
- [ ] Implement circuit breakers
- [ ] Add caching layer (Redis)
- [ ] Configure auto-scaling
- [ ] Set up load balancing
- [ ] Implement request queuing
- [ ] Add distributed tracing
- [ ] Configure backup and recovery
- [ ] Set up alerting
- [ ] Document API versioning strategy

## Support Resources

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick setup guide
- **CHANGES.md** - Migration details
- **API Docs** - http://localhost:8001/docs & http://localhost:8002/docs
- **Test Scripts** - Automated validation
