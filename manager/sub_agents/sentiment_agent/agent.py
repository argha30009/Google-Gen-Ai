from google.adk.agents import Agent
from typing import List, Dict, Any
import json
from textblob import TextBlob

def analyze_sentiment_tool(headlines: str) -> str:
    """
    Analyze sentiment of news headlines using TextBlob.
    
    Args:
        headlines: JSON string containing list of headlines
        
    Returns:
        JSON string with sentiment analysis results
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f">>> analyze_sentiment_tool CALLED")
    
    try:
        # Parse headlines from JSON string
        if isinstance(headlines, str):
            headlines_list = json.loads(headlines)
        else:
            headlines_list = headlines
            
        if not isinstance(headlines_list, list):
            headlines_list = [str(headlines_list)]
        
        per_headline = []
        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        
        for headline in headlines_list:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(str(headline))
            polarity = blob.sentiment.polarity
            
            # Classify based on polarity
            if polarity > 0.05:
                sentiment = "positive"
                distribution["positive"] += 1
            elif polarity < -0.05:
                sentiment = "negative"
                distribution["negative"] += 1
            else:
                sentiment = "neutral"
                distribution["neutral"] += 1
            
            per_headline.append({
                "headline": headline,
                "sentiment": sentiment,
                "score": round(polarity, 3)
            })
        
        result = {
            "per_headline": per_headline,
            "distribution": distribution,
            "total": len(headlines_list)
        }
        
        logger.info(f">>> analyze_sentiment_tool SUCCESS: {distribution}")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f">>> analyze_sentiment_tool ERROR: {str(e)}")
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })

sentiment_agent = Agent(
    name="sentiment_agent",
    model="gemini-2.5-flash",
    description="Performs structured sentiment analysis on news headlines and summarizes tone distribution.",
    tools=[analyze_sentiment_tool],
    instruction="""
You are a structured Sentiment Analysis Agent.

### Task:
Given a list of news headlines, use the `analyze_sentiment_tool` to get sentiment scores, then create a complete analysis.

### Steps:
1. Call `analyze_sentiment_tool` with the headlines as a JSON array string
2. The tool returns per_headline analysis with sentiment labels and scores
3. Based on the distribution, write a brief 1-2 sentence overall_summary
4. Return the complete result as JSON

### Output Format (strict JSON):
{
  "per_headline": [
    {"headline": "<text>", "sentiment": "positive|neutral|negative", "score": float}
  ],
  "overall_summary": "<1-2 sentence summary>",
  "distribution": {"positive": int, "neutral": int, "negative": int}
}

### Rules:
- MUST call analyze_sentiment_tool first
- Create natural summary based on distribution
- Return strictly valid JSON - no Markdown
"""
)
