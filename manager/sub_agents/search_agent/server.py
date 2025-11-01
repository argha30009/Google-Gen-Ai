"""
FastAPI server for search_agent microservice.
Wraps the Google ADK search agent as a REST API.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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

from agent import search_agent

# Initialize the runner
runner = Runner(
    app_name="search_agent_app",
    agent=search_agent,
    session_service=InMemorySessionService()
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Search Agent Service",
    description="Microservice for fetching news headlines using Google Search",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    """Request model for search queries"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "OpenAI latest news"
            }
        }


class SearchResponse(BaseModel):
    """Response model for search results"""
    headlines: List[Dict[str, Any]]
    meta: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "headlines": [
                    {
                        "title": "OpenAI announces new model",
                        "source": "TechCrunch",
                        "date": "2024-01-15"
                    }
                ],
                "meta": {
                    "query": "OpenAI latest news",
                    "count": 1
                }
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "search_agent"}


@app.post("/run", response_model=SearchResponse)
async def run_search(request: SearchRequest):
    """
    Execute search agent to fetch news headlines.
    
    Args:
        request: SearchRequest containing the search query
        
    Returns:
        SearchResponse with headlines and metadata
    """
    try:
        logger.info(f"Received search request for query: {request.query}")
        
        # Generate unique IDs for this request
        user_id = "api_user"
        session_id = str(uuid.uuid4())
        
        # Create session first
        await runner.session_service.create_session(
            user_id=user_id,
            session_id=session_id,
            app_name="search_agent_app"
        )
        
        # Execute the search agent using Runner (async)
        headlines = []
        full_response = ""
        
        # Create proper Content message
        message = types.Content(
            role='user',
            parts=[types.Part(text=request.query)]
        )
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            # Collect agent response from events
            logger.info(f"Event received: {type(event)}")
            
            if hasattr(event, 'content') and event.content:
                content = event.content
                logger.info(f"Event content: {content}")
                
                # Extract text from content parts
                if hasattr(content, 'parts') and content.parts:
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_response += part.text
                else:
                    full_response += str(content)
        
        # Structure the response
        if full_response:
            # Split response into individual headlines if possible
            lines = [line.strip() for line in full_response.split('\n') if line.strip()]
            
            if len(lines) > 1:
                # Multiple headlines found
                for line in lines[:10]:  # Limit to 10 headlines
                    if line and not line.startswith('#'):
                        headlines.append({
                            "title": line,
                            "query": request.query
                        })
            else:
                # Single response
                headlines.append({
                    "title": full_response.strip(),
                    "raw_response": full_response,
                    "query": request.query
                })
        
        if not headlines:
            headlines.append({
                "title": f"No results found for: {request.query}",
                "query": request.query
            })
        
        response = {
            "headlines": headlines,
            "meta": {
                "query": request.query,
                "count": len(headlines),
                "status": "success"
            }
        }
        
        logger.info(f"Search completed successfully for query: {request.query}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing search agent: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
