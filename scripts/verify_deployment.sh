#!/bin/bash

# verify_deployment.sh
# Verifies that backend and frontend deployments are working correctly
# Tests API endpoints and measures response times

set -e

# Colors
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
BLUE=$(tput setaf 4)
BOLD=$(tput bold)
RESET=$(tput sgr0)

echo "${CYAN}${BOLD}========================================${RESET}"
echo "${CYAN}${BOLD}  Deployment Verification${RESET}"
echo "${CYAN}${BOLD}========================================${RESET}"
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "${RED}❌ No active GCP project found.${RESET}"
    exit 1
fi

echo "${BLUE}📦 Project: $PROJECT_ID${RESET}"
echo ""

# Configuration
SERVICE_NAME="manager-service"
REGION="asia-south1"
BUCKET_NAME="misinformation-frontend"

# Results tracking
BACKEND_STATUS="❌"
FRONTEND_STATUS="❌"
API_STATUS="❌"
RESPONSE_TIME="N/A"

echo "${YELLOW}🔍 Checking backend deployment...${RESET}"

# Get Cloud Run service URL
BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format='value(status.url)' 2>/dev/null)

if [ -n "$BACKEND_URL" ]; then
    echo "${CYAN}Backend URL: $BACKEND_URL${RESET}"
    
    # Test backend health
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 404 ]; then
        BACKEND_STATUS="${GREEN}✅${RESET}"
        echo "${GREEN}✅ Backend is responding (HTTP $HTTP_CODE)${RESET}"
    else
        echo "${RED}❌ Backend not responding properly (HTTP $HTTP_CODE)${RESET}"
    fi
else
    echo "${RED}❌ Backend service not found${RESET}"
fi

echo ""
echo "${YELLOW}🔍 Checking frontend deployment...${RESET}"

# Frontend URL
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo "${CYAN}Frontend URL: $FRONTEND_URL${RESET}"

# Test frontend availability
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")

if [ "$FRONTEND_CODE" -eq 200 ]; then
    FRONTEND_STATUS="${GREEN}✅${RESET}"
    echo "${GREEN}✅ Frontend is accessible (HTTP $FRONTEND_CODE)${RESET}"
else
    echo "${RED}❌ Frontend not accessible (HTTP $FRONTEND_CODE)${RESET}"
fi

echo ""
echo "${YELLOW}🔍 Testing API endpoint...${RESET}"

if [ -n "$BACKEND_URL" ]; then
    # Test API with sample request
    TEST_PAYLOAD='{"query": "test"}'
    
    START_TIME=$(date +%s.%N)
    API_RESPONSE=$(curl -s -X POST "$BACKEND_URL/run" \
        -H "Content-Type: application/json" \
        -d "$TEST_PAYLOAD" \
        -w "\n%{http_code}" 2>/dev/null || echo "000")
    END_TIME=$(date +%s.%N)
    
    API_CODE=$(echo "$API_RESPONSE" | tail -n1)
    RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc 2>/dev/null || echo "0")
    RESPONSE_TIME=$(printf "%.2fs" "$RESPONSE_TIME")
    
    if [ "$API_CODE" -eq 200 ]; then
        API_STATUS="${GREEN}✅${RESET}"
        echo "${GREEN}✅ API responding correctly (HTTP $API_CODE)${RESET}"
        echo "${CYAN}Response time: $RESPONSE_TIME${RESET}"
    else
        echo "${RED}❌ API not responding (HTTP $API_CODE)${RESET}"
    fi
else
    echo "${YELLOW}⚠️  Skipping API test (backend URL not available)${RESET}"
fi

# Summary Table
echo ""
echo "${CYAN}${BOLD}========================================${RESET}"
echo "${CYAN}${BOLD}  Verification Summary${RESET}"
echo "${CYAN}${BOLD}========================================${RESET}"
echo ""
printf "${BOLD}%-25s %s${RESET}\n" "Component" "Status"
echo "----------------------------------------"
printf "%-25s %b\n" "Backend (Cloud Run)" "$BACKEND_STATUS"
printf "%-25s %b\n" "Frontend (GCS)" "$FRONTEND_STATUS"
printf "%-25s %b\n" "API Endpoint" "$API_STATUS"
printf "%-25s %s\n" "Response Time" "$RESPONSE_TIME"
echo "----------------------------------------"
echo ""

# URLs
if [ -n "$BACKEND_URL" ]; then
    echo "${CYAN}📍 Backend:${RESET}  $BACKEND_URL"
fi
echo "${CYAN}📍 Frontend:${RESET} $FRONTEND_URL"
echo ""

# Overall status
if [[ "$BACKEND_STATUS" == *"✅"* ]] && [[ "$FRONTEND_STATUS" == *"✅"* ]]; then
    echo "${GREEN}${BOLD}🎉 All systems operational!${RESET}"
    exit 0
else
    echo "${RED}${BOLD}⚠️  Some components are not working properly${RESET}"
    exit 1
fi
