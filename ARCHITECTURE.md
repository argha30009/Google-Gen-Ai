# Architecture Documentation

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User (Web Browser)                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Manager Web UI      │
                    │   Port: 8000          │
                    │                       │
                    │  - FastAPI Server     │
                    │  - HTML/CSS/JS UI     │
                    │  - GET / (Web UI)     │
                    │  - POST /run (API)    │
                    │  - GET /health        │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │   Manager Agent       │
                    │   (Orchestrator)      │
                    │                       │
                    │  - HTTP Client        │
                    │  - Retry Logic        │
                    │  - Error Handling     │
                    │  - Report Generation  │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  Search Service   │   │ Sentiment Service │
        │   Port: 8001      │   │   Port: 8002      │
        │                   │   │                   │
        │  FastAPI Server   │   │  FastAPI Server   │
        │  ├─ POST /run     │   │  ├─ POST /run     │
        │  └─ GET /health   │   │  └─ GET /health   │
        │                   │   │                   │
        │  Google ADK       │   │  Google ADK       │
        │  Runner + Agent   │   │  Runner + Agent   │
        └───────────────────┘   └───────────────────┘
                │                       │
                ▼                       ▼
        ┌───────────────┐       ┌───────────────┐
        │ Google Search │       │  Gemini AI    │
        │     Tool      │       │  Analysis     │
        └───────────────┘       └───────────────┘
```

## Request Flow

### Complete Pipeline Flow

```
1. User Opens Web Browser
   │
   ├─► GET http://localhost:8000/
   │   └─► Returns HTML/CSS/JS Web UI
   │
   └─► User enters query: "OpenAI"
       │
       ├─► JavaScript POST http://localhost:8000/run
       │   Body: {"query": "OpenAI"}
       │
       └─► Manager Web Server receives request
           │
           └─► Step 1: Search for News
               │
               ├─► HTTP POST http://localhost:8001/run
               │   Body: {"query": "OpenAI"}
               │   Timeout: 60s
               │   Retries: 3 (with exponential backoff)
               │
               ├─► Search Service receives request
               │   │
               │   ├─► Validates input (Pydantic)
               │   ├─► Creates ADK Runner session
               │   ├─► Calls runner.run_async(query)
               │   ├─► Agent uses google_search tool
               │   ├─► Extracts headlines from events
               │   └─► Returns structured response
               │
               └─► Response: {"headlines": [...], "meta": {...}}
                   │
                   └─► Step 2: Analyze Sentiment
                       │
                       ├─► Extract headline texts
                       │
                       ├─► HTTP POST http://localhost:8002/run
                       │   Body: {"headlines": ["...", "..."]}
                       │   Timeout: 60s
                       │   Retries: 3 (with exponential backoff)
                       │
                       ├─► Sentiment Service receives request
                       │   │
                       │   ├─► Validates input (Pydantic)
                       │   ├─► Creates ADK Runner session
                       │   ├─► Calls runner.run_async(headlines)
                       │   ├─► Agent analyzes each headline with Gemini
                       │   ├─► Extracts sentiment from events
                       │   └─► Returns structured response
                       │
                       └─► Response: {"sentiment_summary": {...}, "per_item": [...]}
                           │
                           └─► Step 3: Generate Comprehensive Report
                               │
                               ├─► Combine search + sentiment results
                               ├─► Generate sentiment summary
                               ├─► Generate fact check report
                               ├─► Generate bias check report
                               ├─► Generate forensic analysis report
                               │
                               └─► Return complete report to browser
                                   │
                                   └─► JavaScript displays formatted results:
                                       ├─ Sentiment Analysis (with stats)
                                       ├─ Headlines (numbered list)
                                       ├─ Fact Check Report
                                       ├─ Bias Check Report
                                       ├─ Forensic Analysis
                                       └─ Full JSON Response
```

## Component Details

### Manager Agent (Orchestrator)

```
┌─────────────────────────────────────────────────────────┐
│                    ManagerAgent                         │
├─────────────────────────────────────────────────────────┤
│  Properties:                                            │
│  • search_url: str                                      │
│  • sentiment_url: str                                   │
│  • timeout: float (10s)                                 │
│  • client: httpx.Client                                 │
├─────────────────────────────────────────────────────────┤
│  Methods:                                               │
│  • __init__(search_url, sentiment_url, timeout)         │
│  • _call_search_service(query) → Dict                   │
│    └─ @retry(max=3, exponential_backoff)                │
│  • _call_sentiment_service(headlines) → Dict            │
│    └─ @retry(max=3, exponential_backoff)                │
│  • check_services_health() → Dict[str, bool]            │
│  • run(query) → Dict                                    │
│  • _generate_summary(...) → Dict                        │
│  • close()                                              │
│  • __enter__() / __exit__()                             │
└─────────────────────────────────────────────────────────┘
```

### Search Service (Port 8001)

```
┌─────────────────────────────────────────────────────────┐
│              Search Agent Service                       │
├─────────────────────────────────────────────────────────┤
│  Framework: FastAPI                                     │
│  Server: Uvicorn                                        │
│  Port: 8001                                             │
├─────────────────────────────────────────────────────────┤
│  Endpoints:                                             │
│                                                         │
│  GET /health                                            │
│  └─► Returns: {"status": "ok", "service": "..."}       │
│                                                         │
│  POST /run                                              │
│  ├─► Request: SearchRequest                             │
│  │   └─ query: str                                      │
│  ├─► Process: search_agent.run(query)                   │
│  └─► Response: SearchResponse                           │
│      ├─ headlines: List[Dict]                           │
│      └─ meta: Dict                                      │
├─────────────────────────────────────────────────────────┤
│  Models:                                                │
│  • SearchRequest(BaseModel)                             │
│  • SearchResponse(BaseModel)                            │
├─────────────────────────────────────────────────────────┤
│  Error Handling:                                        │
│  • HTTPException for errors                             │
│  • Detailed logging                                     │
│  • 500 status for agent failures                        │
└─────────────────────────────────────────────────────────┘
```

### Sentiment Service (Port 8002)

```
┌─────────────────────────────────────────────────────────┐
│            Sentiment Agent Service                      │
├─────────────────────────────────────────────────────────┤
│  Framework: FastAPI                                     │
│  Server: Uvicorn                                        │
│  Port: 8002                                             │
├─────────────────────────────────────────────────────────┤
│  Endpoints:                                             │
│                                                         │
│  GET /health                                            │
│  └─► Returns: {"status": "ok", "service": "..."}       │
│                                                         │
│  POST /run                                              │
│  ├─► Request: SentimentRequest                          │
│  │   └─ headlines: List[str]                            │
│  ├─► Validation: Non-empty list                         │
│  ├─► Process: sentiment_agent.run(headlines)            │
│  └─► Response: SentimentResponse                        │
│      ├─ sentiment_summary: Dict                         │
│      └─ per_item: List[Dict]                            │
├─────────────────────────────────────────────────────────┤
│  Models:                                                │
│  • SentimentRequest(BaseModel)                          │
│  • SentimentResponse(BaseModel)                         │
├─────────────────────────────────────────────────────────┤
│  Error Handling:                                        │
│  • HTTPException for validation errors (400)            │
│  • HTTPException for agent failures (500)               │
│  • Detailed logging                                     │
└─────────────────────────────────────────────────────────┘
```

## Docker Architecture

### Container Network

```
┌───────────────────────────────────────────────────────────────┐
│                  Docker Network: google-adk-network           │
│                         (Bridge Driver)                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Container: manager-agent                           │    │
│  │  ├─ Image: manager:latest                           │    │
│  │  ├─ Network: google-adk-network                     │    │
│  │  ├─ Depends: search-agent (healthy)                 │    │
│  │  │           sentiment-agent (healthy)              │    │
│  │  └─ Env: SEARCH_SERVICE_URL=http://search-agent:8001│    │
│  │         SENTIMENT_SERVICE_URL=http://sentiment-agent:8002│
│  └─────────────────────────────────────────────────────┘    │
│                           │                                   │
│              ┌────────────┴────────────┐                     │
│              │                         │                     │
│  ┌───────────▼──────────┐  ┌──────────▼─────────┐          │
│  │  search-agent        │  │  sentiment-agent    │          │
│  │  ├─ Port: 8001       │  │  ├─ Port: 8002      │          │
│  │  ├─ Health: /health  │  │  ├─ Health: /health │          │
│  │  ├─ Interval: 30s    │  │  ├─ Interval: 30s   │          │
│  │  └─ Restart: always  │  │  └─ Restart: always │          │
│  └──────────────────────┘  └────────────────────┘          │
│              │                         │                     │
└──────────────┼─────────────────────────┼─────────────────────┘
               │                         │
               ▼                         ▼
        localhost:8001            localhost:8002
```

### Health Check Flow

```
Docker Daemon
    │
    ├─► Every 30s: Check search-agent
    │   │
    │   ├─► Execute: python -c "import httpx; httpx.get('http://localhost:8001/health')"
    │   │
    │   ├─► Timeout: 10s
    │   ├─► Retries: 3
    │   ├─► Start Period: 10s
    │   │
    │   └─► Status: healthy / unhealthy
    │
    └─► Every 30s: Check sentiment-agent
        │
        ├─► Execute: python -c "import httpx; httpx.get('http://localhost:8002/health')"
        │
        ├─► Timeout: 10s
        ├─► Retries: 3
        ├─► Start Period: 10s
        │
        └─► Status: healthy / unhealthy
```

## Error Handling & Retry Logic

### Retry Strategy

```
Request Attempt 1
    │
    ├─► Success? → Return result
    │
    └─► Failure
        │
        ├─► Wait 2 seconds (exponential backoff)
        │
        └─► Request Attempt 2
            │
            ├─► Success? → Return result
            │
            └─► Failure
                │
                ├─► Wait 4 seconds (exponential backoff)
                │
                └─► Request Attempt 3
                    │
                    ├─► Success? → Return result
                    │
                    └─► Failure → Raise exception
```

### Error Flow

```
Manager calls service
    │
    ├─► HTTP Error (4xx, 5xx)
    │   ├─► Log error
    │   ├─► Retry (if attempts < 3)
    │   └─► Return error response
    │
    ├─► Timeout Error
    │   ├─► Log timeout
    │   ├─► Retry (if attempts < 3)
    │   └─► Return timeout error
    │
    ├─► Connection Error
    │   ├─► Log connection failure
    │   ├─► Retry (if attempts < 3)
    │   └─► Return connection error
    │
    └─► Other Exception
        ├─► Log exception
        ├─► Retry (if attempts < 3)
        └─► Return generic error
```

## Data Models

### Search Request/Response

```python
# Request
{
    "query": "OpenAI"
}

# Response
{
    "headlines": [
        {
            "title": "...",
            "source": "...",
            "date": "...",
            "url": "..."
        }
    ],
    "meta": {
        "query": "OpenAI",
        "count": 10,
        "status": "success"
    }
}
```

### Sentiment Request/Response

```python
# Request
{
    "headlines": [
        "OpenAI announces breakthrough",
        "Tech stocks decline",
        "New AI regulations proposed"
    ]
}

# Response
{
    "sentiment_summary": {
        "overall": "mixed",
        "positive_count": 1,
        "negative_count": 1,
        "neutral_count": 1,
        "total_analyzed": 3,
        "full_analysis": "..."
    },
    "per_item": [
        {
            "headline": "OpenAI announces breakthrough",
            "sentiment": "positive",
            "analysis": "..."
        },
        {
            "headline": "Tech stocks decline",
            "sentiment": "negative",
            "analysis": "..."
        },
        {
            "headline": "New AI regulations proposed",
            "sentiment": "neutral",
            "analysis": "..."
        }
    ]
}
```

### Manager Complete Response

```python
{
    "query": "OpenAI",
    "search_results": {
        "headlines": [
            {
                "title": "OpenAI launches new feature...",
                "query": "OpenAI"
            }
        ],
        "meta": {
            "query": "OpenAI",
            "count": 10,
            "status": "success"
        }
    },
    "sentiment_analysis": {
        "sentiment_summary": {
            "overall": "positive",
            "positive_count": 7,
            "negative_count": 1,
            "neutral_count": 2,
            "total_analyzed": 10,
            "full_analysis": "..."
        },
        "per_item": [
            {
                "headline": "OpenAI launches new feature...",
                "sentiment": "positive",
                "analysis": "..."
            }
        ]
    },
    "summary": {
        "overview": "Analysis of 10 headlines about 'OpenAI'",
        "sentiment_overview": "positive",
        "sentiment_summary": "Here's a summary of the news regarding OpenAI:\n\nSentiment Summary:\nThe sentiment around the topic of 'OpenAI' is predominantly positive...\n\nHeadlines and their Sentiment:\n• Headline 1 - **Positive**\n• Headline 2 - **Positive**",
        "fact_check": "Fact Check Report:\nHere's a breakdown of verifiable information...\n\nVerifiable Facts:\n• Multiple news sources report...\n\nConclusion of Fact Check:\nWhile most news sources provide similar accounts...",
        "bias_check": "Bias Check Report:\nAnalyzing the 10 headlines reveals...\n\nPotential Biases Detected:\n• Sentiment Distribution: 7 positive, 1 negative, 2 neutral...\n\nConclusion:\nThe distribution suggests balanced coverage...",
        "forensic_analysis": "Forensic Analysis and Source Tracking Report:\nTo determine the likely origin...\n\nTimeline of Key News Items:\n  - Headline 1\n  - Headline 2\n\nAnalysis of Origin:\nBased on the 10 headlines analyzed...\n\nConclusion:\nThe breadth of coverage suggests widespread dissemination..."
    }
}
```

## Deployment Scenarios

### Local Development

```
Developer Machine
    │
    ├─► Terminal 1: Search Service
    │   └─► uvicorn server:app --port 8001 --reload
    │
    ├─► Terminal 2: Sentiment Service
    │   └─► uvicorn server:app --port 8002 --reload
    │
    └─► Terminal 3: Manager / Tests
        └─► python -c "from manager.agent import root_agent; ..."
```

### Docker Development

```
Developer Machine
    │
    └─► docker compose up --build
        │
        ├─► Builds 3 images
        ├─► Creates network
        ├─► Starts containers
        └─► Exposes ports 8001, 8002
```

### Production (Conceptual)

```
Load Balancer
    │
    ├─► Search Service (3 replicas)
    │   ├─► Instance 1 (8001)
    │   ├─► Instance 2 (8001)
    │   └─► Instance 3 (8001)
    │
    └─► Sentiment Service (3 replicas)
        ├─► Instance 1 (8002)
        ├─► Instance 2 (8002)
        └─► Instance 3 (8002)
```

## Security Considerations

### Current State
- No authentication
- No rate limiting
- HTTP (not HTTPS)
- No input sanitization beyond Pydantic

### Recommended Additions

```
┌─────────────────────────────────────────┐
│  API Gateway                            │
│  ├─ Authentication (JWT/API Keys)       │
│  ├─ Rate Limiting                       │
│  ├─ Request Validation                  │
│  └─ SSL/TLS Termination                 │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│ Search  │           │Sentiment│
│ Service │           │ Service │
└─────────┘           └─────────┘
```

## Monitoring & Observability

### Recommended Stack

```
┌─────────────────────────────────────────┐
│  Grafana (Visualization)                │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  Prometheus (Metrics)                   │
│  ├─ Service health                      │
│  ├─ Request rates                       │
│  ├─ Response times                      │
│  └─ Error rates                         │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│ Search  │           │Sentiment│
│ Service │           │ Service │
│ /metrics│           │ /metrics│
└─────────┘           └─────────┘
```

## Scalability Path

### Horizontal Scaling

```
Current: 1 instance per service
    │
    ├─► Add Load Balancer
    │
    ├─► Scale to 3 instances per service
    │
    ├─► Add Auto-scaling (CPU/Memory based)
    │
    └─► Add Service Mesh (Istio/Linkerd)
```

### Vertical Scaling

```
Current: Default resources
    │
    ├─► Increase CPU allocation
    │
    ├─► Increase Memory allocation
    │
    └─► Optimize container images
```

## Summary

This architecture provides:
- ✅ **Separation of Concerns**: Each service has a single responsibility
- ✅ **Scalability**: Services can scale independently
- ✅ **Resilience**: Retry logic and error handling
- ✅ **Observability**: Health checks and logging
- ✅ **Maintainability**: Clear interfaces and documentation
- ✅ **Testability**: Services can be tested in isolation
- ✅ **Deployability**: Docker support for consistent environments
