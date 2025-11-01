#!/bin/bash

# Startup script for all microservices
# Run this from the project root directory

echo "🚀 Starting all microservices..."

# Define project root
PROJECT_ROOT="/c/Users/argha/Downloads/gh 5"
VENV_PYTHON="$PROJECT_ROOT/venv/Scripts/python.exe"

# Kill any existing services
echo "🧹 Cleaning up existing services..."
pkill -f "python.*server.py" 2>/dev/null || true
sleep 2

# Start Search Agent (Port 8001)
echo "📡 Starting Search Agent on port 8001..."
cd "$PROJECT_ROOT/manager/sub_agents/search_agent"
nohup "$VENV_PYTHON" server.py > search.log 2>&1 &
SEARCH_PID=$!
echo "   ✓ Search Agent started (PID: $SEARCH_PID)"

# Start Sentiment Agent (Port 8002)
echo "😊 Starting Sentiment Agent on port 8002..."
cd "$PROJECT_ROOT/manager/sub_agents/sentiment_agent"
nohup "$VENV_PYTHON" server.py > sentiment.log 2>&1 &
SENTIMENT_PID=$!
echo "   ✓ Sentiment Agent started (PID: $SENTIMENT_PID)"

# Start Trends Agent (Port 8003)
echo "📈 Starting Trends Agent on port 8003..."
cd "$PROJECT_ROOT/manager/sub_agents/trends_agent"
nohup "$VENV_PYTHON" server.py > trends.log 2>&1 &
TRENDS_PID=$!
echo "   ✓ Trends Agent started (PID: $TRENDS_PID)"

# Start Manager (Port 8000)
echo "🎯 Starting Manager Agent on port 8000..."
cd "$PROJECT_ROOT/manager"
nohup "$VENV_PYTHON" server.py > manager.log 2>&1 &
MANAGER_PID=$!
echo "   ✓ Manager Agent started (PID: $MANAGER_PID)"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check health of all services
echo ""
echo "🏥 Checking service health..."

check_service() {
    local port=$1
    local name=$2
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "   ✅ $name (port $port) is healthy"
        return 0
    else
        echo "   ❌ $name (port $port) is not responding"
        return 1
    fi
}

HEALTH_OK=true
check_service 8001 "Search Agent" || HEALTH_OK=false
check_service 8002 "Sentiment Agent" || HEALTH_OK=false
check_service 8003 "Trends Agent" || HEALTH_OK=false
check_service 8000 "Manager Agent" || HEALTH_OK=false

echo ""
if [ "$HEALTH_OK" = true ]; then
    echo "✨ All services are running successfully!"
    echo ""
    echo "📍 Service URLs:"
    echo "   - Manager (Main):    http://localhost:8000"
    echo "   - Search Agent:      http://localhost:8001"
    echo "   - Sentiment Agent:   http://localhost:8002"
    echo "   - Trends Agent:      http://localhost:8003"
    echo ""
    echo "🌐 Frontend: Start with 'cd frontend/frontend-magic-pattern && npm run dev'"
    echo ""
    echo "📋 To stop all services: pkill -f 'python.*server.py'"
else
    echo "⚠️  Some services failed to start. Check the log files:"
    echo "   - manager/sub_agents/search_agent/search.log"
    echo "   - manager/sub_agents/sentiment_agent/sentiment.log"
    echo "   - manager/sub_agents/trends_agent/trends.log"
    echo "   - manager/manager.log"
fi
