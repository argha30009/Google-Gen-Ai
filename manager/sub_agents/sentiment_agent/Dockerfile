# Sentiment Agent Microservice Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download TextBlob corpora
RUN python -m textblob.download_corpora

# Copy the agent code
COPY agent.py .
COPY server.py .

# Create a minimal __init__.py file
RUN echo "# Sentiment Agent" > __init__.py

# Expose port
EXPOSE 8002

# Run the server (PORT environment variable will be read from server.py)
CMD ["python", "server.py"]
