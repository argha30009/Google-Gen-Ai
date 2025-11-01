# Manager Agent Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the manager code
COPY agent.py .
COPY __init__.py . 2>/dev/null || echo "# Manager Agent" > __init__.py

# The manager doesn't expose a port - it's a client that calls other services
# You can run it interactively or as a script

CMD ["python", "-c", "from agent import root_agent; print('Manager agent ready. Use root_agent.run(query) to execute.')"]
