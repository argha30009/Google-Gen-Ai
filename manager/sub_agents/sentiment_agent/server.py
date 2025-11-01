"""
FastAPI server for sentiment_agent microservice.
Wraps the Google ADK sentiment agent as a REST API.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
import google.genai.types as types
import uuid

# Load environment variables from .env file if it exists
from pathlib import Path
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Verify API key is set
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

from agent import sentiment_agent

# Initialize the runner
runner = Runner(
    app_name="sentiment_agent_app",
    agent=sentiment_agent,
    session_service=InMemorySessionService()
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Agent Service",
    description="Microservice for analyzing sentiment of news headlines",
    version="1.0.0"
)


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    headlines: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "headlines": [
                    "OpenAI announces breakthrough in AI research",
                    "Tech stocks decline amid market uncertainty",
                    "New regulations proposed for AI industry"
                ]
            }
        }


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis results"""
    sentiment_summary: Dict[str, Any]
    per_item: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentiment_summary": {
                    "overall": "mixed",
                    "positive_count": 1,
                    "negative_count": 1,
                    "neutral_count": 1
                },
                "per_item": [
                    {
                        "headline": "OpenAI announces breakthrough in AI research",
                        "sentiment": "positive",
                        "score": 0.8
                    }
                ]
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "sentiment_agent"}


@app.post("/run", response_model=SentimentResponse)
async def run_sentiment_analysis(request: SentimentRequest):
    """
    Execute sentiment agent to analyze headlines.
    
    Args:
        request: SentimentRequest containing list of headlines
        
    Returns:
        SentimentResponse with sentiment summary and per-item analysis
    """
    try:
        logger.info(f"Received sentiment analysis request for {len(request.headlines)} headlines")
        
        if not request.headlines:
            raise HTTPException(
                status_code=400,
                detail="Headlines list cannot be empty"
            )
        
        # Generate unique IDs for this request
        user_id = "api_user"
        session_id = str(uuid.uuid4())
        
        # Create session first
        await runner.session_service.create_session(
            user_id=user_id,
            session_id=session_id,
            app_name="sentiment_agent_app"
        )
        
        # Format the input as a prompt for the agent
        headlines_text = "\n".join([f"- {h}" for h in request.headlines])
        prompt = f"Analyze the sentiment of these headlines:\n{headlines_text}"
        
        # Execute the sentiment agent using Runner (async)
        full_response = ""
        
        # Create proper Content message
        message = types.Content(
            role='user',
            parts=[types.Part(text=prompt)]
        )
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            # Collect agent response from events
            if hasattr(event, 'content') and event.content:
                full_response += str(event.content)
            elif hasattr(event, 'text') and event.text:
                full_response += str(event.text)
        
        # Parse the agent's response
        per_item = []
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Simple sentiment detection from response
        response_lower = full_response.lower()
        
        for headline in request.headlines:
            # Basic sentiment detection
            sentiment = "neutral"
            if "positive" in response_lower or "good" in response_lower or "optimistic" in response_lower:
                sentiment = "positive"
                sentiment_counts["positive"] += 1
            elif "negative" in response_lower or "bad" in response_lower or "pessimistic" in response_lower:
                sentiment = "negative"
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1
            
            per_item.append({
                "headline": headline,
                "sentiment": sentiment,
                "analysis": full_response[:200] if full_response else "Analysis completed"
            })
        
        # Determine overall sentiment
        total = len(request.headlines)
        if sentiment_counts["positive"] > total / 2:
            overall = "positive"
        elif sentiment_counts["negative"] > total / 2:
            overall = "negative"
        else:
            overall = "mixed"
        
        response = {
            "sentiment_summary": {
                "overall": overall,
                "positive_count": sentiment_counts["positive"],
                "negative_count": sentiment_counts["negative"],
                "neutral_count": sentiment_counts["neutral"],
                "total_analyzed": total,
                "full_analysis": full_response if full_response else "No analysis available"
            },
            "per_item": per_item
        }
        
        logger.info(f"Sentiment analysis completed for {len(request.headlines)} headlines")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing sentiment analysis request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing sentiment agent: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
