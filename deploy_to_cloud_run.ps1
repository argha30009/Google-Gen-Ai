# Google Cloud Run Deployment Script (PowerShell)
# Deploy all microservices to Cloud Run in asia-south1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Google Cloud Run Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = $env:GOOGLE_CLOUD_PROJECT
if (-not $PROJECT_ID) {
    $PROJECT_ID = gcloud config get-value project
}
$REGION = "asia-south1"
$SEARCH_SERVICE_NAME = "search-agent"
$SENTIMENT_SERVICE_NAME = "sentiment-agent"
$TRENDS_SERVICE_NAME = "trends-agent"
$MANAGER_SERVICE_NAME = "manager-agent"

Write-Host "📋 Configuration:"
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Region: $REGION"
Write-Host ""

# Check if gcloud is installed
try {
    gcloud version | Out-Null
} catch {
    Write-Host "❌ Error: gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
Write-Host ""

# Enable required APIs
Write-Host "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
Write-Host "✅ APIs enabled" -ForegroundColor Green
Write-Host ""

# Deploy Search Agent
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "1️⃣  Deploying Search Agent..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Push-Location manager/sub_agents/search_agent
gcloud run deploy $SEARCH_SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --project $PROJECT_ID

$SEARCH_URL = gcloud run services describe $SEARCH_SERVICE_NAME `
    --region $REGION `
    --format 'value(status.url)' `
    --project $PROJECT_ID
Write-Host "✅ Search Agent deployed at: $SEARCH_URL" -ForegroundColor Green
Write-Host ""
Pop-Location

# Deploy Sentiment Agent
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "2️⃣  Deploying Sentiment Agent..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Push-Location manager/sub_agents/sentiment_agent
gcloud run deploy $SENTIMENT_SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --project $PROJECT_ID

$SENTIMENT_URL = gcloud run services describe $SENTIMENT_SERVICE_NAME `
    --region $REGION `
    --format 'value(status.url)' `
    --project $PROJECT_ID
Write-Host "✅ Sentiment Agent deployed at: $SENTIMENT_URL" -ForegroundColor Green
Write-Host ""
Pop-Location

# Deploy Trends Agent
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "3️⃣  Deploying Trends Agent..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Push-Location manager/sub_agents/trends_agent
gcloud run deploy $TRENDS_SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --project $PROJECT_ID

$TRENDS_URL = gcloud run services describe $TRENDS_SERVICE_NAME `
    --region $REGION `
    --format 'value(status.url)' `
    --project $PROJECT_ID
Write-Host "✅ Trends Agent deployed at: $TRENDS_URL" -ForegroundColor Green
Write-Host ""
Pop-Location

# Deploy Manager Agent
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "4️⃣  Deploying Manager Agent..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Push-Location manager
gcloud run deploy $MANAGER_SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --set-env-vars "SEARCH_AGENT_URL=$SEARCH_URL,SENTIMENT_AGENT_URL=$SENTIMENT_URL,TRENDS_AGENT_URL=$TRENDS_URL" `
    --project $PROJECT_ID

$MANAGER_URL = gcloud run services describe $MANAGER_SERVICE_NAME `
    --region $REGION `
    --format 'value(status.url)' `
    --project $PROJECT_ID
Write-Host "✅ Manager Agent deployed at: $MANAGER_URL" -ForegroundColor Green
Write-Host ""
Pop-Location

# Summary
Write-Host "==========================================" -ForegroundColor Green
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Service URLs:"
Write-Host ""
Write-Host "1. Manager Service:    $MANAGER_URL"
Write-Host "   • Health:           $MANAGER_URL/health"
Write-Host "   • Docs:             $MANAGER_URL/docs"
Write-Host ""
Write-Host "2. Search Agent:       $SEARCH_URL"
Write-Host "   • Health:           $SEARCH_URL/health"
Write-Host "   • Docs:             $SEARCH_URL/docs"
Write-Host ""
Write-Host "3. Sentiment Agent:    $SENTIMENT_URL"
Write-Host "   • Health:           $SENTIMENT_URL/health"
Write-Host "   • Docs:             $SENTIMENT_URL/docs"
Write-Host ""
Write-Host "4. Trends Agent:       $TRENDS_URL"
Write-Host "   • Health:           $TRENDS_URL/health"
Write-Host "   • Docs:             $TRENDS_URL/docs"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 Quick Test:"
Write-Host "curl -X POST $MANAGER_URL/run ``" -ForegroundColor Yellow
Write-Host "  -H 'Content-Type: application/json' ``" -ForegroundColor Yellow
Write-Host "  -d '{`"query`": `"artificial intelligence`"}'" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
