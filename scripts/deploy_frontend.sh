#!/bin/bash

# deploy_frontend.sh
# Builds React frontend and deploys to Google Cloud Storage
# Makes bucket publicly accessible

set -e

# Colors
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

echo "${CYAN}========================================${RESET}"
echo "${CYAN}  Deploying Frontend to GCS${RESET}"
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
BUCKET_NAME="misinformation-frontend"
FRONTEND_DIR="frontend/frontend-magic-pattern"
DIST_DIR="$FRONTEND_DIR/dist"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "${RED}❌ Frontend directory '$FRONTEND_DIR' not found.${RESET}"
    exit 1
fi

echo "${YELLOW}🔨 Building React frontend...${RESET}"
cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "${CYAN}📦 Installing dependencies...${RESET}"
    npm install
fi

# Build frontend
if npm run build; then
    echo "${GREEN}✅ Frontend built successfully${RESET}"
else
    echo "${RED}❌ Failed to build frontend${RESET}"
    exit 1
fi

# Return to project root
cd ../..

echo ""
echo "${YELLOW}☁️  Setting up GCS bucket...${RESET}"

# Create bucket if it doesn't exist
if ! gsutil ls -b "gs://$BUCKET_NAME" >/dev/null 2>&1; then
    echo "${CYAN}Creating bucket: $BUCKET_NAME${RESET}"
    gsutil mb -p "$PROJECT_ID" -l asia-south1 "gs://$BUCKET_NAME"
    echo "${GREEN}✅ Bucket created${RESET}"
else
    echo "${CYAN}ℹ️  Bucket already exists${RESET}"
fi

# Configure bucket for website hosting
gsutil web set -m index.html -e 404.html "gs://$BUCKET_NAME" 2>/dev/null || true

echo ""
echo "${YELLOW}📤 Uploading files to GCS...${RESET}"

# Upload dist files
if gsutil -m rsync -r -d "$DIST_DIR" "gs://$BUCKET_NAME"; then
    echo "${GREEN}✅ Files uploaded successfully${RESET}"
else
    echo "${RED}❌ Failed to upload files${RESET}"
    exit 1
fi

# Make bucket public
echo ""
echo "${YELLOW}🔓 Making bucket publicly accessible...${RESET}"
gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"

# Set cache control for static assets
gsutil -m setmeta -h "Cache-Control:public, max-age=3600" "gs://$BUCKET_NAME/**"

FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"

echo ""
echo "${CYAN}========================================${RESET}"
echo "${GREEN}🎉 Frontend Deployment Complete!${RESET}"
echo "${CYAN}========================================${RESET}"
echo ""
echo "${CYAN}Frontend URL:${RESET} $FRONTEND_URL"
echo ""
echo "Alternative URLs:"
echo "  ${YELLOW}https://storage.cloud.google.com/$BUCKET_NAME/index.html${RESET}"
echo "  ${YELLOW}https://$BUCKET_NAME.storage.googleapis.com/index.html${RESET}"
echo ""
