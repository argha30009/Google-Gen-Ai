"""
Google Trends Agent using Google ADK.
Fetches and visualizes Google Trends data for a given keyword.
"""
from google.adk.agents import Agent
import json
from pytrends.request import TrendReq
import pandas as pd

def google_trends_tool(keyword: str) -> str:
    """
    Fetch Google Trends data for a keyword using pytrends.
    
    Args:
        keyword: The keyword to search trends for
        
    Returns:
        JSON string with trends data
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f">>> google_trends_tool CALLED with keyword: {keyword}")
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Build payload for interest over time
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
        
        # Get interest over time data
        interest_df = pytrends.interest_over_time()
        
        if interest_df.empty:
            return json.dumps({
                "error": "No data available for this keyword",
                "keyword": keyword,
                "status": "no_data"
            })
        
        # Remove 'isPartial' column if it exists
        if 'isPartial' in interest_df.columns:
            interest_df = interest_df.drop(columns=['isPartial'])
        
        # Get trend statistics
        values = interest_df[keyword].tolist()
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        current_val = values[-1]
        
        # Determine trend direction (compare last 3 months vs previous 3 months)
        if len(values) >= 6:
            recent_avg = sum(values[-3:]) / 3
            previous_avg = sum(values[-6:-3]) / 3
            if recent_avg > previous_avg * 1.1:
                trend_direction = "rising"
            elif recent_avg < previous_avg * 0.9:
                trend_direction = "falling"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"
        
        # Find peak date
        peak_idx = values.index(max_val)
        peak_date = str(interest_df.index[peak_idx].date())
        
        result = {
            "keyword": keyword,
            "status": "success",
            "trend_direction": trend_direction,
            "statistics": {
                "current": int(current_val),
                "max": int(max_val),
                "min": int(min_val),
                "average": round(avg_val, 2),
                "peak_date": peak_date
            },
            "data_points": len(values),
            "sample_values": values[-12:]  # Last 12 data points
        }
        
        logger.info(f">>> google_trends_tool SUCCESS: trend={trend_direction}, current={current_val}")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f">>> google_trends_tool ERROR: {str(e)}")
        return json.dumps({
            "error": str(e),
            "keyword": keyword,
            "status": "failed"
        })

google_trends_agent = Agent(
    name="google_trends_agent",
    model="gemini-2.5-flash",
    description="Fetches and visualizes Google Trends data for a keyword.",
    tools=[google_trends_tool],
    instruction="""
You are a Google Trends Analysis Agent.

### Task:
Given a keyword, use the `google_trends_tool` to fetch search interest data, then provide a detailed analysis.

### Steps:
1. Call `google_trends_tool` with the keyword
2. The tool returns trend statistics including direction, peak dates, and values
3. Analyze the data and write a comprehensive summary
4. Return result as JSON

### Output Format (strict JSON):
{
  "keyword": "<the keyword>",
  "trend_direction": "rising|falling|stable",
  "summary": "<detailed 3-4 sentence analysis>",
  "statistics": {
    "current": int,
    "max": int,
    "average": float,
    "peak_date": "YYYY-MM-DD"
  }
}

### Rules:
- MUST call google_trends_tool first to get data
- Provide insightful analysis of the trend pattern
- Mention specific statistics (peak date, current vs average, etc.)
- Return strictly valid JSON - no Markdown
"""
)
