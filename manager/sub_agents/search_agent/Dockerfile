# Search Agent Microservice Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY agent.py .
COPY server.py .
COPY __init__.py . 2>/dev/null || echo "# Search Agent" > __init__.py

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
