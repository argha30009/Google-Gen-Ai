#!/bin/bash

# Deploy all microservices to Cloud Run
# This script builds and deploys all agent services

set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="asia-south1"
# API_KEY should be passed as environment variable
# Usage: API_KEY="your-key-here" bash deploy_all_agents.sh
if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY environment variable is not set"
    echo "Usage: API_KEY='your-api-key' bash deploy_all_agents.sh"
    exit 1
fi

echo "🚀 Starting deployment of all microservices..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Array to store service URLs
declare -A SERVICE_URLS

# Deploy Search Agent
echo "📦 Building and deploying Search Agent..."
cd manager/sub_agents/search_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/search-agent .
gcloud run deploy search-agent \
  --image gcr.io/$PROJECT_ID/search-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet

SEARCH_URL=$(gcloud run services describe search-agent --region $REGION --format='value(status.url)')
SERVICE_URLS[SEARCH]=$SEARCH_URL
echo "✅ Search Agent deployed: $SEARCH_URL"
cd ../../..

# Deploy Sentiment Agent
echo ""
echo "📦 Building and deploying Sentiment Agent..."
cd manager/sub_agents/sentiment_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/sentiment-agent .
gcloud run deploy sentiment-agent \
  --image gcr.io/$PROJECT_ID/sentiment-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet

SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region $REGION --format='value(status.url)')
SERVICE_URLS[SENTIMENT]=$SENTIMENT_URL
echo "✅ Sentiment Agent deployed: $SENTIMENT_URL"
cd ../../..

# Deploy Trends Agent
echo ""
echo "📦 Building and deploying Trends Agent..."
cd manager/sub_agents/trends_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/trends-agent .
gcloud run deploy trends-agent \
  --image gcr.io/$PROJECT_ID/trends-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --quiet

TRENDS_URL=$(gcloud run services describe trends-agent --region $REGION --format='value(status.url)')
SERVICE_URLS[TRENDS]=$TRENDS_URL
echo "✅ Trends Agent deployed: $TRENDS_URL"
cd ../../..

# Deploy Manager Service with updated environment variables
echo ""
echo "📦 Redeploying Manager Service with updated URLs..."
gcloud run deploy manager-service \
  --image gcr.io/$PROJECT_ID/manager-service \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY,SEARCH_AGENT_URL=$SEARCH_URL,SENTIMENT_AGENT_URL=$SENTIMENT_URL,TRENDS_AGENT_URL=$TRENDS_URL \
  --quiet

MANAGER_URL=$(gcloud run services describe manager-service --region $REGION --format='value(status.url)')
echo "✅ Manager Service deployed: $MANAGER_URL"

# Print summary
echo ""
echo "🎉 All services deployed successfully!"
echo ""
echo "Service URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Manager:   $MANAGER_URL"
echo "Search:    $SEARCH_URL"
echo "Sentiment: $SENTIMENT_URL"
echo "Trends:    $TRENDS_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Test the manager service:"
echo "curl -X POST $MANAGER_URL/run -H 'Content-Type: application/json' -d '{\"query\": \"Climate change impact\"}'"
