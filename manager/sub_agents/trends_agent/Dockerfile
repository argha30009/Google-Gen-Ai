# Trends Agent Microservice Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY agent.py .
COPY server.py .

# Create a minimal __init__.py file
RUN echo "# Trends Agent" > __init__.py

# Expose port
EXPOSE 8003

# Run the server
CMD ["python", "server.py"]
