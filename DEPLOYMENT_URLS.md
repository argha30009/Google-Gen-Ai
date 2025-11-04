# ��� DEPLOYMENT SUMMARY - Google Cloud Platform

## ✅ Backend Microservices (Cloud Run)

All services deployed in **asia-south1** region:

### 1. **Search Agent**
- URL: https://search-agent-betutdirna-el.a.run.app
- Health: https://search-agent-betutdirna-el.a.run.app/health
- Docs: https://search-agent-betutdirna-el.a.run.app/docs

### 2. **Sentiment Agent**
- URL: https://sentiment-agent-betutdirna-el.a.run.app
- Health: https://sentiment-agent-betutdirna-el.a.run.app/health
- Docs: https://sentiment-agent-betutdirna-el.a.run.app/docs

### 3. **Trends Agent**
- URL: https://trends-agent-betutdirna-el.a.run.app
- Health: https://trends-agent-betutdirna-el.a.run.app/health
- Docs: https://trends-agent-betutdirna-el.a.run.app/docs

### 4. **FactCheck Agent**
- URL: https://factcheck-agent-betutdirna-el.a.run.app
- Health: https://factcheck-agent-betutdirna-el.a.run.app/health
- Docs: https://factcheck-agent-betutdirna-el.a.run.app/docs

### 5. **Manager Agent (Main API)** ✅ UPDATED
- URL: https://manager-agent-466223788759.asia-south1.run.app
- Health: https://manager-agent-466223788759.asia-south1.run.app/health
- API: https://manager-agent-466223788759.asia-south1.run.app/run
- Docs: https://manager-agent-466223788759.asia-south1.run.app/docs
- **Previous URL** (deprecated): https://manager-agent-betutdirna-el.a.run.app

## 🌐 Frontend (Google Cloud Storage) ✅ UPDATED

- **Main URL**: https://storage.googleapis.com/clipse-app/index.html
- **Bucket**: gs://clipse-app
- **Previous Bucket** (deprecated): gs://news-analysis-frontend-1762108971

## ��� Project Details

- **Project ID**: misinformation-detector-476811
- **Region**: asia-south1
- **Deployment Date**: November 2, 2025

## ��� Testing the API

```bash
curl -X POST https://manager-agent-betutdirna-el.a.run.app/run \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence news"}'
```

## ��� Redeployment Commands

### Redeploy a specific service:
```bash
cd manager/sub_agents/[service-name]
gcloud run deploy [service-name] --source . --region asia-south1 --allow-unauthenticated
```

### Redeploy frontend:
```bash
cd frontend/frontend-magic-pattern
npm run build
gsutil -m cp -r dist/* gs://news-analysis-frontend-1762108971/
```

## ��� Monitoring

View logs in Google Cloud Console:
- Cloud Run Logs: https://console.cloud.google.com/run?project=misinformation-detector-476811
- Storage Logs: https://console.cloud.google.com/storage/browser?project=misinformation-detector-476811

