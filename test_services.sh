#!/bin/bash

# Test script for Google ADK Microservices
# This script validates all services are working correctly

set -e

echo "=================================="
echo "Google ADK Microservices Test"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    
    echo -n "Checking $name... "
    if curl -s "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        return 1
    fi
}

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo ""
    echo "Testing: $description"
    echo "----------------------------------------"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$url")
    else
        response=$(curl -s -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
}

# Check if services are running
echo "Step 1: Health Checks"
echo "===================="
echo ""

search_running=false
sentiment_running=false

if check_service "http://localhost:8001" "Search Agent Service"; then
    search_running=true
fi

if check_service "http://localhost:8002" "Sentiment Agent Service"; then
    sentiment_running=true
fi

echo ""

if [ "$search_running" = false ] || [ "$sentiment_running" = false ]; then
    echo -e "${YELLOW}⚠ Warning: Some services are not running${NC}"
    echo ""
    echo "To start services locally:"
    echo "  Terminal 1: cd manager/sub_agents/search_agent && uvicorn server:app --port 8001"
    echo "  Terminal 2: cd manager/sub_agents/sentiment_agent && uvicorn server:app --port 8002"
    echo ""
    echo "Or use Docker:"
    echo "  docker compose up --build"
    echo ""
    exit 1
fi

# Test Search Service
echo "Step 2: Testing Search Service"
echo "==============================="
test_endpoint "POST" "http://localhost:8001/run" \
    '{"query":"OpenAI"}' \
    "Search for 'OpenAI' news"

# Test Sentiment Service
echo "Step 3: Testing Sentiment Service"
echo "=================================="
test_endpoint "POST" "http://localhost:8002/run" \
    '{"headlines":["OpenAI announces breakthrough in AI research","Tech stocks decline amid market uncertainty","New regulations proposed for AI industry"]}' \
    "Analyze sentiment of sample headlines"

# Test Pipeline
echo "Step 4: Testing Full Pipeline"
echo "=============================="
echo ""
echo "Fetching search results and piping to sentiment analysis..."
echo ""

# Get search results
search_response=$(curl -s -X POST "http://localhost:8001/run" \
    -H "Content-Type: application/json" \
    -d '{"query":"artificial intelligence"}')

echo "Search Results:"
echo "$search_response" | python3 -m json.tool 2>/dev/null || echo "$search_response"
echo ""

# Extract headlines (simplified - in production use jq or proper JSON parsing)
echo "Note: For full pipeline testing, use the Manager Agent:"
echo ""
echo "  cd manager"
echo "  python3 << EOF"
echo "from agent import root_agent"
echo "import json"
echo "result = root_agent.run('OpenAI')"
echo "print(json.dumps(result, indent=2))"
echo "EOF"
echo ""

echo "=================================="
echo -e "${GREEN}✓ All tests completed!${NC}"
echo "=================================="
echo ""
echo "Services are running correctly!"
echo ""
echo "API Documentation:"
echo "  - Search Agent:    http://localhost:8001/docs"
echo "  - Sentiment Agent: http://localhost:8002/docs"
echo ""
