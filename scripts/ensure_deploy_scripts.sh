#!/bin/bash

# ensure_deploy_scripts.sh
# Verifies presence of deployment scripts and regenerates missing ones
# Usage: bash scripts/ensure_deploy_scripts.sh

# Color definitions
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
CYAN=$(tput setaf 6)
BOLD=$(tput bold)
RESET=$(tput sgr0)

# Header
echo "${CYAN}${BOLD}========================================${RESET}"
echo "${CYAN}${BOLD}  Deployment Scripts Verification${RESET}"
echo "${CYAN}${BOLD}========================================${RESET}"
echo ""

# Script directory
SCRIPT_DIR="scripts"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ensure we're in project root
cd "$PROJECT_ROOT" || exit 1

# Function to print success
print_success() {
    echo "${GREEN}✅ $1${RESET}"
}

# Function to print error
print_error() {
    echo "${RED}❌ $1${RESET}"
}

# Function to print info
print_info() {
    echo "${BLUE}ℹ️  $1${RESET}"
}

# Function to print warning
print_warning() {
    echo "${YELLOW}⚠️  $1${RESET}"
}

# Function to create deploy_backend.sh
create_deploy_backend() {
    cat > "$SCRIPT_DIR/deploy_backend.sh" << 'EOF'
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
EOF

    chmod +x "$SCRIPT_DIR/deploy_backend.sh"
    echo "${GREEN}🆕 Created: $SCRIPT_DIR/deploy_backend.sh${RESET}"
}

# Function to create deploy_frontend.sh
create_deploy_frontend() {
    cat > "$SCRIPT_DIR/deploy_frontend.sh" << 'EOF'
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
EOF

    chmod +x "$SCRIPT_DIR/deploy_frontend.sh"
    echo "${GREEN}🆕 Created: $SCRIPT_DIR/deploy_frontend.sh${RESET}"
}

# Function to create verify_deployment.sh
create_verify_deployment() {
    cat > "$SCRIPT_DIR/verify_deployment.sh" << 'EOF'
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
EOF

    chmod +x "$SCRIPT_DIR/verify_deployment.sh"
    echo "${GREEN}🆕 Created: $SCRIPT_DIR/verify_deployment.sh${RESET}"
}

# Main verification logic
echo "${BLUE}🔍 Checking deployment scripts...${RESET}"
echo ""

SCRIPTS_CHECKED=0
SCRIPTS_CREATED=0
SCRIPTS_EXIST=0

# Check deploy_backend.sh
echo -n "${CYAN}📦 Backend deploy script... ${RESET}"
if [ -f "$SCRIPT_DIR/deploy_backend.sh" ]; then
    print_success "Already exists"
    SCRIPTS_EXIST=$((SCRIPTS_EXIST + 1))
else
    echo ""
    create_deploy_backend
    SCRIPTS_CREATED=$((SCRIPTS_CREATED + 1))
fi
SCRIPTS_CHECKED=$((SCRIPTS_CHECKED + 1))

# Check deploy_frontend.sh
echo -n "${CYAN}🌐 Frontend deploy script... ${RESET}"
if [ -f "$SCRIPT_DIR/deploy_frontend.sh" ]; then
    print_success "Already exists"
    SCRIPTS_EXIST=$((SCRIPTS_EXIST + 1))
else
    echo ""
    create_deploy_frontend
    SCRIPTS_CREATED=$((SCRIPTS_CREATED + 1))
fi
SCRIPTS_CHECKED=$((SCRIPTS_CHECKED + 1))

# Check verify_deployment.sh
echo -n "${CYAN}🧪 Verification script... ${RESET}"
if [ -f "$SCRIPT_DIR/verify_deployment.sh" ]; then
    print_success "Already exists"
    SCRIPTS_EXIST=$((SCRIPTS_EXIST + 1))
else
    echo ""
    create_verify_deployment
    SCRIPTS_CREATED=$((SCRIPTS_CREATED + 1))
fi
SCRIPTS_CHECKED=$((SCRIPTS_CHECKED + 1))

# Summary
echo ""
echo "${CYAN}${BOLD}========================================${RESET}"
echo "${GREEN}${BOLD}✅ All deployment scripts verified${RESET}"
echo "${CYAN}${BOLD}========================================${RESET}"
echo ""
echo "${BLUE}Summary:${RESET}"
echo "  Total scripts checked: ${CYAN}$SCRIPTS_CHECKED${RESET}"
echo "  Already existed: ${GREEN}$SCRIPTS_EXIST${RESET}"
echo "  Newly created: ${YELLOW}$SCRIPTS_CREATED${RESET}"
echo ""

if [ $SCRIPTS_CREATED -gt 0 ]; then
    echo "${GREEN}🆕 Created $SCRIPTS_CREATED new script(s)${RESET}"
    echo ""
fi

echo "${CYAN}Available deployment scripts:${RESET}"
echo "  ${GREEN}✓${RESET} $SCRIPT_DIR/deploy_backend.sh"
echo "  ${GREEN}✓${RESET} $SCRIPT_DIR/deploy_frontend.sh"
echo "  ${GREEN}✓${RESET} $SCRIPT_DIR/verify_deployment.sh"
echo ""
echo "${CYAN}${BOLD}🎯 All deployment scripts ready!${RESET}"
echo ""
echo "You can now run:"
echo "  ${YELLOW}bash scripts/deploy_all.sh${RESET}        ${BLUE}# Deploy everything${RESET}"
echo "  ${YELLOW}bash scripts/deploy_backend.sh${RESET}    ${BLUE}# Deploy backend only${RESET}"
echo "  ${YELLOW}bash scripts/deploy_frontend.sh${RESET}   ${BLUE}# Deploy frontend only${RESET}"
echo "  ${YELLOW}bash scripts/verify_deployment.sh${RESET} ${BLUE}# Verify deployments${RESET}"
echo ""

# Make this script executable once using:
# chmod +x scripts/ensure_deploy_scripts.sh
