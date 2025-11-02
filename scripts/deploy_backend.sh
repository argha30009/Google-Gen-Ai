#!/bin/bash

# deploy_backend.sh
# Builds and deploys the FastAPI backend to Google Cloud Run
# Region: asia-south1

set -e

# Colors
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

echo "${CYAN}========================================${RESET}"
echo "${CYAN}  Deploying Backend to Cloud Run${RESET}"
echo "${CYAN}========================================${RESET}"
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "${RED}❌ No active GCP project found.${RESET}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "${CYAN}📦 Active Project: $PROJECT_ID${RESET}"
echo ""

# Configuration
SERVICE_NAME="manager-service"
REGION="asia-south1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
BACKEND_DIR="manager"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "${RED}❌ Backend directory '$BACKEND_DIR' not found.${RESET}"
    exit 1
fi

echo "${YELLOW}🔨 Building container image...${RESET}"
cd "$BACKEND_DIR"

# Build with Cloud Build
if gcloud builds submit --tag "$IMAGE_NAME" .; then
    echo "${GREEN}✅ Container image built successfully${RESET}"
else
    echo "${RED}❌ Failed to build container image${RESET}"
    exit 1
fi

echo ""
echo "${YELLOW}🚀 Deploying to Cloud Run...${RESET}"

# Deploy to Cloud Run
if gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY:-}" \
    --port 8000; then
    echo ""
    echo "${GREEN}✅ Backend deployed successfully!${RESET}"
else
    echo "${RED}❌ Deployment failed${RESET}"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format='value(status.url)' 2>/dev/null)

echo ""
echo "${CYAN}========================================${RESET}"
echo "${GREEN}🎉 Deployment Complete!${RESET}"
echo "${CYAN}========================================${RESET}"
echo ""
echo "${CYAN}Backend URL:${RESET} $SERVICE_URL"
echo ""
echo "Test with:"
echo "  ${YELLOW}curl -X POST $SERVICE_URL/run \\${RESET}"
echo "    ${YELLOW}-H 'Content-Type: application/json' \\${RESET}"
echo "    ${YELLOW}-d '{\"query\": \"AI news\"}'${RESET}"
echo ""
