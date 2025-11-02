#!/bin/bash

# Startup script for all Google ADK services
# This script starts all services with proper delays and health checks

set -e

echo "=================================="
echo "Starting Google ADK Services"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an | grep ":$port.*LISTEN" >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be healthy
wait_for_service() {
    local url=$1
    local name=$2
    local max_wait=60
    local waited=0
    
    echo -n "Waiting for $name to be ready..."
    while [ $waited -lt $max_wait ]; do
        if curl -s "$url/health" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        waited=$((waited + 2))
    done
    
    echo -e " ${RED}✗ Timeout${NC}"
    return 1
}

# Kill any existing services
echo -e "${YELLOW}Stopping any existing services...${NC}"
pkill -f "python.*server.py" 2>/dev/null || true
pkill -f "uvicorn.*server:app" 2>/dev/null || true
sleep 3

# Check if ports are free
echo ""
echo "Checking ports..."
for port in 8000 8001 8002 8003; do
    if check_port $port; then
        echo -e "${RED}✗ Port $port is still in use. Waiting...${NC}"
        sleep 3
        if check_port $port; then
            echo -e "${RED}✗ Port $port could not be freed. Please check and kill the process manually.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Port $port is free${NC}"
    fi
done

echo ""
echo -e "${BLUE}Starting services...${NC}"
echo ""

# Start Search Agent
echo -e "${BLUE}[1/4]${NC} Starting Search Agent (port 8001)..."
cd manager/sub_agents/search_agent
nohup python server.py > ../../../search.log 2>&1 &
SEARCH_PID=$!
echo "      PID: $SEARCH_PID"
cd ../../..
sleep 5

# Start Sentiment Agent
echo -e "${BLUE}[2/4]${NC} Starting Sentiment Agent (port 8002)..."
cd manager/sub_agents/sentiment_agent
nohup python server.py > ../../../sentiment.log 2>&1 &
SENTIMENT_PID=$!
echo "      PID: $SENTIMENT_PID"
cd ../../..
sleep 5

# Start Trends Agent
echo -e "${BLUE}[3/4]${NC} Starting Trends Agent (port 8003)..."
cd manager/sub_agents/trends_agent
nohup python server.py > ../../../trends.log 2>&1 &
TRENDS_PID=$!
echo "      PID: $TRENDS_PID"
cd ../..
sleep 5

# Start Manager Service
echo -e "${BLUE}[4/4]${NC} Starting Manager Service (port 8000)..."
cd manager
nohup python server.py > ../manager.log 2>&1 &
MANAGER_PID=$!
echo "      PID: $MANAGER_PID"
cd ..
sleep 5

echo ""
echo "Performing health checks..."
echo ""

# Wait for all services
all_healthy=true
if ! wait_for_service "http://localhost:8001" "Search Agent"; then
    all_healthy=false
fi

if ! wait_for_service "http://localhost:8002" "Sentiment Agent"; then
    all_healthy=false
fi

if ! wait_for_service "http://localhost:8003" "Trends Agent"; then
    all_healthy=false
fi

if ! wait_for_service "http://localhost:8000" "Manager Service"; then
    all_healthy=false
fi

echo ""
if [ "$all_healthy" = true ]; then
    echo "=================================="
    echo -e "${GREEN}✓ All services started successfully!${NC}"
    echo "=================================="
    echo ""
    echo "Service URLs:"
    echo "  - Manager Service:   http://localhost:8000"
    echo "  - Search Agent:      http://localhost:8001"
    echo "  - Sentiment Agent:   http://localhost:8002"
    echo "  - Trends Agent:      http://localhost:8003"
    echo ""
    echo "API Documentation:"
    echo "  - Manager:    http://localhost:8000/docs"
    echo "  - Search:     http://localhost:8001/docs"
    echo "  - Sentiment:  http://localhost:8002/docs"
    echo "  - Trends:     http://localhost:8003/docs"
    echo ""
    echo "Logs:"
    echo "  - Manager:    manager.log"
    echo "  - Search:     search.log"
    echo "  - Sentiment:  sentiment.log"
    echo "  - Trends:     trends.log"
    echo ""
    echo "To test the system:"
    echo "  curl -X POST http://localhost:8000/run \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"query\": \"artificial intelligence trends\"}'"
    echo ""
    echo "To stop all services:"
    echo "  pkill -f 'python.*server.py'"
    echo ""
else
    echo "=================================="
    echo -e "${RED}✗ Some services failed to start${NC}"
    echo "=================================="
    echo ""
    echo "Check the log files for errors:"
    echo "  - tail -f manager.log"
    echo "  - tail -f search.log"
    echo "  - tail -f sentiment.log"
    echo "  - tail -f trends.log"
    echo ""
    exit 1
fi
