#!/bin/bash

# Google Cloud Run Deployment Script
# Deploy all microservices to Cloud Run in asia-south1

set -e

echo "=========================================="
echo "  Google Cloud Run Deployment Script"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="asia-south1"
SEARCH_SERVICE_NAME="search-agent"
SENTIMENT_SERVICE_NAME="sentiment-agent"
TRENDS_SERVICE_NAME="trends-agent"
MANAGER_SERVICE_NAME="manager-agent"

echo "📋 Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ Error: Not logged in to gcloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
echo "✅ APIs enabled"
echo ""

# Deploy Search Agent
echo "=========================================="
echo "1️⃣  Deploying Search Agent..."
echo "=========================================="
cd manager/sub_agents/search_agent
gcloud run deploy $SEARCH_SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project $PROJECT_ID

SEARCH_URL=$(gcloud run services describe $SEARCH_SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)
echo "✅ Search Agent deployed at: $SEARCH_URL"
echo ""
cd ../../..

# Deploy Sentiment Agent
echo "=========================================="
echo "2️⃣  Deploying Sentiment Agent..."
echo "=========================================="
cd manager/sub_agents/sentiment_agent
gcloud run deploy $SENTIMENT_SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project $PROJECT_ID

SENTIMENT_URL=$(gcloud run services describe $SENTIMENT_SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)
echo "✅ Sentiment Agent deployed at: $SENTIMENT_URL"
echo ""
cd ../../..

# Deploy Trends Agent
echo "=========================================="
echo "3️⃣  Deploying Trends Agent..."
echo "=========================================="
cd manager/sub_agents/trends_agent
gcloud run deploy $TRENDS_SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project $PROJECT_ID

TRENDS_URL=$(gcloud run services describe $TRENDS_SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)
echo "✅ Trends Agent deployed at: $TRENDS_URL"
echo ""
cd ../../..

# Deploy Manager Agent
echo "=========================================="
echo "4️⃣  Deploying Manager Agent..."
echo "=========================================="
cd manager
gcloud run deploy $MANAGER_SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "SEARCH_AGENT_URL=$SEARCH_URL,SENTIMENT_AGENT_URL=$SENTIMENT_URL,TRENDS_AGENT_URL=$TRENDS_URL" \
    --project $PROJECT_ID

MANAGER_URL=$(gcloud run services describe $MANAGER_SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)
echo "✅ Manager Agent deployed at: $MANAGER_URL"
echo ""
cd ..

# Summary
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📍 Service URLs:"
echo ""
echo "1. Manager Service:    $MANAGER_URL"
echo "   • Health:           $MANAGER_URL/health"
echo "   • Docs:             $MANAGER_URL/docs"
echo ""
echo "2. Search Agent:       $SEARCH_URL"
echo "   • Health:           $SEARCH_URL/health"
echo "   • Docs:             $SEARCH_URL/docs"
echo ""
echo "3. Sentiment Agent:    $SENTIMENT_URL"
echo "   • Health:           $SENTIMENT_URL/health"
echo "   • Docs:             $SENTIMENT_URL/docs"
echo ""
echo "4. Trends Agent:       $TRENDS_URL"
echo "   • Health:           $TRENDS_URL/health"
echo "   • Docs:             $TRENDS_URL/docs"
echo ""
echo "=========================================="
echo "🧪 Quick Test:"
echo "curl -X POST $MANAGER_URL/run \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"artificial intelligence\"}'"
echo "=========================================="
