# 🚀 Quick Start Guide

## Get Started in 3 Steps!

### Step 1: Install Frontend Dependencies
```bash
cd "frontend/frontend-magic-pattern"
npm install
```

### Step 2: Start All Backend Services
```bash
# From project root
chmod +x start_services.sh
./start_services.sh
```

Wait for all services to show ✅ healthy status.

### Step 3: Start Frontend
```bash
cd "frontend/frontend-magic-pattern"
npm run dev
```

## 🌐 Access the Application

Open your browser to: **http://localhost:5173**

## 🔍 Try These Queries

**Valid News Queries:**
- "AI news"
- "latest technology updates"
- "climate change news"
- "cryptocurrency trends"

**Invalid (Non-News) Queries:**
- "2 + 2" (math)
- "recipe for pasta" (cooking)
- "write code for sorting" (programming)

These will return "Could not find any data for the topic"

## 📍 Service URLs

- **Frontend**: http://localhost:5173
- **Manager API**: http://localhost:8000
- **Search Agent**: http://localhost:8001
- **Sentiment Agent**: http://localhost:8002
- **Trends Agent**: http://localhost:8003

## 🛑 Stop All Services

```bash
chmod +x stop_services.sh
./stop_services.sh
```

## 📚 More Information

- See `FRONTEND_INTEGRATION_SUMMARY.md` for full details
- See `frontend/INTEGRATION_README.md` for technical documentation

---

**That's it! You're ready to go!** 🎉
