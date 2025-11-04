# 🔧 Troubleshooting Guide

## Frontend Shows Old Error

If you still see the HTTP 500 error after deployment:

### Solution 1: Clear Browser Cache
1. Open your browser's developer console (F12)
2. Right-click on the refresh button
3. Select "Empty Cache and Hard Reload"
4. Or use Ctrl+Shift+Delete to clear cache

### Solution 2: Force Refresh
- **Chrome/Edge**: Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- **Firefox**: Press `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- **Safari**: Press `Cmd + Option + R`

### Solution 3: Use Incognito/Private Mode
Open the URL in an incognito/private browsing window to bypass cache:
```
https://storage.googleapis.com/clipse-app/index.html
```

### Solution 4: Add Cache-Busting Query Parameter
Add `?v=2` to the URL:
```
https://storage.googleapis.com/clipse-app/index.html?v=2
```

## Backend Service Errors

### Check Service Health
Test each service individually:

```bash
# Manager Agent
curl https://manager-agent-466223788759.asia-south1.run.app/health

# Search Agent
curl https://search-agent-466223788759.asia-south1.run.app/health

# Sentiment Agent
curl https://sentiment-agent-betutdirna-el.a.run.app/health

# FactCheck Agent
curl https://factcheck-agent-466223788759.asia-south1.run.app/health

# Trends Agent
curl https://trends-agent-466223788759.asia-south1.run.app/health
```

### Check Service Logs
```bash
# View manager agent logs
gcloud run services logs read manager-agent --region asia-south1 --limit 50

# View specific agent logs
gcloud run services logs read search-agent --region asia-south1 --limit 50
```

### Verify Environment Variables
```bash
# Check manager agent configuration
gcloud run services describe manager-agent --region asia-south1 --format="get(spec.template.spec.containers[0].env)"
```

## Common Issues

### Issue: "CORS Error"
**Solution**: Manager agent has CORS enabled. If you see this error, check that you're accessing from the correct domain.

### Issue: "Timeout Error"
**Solution**: Cloud Run services have a 300-second timeout. For long-running queries, this is expected. The frontend should handle timeouts gracefully.

### Issue: "Authentication Required"
**Solution**: All services are configured with `--allow-unauthenticated`. If you see auth errors, redeploy the service:
```bash
gcloud run services update manager-agent --region asia-south1 --allow-unauthenticated
```

### Issue: "Service Unavailable (503)"
**Solution**: The service might be cold-starting. Wait 10-15 seconds and try again. Cloud Run services scale down to zero when idle.

## Verification Commands

### Test Complete Flow
```bash
# Test a simple query
curl -X POST "https://manager-agent-466223788759.asia-south1.run.app/run" \
  -H "Content-Type: application/json" \
  -d '{"input": "What is climate change?"}'
```

### Check Frontend is Loading
```bash
curl -I https://storage.googleapis.com/clipse-app/index.html
```

Should return `HTTP/1.1 200 OK`

## Emergency Redeployment

If all else fails, redeploy everything:

```bash
# Redeploy manager agent
cd manager
gcloud run deploy manager-agent --source . --region asia-south1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_KEY,\
SEARCH_AGENT_URL=https://search-agent-466223788759.asia-south1.run.app,\
SENTIMENT_AGENT_URL=https://sentiment-agent-betutdirna-el.a.run.app,\
FACTCHECK_AGENT_URL=https://factcheck-agent-466223788759.asia-south1.run.app,\
TRENDS_AGENT_URL=https://trends-agent-466223788759.asia-south1.run.app

# Redeploy frontend
cd ../frontend/frontend-magic-pattern
npm run build
gsutil -m rsync -r -d dist/ gs://clipse-app/
```

## Support

If issues persist:
1. Check Cloud Build logs: https://console.cloud.google.com/cloud-build/builds
2. Check Cloud Run logs: https://console.cloud.google.com/run
3. Verify API quota: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

## Quick Status Check

Run this one-liner to check all services:
```bash
echo "Manager: $(curl -s -o /dev/null -w "%{http_code}" https://manager-agent-466223788759.asia-south1.run.app/)" && \
echo "Search: $(curl -s -o /dev/null -w "%{http_code}" https://search-agent-466223788759.asia-south1.run.app/health)" && \
echo "Sentiment: $(curl -s -o /dev/null -w "%{http_code}" https://sentiment-agent-betutdirna-el.a.run.app/health)" && \
echo "FactCheck: $(curl -s -o /dev/null -w "%{http_code}" https://factcheck-agent-466223788759.asia-south1.run.app/health)" && \
echo "Trends: $(curl -s -o /dev/null -w "%{http_code}" https://trends-agent-466223788759.asia-south1.run.app/health)"
```

All services should return `200`.
