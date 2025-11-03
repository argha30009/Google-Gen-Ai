#!/bin/bash
# Deploy all sub-agents to Cloud Run

set -e  # Exit on error

PROJECT_ID="misinformation-detector-476811"
REGION="asia-south1"
# SECURITY: API_KEY should be passed as environment variable
# Usage: API_KEY=your_key_here bash deploy_subagents.sh
API_KEY="${GOOGLE_API_KEY}"

echo "Building and deploying search agent..."
cd manager/sub_agents/search_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/search-agent .
gcloud run deploy search-agent \
  --image gcr.io/$PROJECT_ID/search-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --timeout=300 \
  --cpu=2 \
  --memory=2Gi

cd ../../..

echo "Building and deploying sentiment agent..."
cd manager/sub_agents/sentiment_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/sentiment-agent .
gcloud run deploy sentiment-agent \
  --image gcr.io/$PROJECT_ID/sentiment-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --timeout=300 \
  --cpu=2 \
  --memory=2Gi

cd ../../..

echo "Building and deploying trends agent..."
cd manager/sub_agents/trends_agent
gcloud builds submit --tag gcr.io/$PROJECT_ID/trends-agent .
gcloud run deploy trends-agent \
  --image gcr.io/$PROJECT_ID/trends-agent \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$API_KEY \
  --timeout=300 \
  --cpu=2 \
  --memory=2Gi

cd ../../..

echo "All sub-agents deployed successfully!"

# Get URLs
echo ""
echo "Service URLs:"
gcloud run services list --region $REGION --format="table(metadata.name,status.url)"
