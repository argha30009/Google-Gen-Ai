# Frontend Integration Guide

## Overview
The frontend has been successfully integrated with the backend microservices architecture. The React/TypeScript application now fetches real-time news data, sentiment analysis, and trends from the backend API.

## Architecture

### Backend (Python/FastAPI)
- **Manager Agent** (Port 8000): Orchestrates all microservices
- **Search Agent** (Port 8001): Fetches news headlines via Google Search
- **Sentiment Agent** (Port 8002): Analyzes sentiment using TextBlob
- **Trends Agent** (Port 8003): Provides Google Trends analysis

### Frontend (React/TypeScript/Vite)
- **Location**: `frontend/frontend-magic-pattern/`
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6

## Changes Made

### 1. Backend Changes (`manager/server.py`)
- ✅ Added CORS middleware to allow frontend access
- ✅ Configured to accept requests from `localhost:5173` (Vite default port)

### 2. Frontend Changes

#### Created Files:
- **`src/context/NewsContext.tsx`**: Global state management for news data
  - Handles API calls to backend
  - Manages loading states
  - Error handling
  - Provides `useNews()` hook

#### Modified Files:
- **`src/App.tsx`**: Wrapped with `NewsProvider` for global state access
- **`src/components/SearchBar.tsx`**: 
  - Integrated with backend API
  - Sends queries to `http://localhost:8000/run`
  - Navigates to dashboard on successful fetch
  
- **`src/components/FactCheckReport.tsx`**: Displays fact check from backend
- **`src/components/HeadlineSummary.tsx`**: Shows headlines with sentiment tags
- **`src/components/SentimentAnalysis.tsx`**: Real-time sentiment distribution
- **`src/components/BiasCheckReport.tsx`**: Bias analysis from backend
- **`src/components/ForensicAnalysis.tsx`**: Forensic analysis metrics

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Python 3.13+ with venv
- All backend services running

### Step 1: Install Frontend Dependencies
```bash
cd frontend/frontend-magic-pattern
npm install
```

### Step 2: Start Backend Services
Make sure all 4 microservices are running:

```bash
# Terminal 1: Search Agent
cd manager/sub_agents/search_agent
python server.py  # Port 8001

# Terminal 2: Sentiment Agent
cd manager/sub_agents/sentiment_agent
python server.py  # Port 8002

# Terminal 3: Trends Agent
cd manager/sub_agents/trends_agent
python server.py  # Port 8003

# Terminal 4: Manager
cd manager
python server.py  # Port 8000
```

Or use the nohup method:
```bash
# From project root
cd manager/sub_agents/search_agent && nohup python server.py > search.log 2>&1 &
cd manager/sub_agents/sentiment_agent && nohup python server.py > sentiment.log 2>&1 &
cd manager/sub_agents/trends_agent && nohup python server.py > trends.log 2>&1 &
cd manager && nohup python server.py > manager.log 2>&1 &
```

### Step 3: Start Frontend Development Server
```bash
cd frontend/frontend-magic-pattern
npm run dev
```

The frontend will start on **http://localhost:5173**

### Step 4: Test the Integration
1. Open browser to http://localhost:5173
2. Enter a news query (e.g., "AI news", "technology updates")
3. Click "Check" button
4. View results on the Dashboard page

## API Flow

```
User Input (Frontend)
    ↓
SearchBar Component
    ↓
useNews() Context
    ↓
POST http://localhost:8000/run
    ↓
Manager Agent
    ↓
Orchestrates: Search → Sentiment → Trends
    ↓
Returns Combined Results
    ↓
NewsContext Updates State
    ↓
Dashboard Components Re-render
```

## Data Structure

### Request to Backend:
```json
{
  "query": "AI news"
}
```

### Response from Backend:
```json
{
  "query": "AI news",
  "search_results": {
    "headlines": [
      {"title": "...", "query": "AI news"}
    ]
  },
  "sentiment_analysis": {
    "sentiment_summary": {
      "overall": "positive",
      "positive_count": 5,
      "negative_count": 2,
      "neutral_count": 3,
      "total_analyzed": 10
    },
    "per_item": [
      {
        "headline": "...",
        "sentiment": "positive",
        "polarity": 0.5,
        "subjectivity": 0.6
      }
    ]
  },
  "trends_analysis": {...},
  "summary": {
    "overview": "...",
    "sentiment_summary": "...",
    "fact_check": "...",
    "bias_check": "...",
    "forensic_analysis": "..."
  },
  "status": "success"
}
```

## Features

### ✅ Implemented
- Real-time news search
- Sentiment analysis visualization
- Fact check reporting
- Bias detection
- Forensic analysis
- Loading states
- Error handling
- Non-news query validation (returns "no data" for math, recipes, code queries)

### 🔄 Enhanced Components
- **SearchBar**: Live API integration with loading states
- **HeadlineSummary**: Displays actual headlines with sentiment badges
- **SentimentAnalysis**: Shows real distribution from backend
- **FactCheckReport**: Displays comprehensive fact check analysis
- **BiasCheckReport**: Shows bias analysis from multiple sources
- **ForensicAnalysis**: Displays source tracking metrics

## Troubleshooting

### Backend Not Responding
```bash
# Check if all services are running
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### CORS Errors
- Ensure `CORSMiddleware` is properly configured in `manager/server.py`
- Check that frontend is running on port 5173

### TypeScript Errors
```bash
# Install missing dependencies
cd frontend/frontend-magic-pattern
npm install
```

### Port Conflicts
If ports are in use:
```bash
# Kill processes on ports
netstat -ano | findstr "8000"  # Find PID
taskkill /F /PID <PID>         # Kill process
```

## Git Branch
All changes are in the `feature/non-news-query-validation` branch.

To merge into master:
```bash
git checkout master
git merge feature/non-news-query-validation
```

## Next Steps

### Potential Enhancements:
1. Add loading skeletons for better UX
2. Implement search history
3. Add export functionality (PDF/CSV)
4. Add charts for trends visualization
5. Implement user authentication
6. Add favorite/bookmark feature
7. Real-time updates with WebSockets
8. Mobile responsive improvements

## Support
For issues or questions, check:
- Backend logs in manager/sub_agents/*/server.py
- Frontend console (F12 in browser)
- Network tab for API call details
