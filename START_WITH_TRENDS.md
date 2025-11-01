# 🚀 Quick Start: News Analysis with Google Trends

## 📦 Install Dependencies

First, install the required packages for the Trends Agent:

```bash
cd /Users/amansiddharth/Downloads/gh
source venv/bin/activate
pip install pytrends matplotlib pandas
```

## 🎯 Start All Services

### Terminal 1 - Search Agent (Port 8001)
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/search_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2 - Sentiment Agent (Port 8002)
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/sentiment_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

### Terminal 3 - Trends Agent (Port 8003) ⭐ NEW!
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager/sub_agents/trends_agent
../../../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8003 --reload
```

### Terminal 4 - Manager Web UI (Port 8000)
```bash
export GOOGLE_API_KEY="AIzaSyCTy7qN45nojQFv-2QehIIcmTvquGnncJU"
cd /Users/amansiddharth/Downloads/gh/manager
../venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Access the Application

Open your browser and go to:
### **http://localhost:8000**

## 🎨 What You'll See

The web interface now includes a **new Trends Analysis section** with:

### 📊 Statistics Cards
- **Current Interest**: Latest search interest value
- **Peak Interest**: Highest point in the timeline
- **Average Interest**: Mean value over time
- **Trend Direction**: Rising, Falling, or Stable

### 📈 Interactive Plot
- Beautiful line chart showing search interest over time (last 12 months)
- Timeline on X-axis, relative interest (0-100) on Y-axis
- Gradient fill for visual appeal

### 🤖 AI Analysis
- Comprehensive trend interpretation by Gemini AI
- Pattern identification
- Context and insights

## 🧪 Test It Out

Try searching for:
- **"Tesla"** - See automotive/tech trends
- **"ChatGPT"** - AI adoption trends
- **"Climate Change"** - Environmental awareness
- **"Olympics"** - Seasonal event patterns
- **"Bitcoin"** - Cryptocurrency interest

## 📊 Output Sections

Your complete analysis now includes:

1. **📊 Sentiment Analysis**
   - Total analyzed, Positive, Neutral, Negative counts
   - Per-headline sentiment breakdown

2. **📰 Headlines**
   - Numbered list of all news headlines found

3. **✅ Fact Check Report**
   - Verifiable facts and discrepancies

4. **🔍 Bias Check Report**
   - Sentiment distribution and bias analysis

5. **🕵️ Forensic Analysis**
   - Source tracking and timeline

6. **📈 Google Trends Analysis** ⭐ NEW!
   - Statistics (Current, Peak, Average, Direction)
   - Visual plot with timeline
   - AI-generated insights

7. **📋 Full Response**
   - Complete JSON for developers

## 🔧 Technical Details

### Trends Data
- **Source**: Google Trends (via pytrends library)
- **Timeframe**: Last 12 months
- **Update Frequency**: Real-time on each query
- **Plot Format**: PNG image (base64 encoded)

### Performance
- **Trends Analysis Time**: ~3-5 seconds
- **Plot Generation**: ~1 second
- **Total Pipeline**: ~10-15 seconds (with all agents)

### Error Handling
- If Trends service fails, the rest of the pipeline continues
- Graceful degradation - you still get news and sentiment analysis
- Detailed error logging for debugging

## 🎯 API Usage

### Direct Trends API Call
```bash
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence"}'
```

### Full Pipeline via Manager
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"query": "Tesla"}'
```

## 📸 What the Plot Shows

The trends plot displays:
- **X-Axis**: Timeline (dates over last 12 months)
- **Y-Axis**: Relative search interest (0-100 scale)
- **Line**: Actual trend data
- **Shaded Area**: Visual emphasis of the trend
- **Grid**: Easy value reading

### Interpreting Values
- **100**: Peak popularity for the term
- **50**: Half of peak popularity
- **0**: Not enough data for that period

## 🔄 How It Works

1. User enters a query (e.g., "Tesla")
2. Manager calls all three agents in parallel:
   - Search Agent → Fetches news headlines
   - Sentiment Agent → Analyzes sentiment
   - Trends Agent → Fetches Google Trends data
3. Trends Agent:
   - Queries Google Trends API (pytrends)
   - Generates matplotlib plot
   - Converts plot to base64 image
   - Calculates statistics
   - Gets AI analysis from Gemini
4. Manager combines all results
5. Web UI displays everything beautifully

## 🎉 Benefits

✅ **Visual Insights**: See search interest trends at a glance
✅ **Context**: Understand if news matches public interest
✅ **Patterns**: Identify seasonal or event-driven trends
✅ **Comparison**: News sentiment vs. search popularity
✅ **Historical Data**: 12 months of trend history

## 🐛 Troubleshooting

### Trends Agent Won't Start
```bash
# Install missing dependencies
pip install pytrends matplotlib pandas
```

### No Plot Showing
- Check if trends_analysis exists in response
- Verify pytrends can access Google Trends
- Check browser console for errors

### Plot Generation Slow
- Normal for first request (matplotlib initialization)
- Subsequent requests should be faster
- Consider adding caching for popular queries

## 🚀 Next Steps

1. **Add Caching**: Cache trends data for 1 hour
2. **Multiple Keywords**: Compare trends for multiple terms
3. **Custom Timeframes**: Allow user to select time period
4. **Download Plot**: Add button to download PNG
5. **Interactive Charts**: Use Chart.js for interactive plots

## 📝 Summary

You now have a complete news analysis system with:
- ✅ News search
- ✅ Sentiment analysis
- ✅ Comprehensive reports
- ✅ **Google Trends visualization** ⭐

Enjoy exploring news with trend context! 🎊
