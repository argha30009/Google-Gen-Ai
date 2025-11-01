# Quick Start Guide

Get your Google ADK microservices up and running in minutes!

## 🚀 Quick Start with Docker (Recommended)

```bash
# 1. Build and start all services
docker compose up --build

# 2. In another terminal, test the services
./test_services.py
```

That's it! Your services are now running at:
- Search Agent: http://localhost:8001
- Sentiment Agent: http://localhost:8002

## 🧪 Quick Test

```bash
# Test search service
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"query":"OpenAI"}'

# Test sentiment service
curl -X POST http://localhost:8002/run \
  -H "Content-Type: application/json" \
  -d '{"headlines":["AI breakthrough announced","Market shows uncertainty"]}'
```

## 💻 Local Development Setup

### 1. Install Dependencies

```bash
# Search Agent
cd manager/sub_agents/search_agent
pip install -r requirements.txt

# Sentiment Agent
cd ../sentiment_agent
pip install -r requirements.txt
python -m textblob.download_corpora

# Manager
cd ../../
pip install -r requirements.txt
```

### 2. Start Services

**Terminal 1 - Search Agent:**
```bash
cd manager/sub_agents/search_agent
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Sentiment Agent:**
```bash
cd manager/sub_agents/sentiment_agent
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 3 - Test Manager:**
```bash
cd manager
python3 << 'EOF'
from agent import root_agent
import json

result = root_agent.run("OpenAI")
print(json.dumps(result, indent=2))
EOF
```

## 🔍 Verify Everything Works

Run the test suite:

```bash
# Python test (recommended)
python3 test_services.py

# Or bash script
./test_services.sh
```

## 📖 Interactive API Documentation

Once services are running, visit:
- Search Agent: http://localhost:8001/docs
- Sentiment Agent: http://localhost:8002/docs

Try the APIs directly in your browser!

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8001
lsof -i :8002

# Kill the process
kill -9 <PID>
```

### Services Not Responding

```bash
# Check if services are running
curl http://localhost:8001/health
curl http://localhost:8002/health

# Check Docker logs
docker compose logs -f
```

### Import Errors

Make sure you're in the correct directory and have installed dependencies:

```bash
cd /Users/amansiddharth/Downloads/gh
pip install -r manager/requirements.txt
pip install -r manager/sub_agents/search_agent/requirements.txt
pip install -r manager/sub_agents/sentiment_agent/requirements.txt
```

## 📚 Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API docs at `/docs` endpoints
3. Customize the agents in `agent.py` files
4. Add authentication and monitoring for production

## 🎯 Example Usage

### Python Client

```python
import httpx

# Search for news
response = httpx.post(
    "http://localhost:8001/run",
    json={"query": "artificial intelligence"},
    timeout=30.0
)
search_results = response.json()
print(f"Found {len(search_results['headlines'])} headlines")

# Analyze sentiment
headlines = [h.get('title', str(h)) for h in search_results['headlines']]
response = httpx.post(
    "http://localhost:8002/run",
    json={"headlines": headlines},
    timeout=30.0
)
sentiment = response.json()
print(f"Overall sentiment: {sentiment['sentiment_summary']['overall']}")
```

### Using Manager Agent

```python
from manager.agent import root_agent

# Full pipeline in one call
result = root_agent.run("climate change")

print(f"Query: {result['query']}")
print(f"Headlines found: {len(result['search_results']['headlines'])}")
print(f"Sentiment: {result['sentiment_analysis']['sentiment_summary']['overall']}")
```

## 🛠️ Development Tips

- Use `--reload` flag with uvicorn for auto-reload during development
- Check logs for debugging: `docker compose logs -f <service-name>`
- Test individual services before testing the full pipeline
- Use the `/docs` endpoints for interactive API testing

Happy coding! 🎉
