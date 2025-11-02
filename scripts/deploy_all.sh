#!/bin/bash
# 🚀 Full deployment script for GH-5 project
# Deploys both backend (FastAPI) and frontend (React)

GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

echo "${YELLOW}🚀 Starting full project deployment...${RESET}"

# Verify scripts exist
if [ ! -f scripts/deploy_backend.sh ]; then
  echo "${RED}❌ Backend deploy script missing: scripts/deploy_backend.sh${RESET}"
  exit 1
fi

if [ ! -f scripts/deploy_frontend.sh ]; then
  echo "${RED}❌ Frontend deploy script missing: scripts/deploy_frontend.sh${RESET}"
  exit 1
fi

# Step 1: Deploy backend
echo "${YELLOW}📦 Deploying Backend (Cloud Run)...${RESET}"
bash scripts/deploy_backend.sh
if [ $? -ne 0 ]; then
  echo "${RED}❌ Backend deployment failed.${RESET}"
  exit 1
fi

# Step 2: Deploy frontend
echo "${YELLOW}🌐 Deploying Frontend (GCS + CDN)...${RESET}"
bash scripts/deploy_frontend.sh
if [ $? -ne 0 ]; then
  echo "${RED}❌ Frontend deployment failed.${RESET}"
  exit 1
fi

# Step 3: Done
echo ""
echo "${GREEN}✅ All components deployed successfully!${RESET}"
echo "-------------------------------------------"
echo "🧠 Backend (FastAPI):   gcloud run services list"
echo "🌍 Frontend (React):    https://storage.googleapis.com/misinformation-frontend/index.html"
echo "-------------------------------------------"
