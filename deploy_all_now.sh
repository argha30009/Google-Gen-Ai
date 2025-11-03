#!/bin/bash

# Simple deployment script for all microservices
set -e

PROJECT_ID="misinformation-detector-476811"
REGION="asia-south1"
# SECURITY: API_KEY should be passed as environment variable
# Usage: API_KEY=your_key_here bash deploy_all_now.sh
API_KEY="${GOOGLE_API_KEY}"

echo "======================================"
echo "Deploying All Microservices"
echo "======================================"
echo ""

# Search Agent
echo "[1/5] Deploying Search Agent..."
cd manager/sub_agents/search_agent
gcloud run deploy search-agent \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet \
  --timeout=300

SEARCH_URL=$(gcloud run services describe search-agent --region $REGION --format='value(status.url)')
echo "✓ Search Agent: $SEARCH_URL"
cd ../../..

# Sentiment Agent
echo ""
echo "[2/5] Deploying Sentiment Agent..."
cd manager/sub_agents/sentiment_agent
gcloud run deploy sentiment-agent \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet \
  --timeout=300

SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region $REGION --format='value(status.url)')
echo "✓ Sentiment Agent: $SENTIMENT_URL"
cd ../../..

# Trends Agent
echo ""
echo "[3/5] Deploying Trends Agent..."
cd manager/sub_agents/trends_agent
gcloud run deploy trends-agent \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet \
  --timeout=300

TRENDS_URL=$(gcloud run services describe trends-agent --region $REGION --format='value(status.url)')
echo "✓ Trends Agent: $TRENDS_URL"
cd ../../..

# FactCheck Agent
echo ""
echo "[4/5] Deploying FactCheck Agent..."
cd manager/sub_agents/factcheck_agent
gcloud run deploy factcheck-agent \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet \
  --timeout=300

FACTCHECK_URL=$(gcloud run services describe factcheck-agent --region $REGION --format='value(status.url)')
echo "✓ FactCheck Agent: $FACTCHECK_URL"
cd ../../..

# Manager Agent
echo ""
echo "[5/5] Deploying Manager Agent..."
cd manager
gcloud run deploy manager-agent \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY,SEARCH_URL=$SEARCH_URL,SENTIMENT_URL=$SENTIMENT_URL,TRENDS_URL=$TRENDS_URL,FACTCHECK_URL=$FACTCHECK_URL \
  --quiet \
  --timeout=300

MANAGER_URL=$(gcloud run services describe manager-agent --region $REGION --format='value(status.url)')
echo "✓ Manager Agent: $MANAGER_URL"
cd ..

echo ""
echo "======================================"
echo "✅ ALL SERVICES DEPLOYED!"
echo "======================================"
echo ""
echo "Service URLs:"
echo "  Search Agent:    $SEARCH_URL"
echo "  Sentiment Agent: $SENTIMENT_URL"
echo "  Trends Agent:    $TRENDS_URL"
echo "  FactCheck Agent: $FACTCHECK_URL"
echo "  Manager Agent:   $MANAGER_URL"
echo ""
echo "Manager API: $MANAGER_URL/run"
