# Manager Agent Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the manager code
COPY agent.py .
COPY server.py .

# Create a minimal __init__.py file
RUN echo "# Manager Agent" > __init__.py

# Expose port for the FastAPI server
EXPOSE 8000

# Run the FastAPI server
CMD ["python", "server.py"]
