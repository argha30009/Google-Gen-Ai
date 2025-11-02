"""
FastAPI server for sentiment_agent microservice.
Wraps the Google ADK sentiment agent as a REST API.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import json
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
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
    Execute sentiment agent using ADK Runner to analyze headlines.
    
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
        
        # Use ADK Runner pattern
        try:
            # Create session
            user_id = "default_user"
            session_id = str(uuid.uuid4())
            await runner.session_service.create_session(
                app_name="sentiment_agent_app",
                user_id=user_id,
                session_id=session_id
            )
            
            # Create message with proper Content object
            headlines_json = json.dumps(request.headlines)
            message_content = types.Content(
                role="user",
                parts=[types.Part(text=f"Analyze sentiment for these headlines: {headlines_json}")]
            )
            
            # Call ADK Runner
            result_generator = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message_content
            )
            
            # Collect results from async generator
            result = None
            async for chunk in result_generator:
                result = chunk
            
            # Extract text from Event->Content->Parts
            result_text = ""
            if result is None:
                raise ValueError("No result received from ADK Runner")
            
            content_obj = result.content if hasattr(result, 'content') else result
            
            if hasattr(content_obj, 'parts'):
                for part in content_obj.parts:
                    if hasattr(part, 'text'):
                        result_text += part.text
            elif hasattr(content_obj, 'text'):
                result_text = content_obj.text
            else:
                result_text = str(content_obj)
            
            if not result_text or not isinstance(result_text, str):
                raise ValueError(f"No valid text extracted. Got type: {type(result_text)}")
            
            # Strip markdown wrappers
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Parse JSON response
            parsed_result = json.loads(result_text)
            
            # Extract data from ADK response
            per_headline = parsed_result.get('per_headline', [])
            distribution = parsed_result.get('distribution', {})
            overall_summary = parsed_result.get('overall_summary', '')
            
            # Determine overall sentiment
            total = len(request.headlines)
            if distribution.get('positive', 0) > total / 2:
                overall = "positive"
            elif distribution.get('negative', 0) > total / 2:
                overall = "negative"
            else:
                overall = "mixed"
            
            response = {
                "sentiment_summary": {
                    "overall": overall,
                    "positive_count": distribution.get('positive', 0),
                    "negative_count": distribution.get('negative', 0),
                    "neutral_count": distribution.get('neutral', 0),
                    "total_analyzed": total,
                    "full_analysis": overall_summary
                },
                "per_item": per_headline
            }
            
            logger.info(f"Sentiment analysis completed for {len(request.headlines)} headlines")
            return response
            
        except Exception as adk_error:
            logger.error(f"ADK Runner error: {str(adk_error)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"ADK Runner error: {str(adk_error)}"
            )
        
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
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
