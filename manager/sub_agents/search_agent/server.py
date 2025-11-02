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
    Execute search agent using ADK Runner with proper message format.
    
    Args:
        request: SearchRequest containing the search query
        
    Returns:
        SearchResponse with headlines and metadata
    """
    try:
        logger.info(f"Received search request for query: {request.query}")
        
        # Create a new session for this request
        user_id = "default_user"
        session_id = str(uuid.uuid4())
        
        # Create the session before using it (app_name is required)
        await runner.session_service.create_session(
            app_name="search_agent_app",
            user_id=user_id,
            session_id=session_id
        )
        
        # Fix for "'str' object has no attribute 'role'" error:
        # Create proper Content object with role and parts
        message_content = types.Content(
            role="user",
            parts=[types.Part(text=f"Search for recent news headlines about: {request.query}")]
        )
        
        # Use ADK Runner with properly formatted message
        try:
            # Call ADK Runner with correct parameters (user_id, session_id, new_message as Content object)
            # ADK Runner returns an async generator, not a direct result
            result_generator = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message_content  # Pass Content object, not string
            )
            
            # Collect results from the async generator
            result = None
            async for chunk in result_generator:
                result = chunk  # Get the final result
                # If you want to process streaming chunks, handle them here
            
            # Extract response text from ADK result
            # ADK Runner returns an Event object containing a Content object
            result_text = ""
            if result is None:
                raise ValueError("No result received from ADK Runner")
            
            logger.info(f"Result type: {type(result)}")
            
            # First, get the Content object from the Event
            content_obj = None
            if hasattr(result, 'content'):
                content_obj = result.content
            elif hasattr(result, 'parts'):
                content_obj = result  # Already a Content object
            else:
                content_obj = result
            
            logger.info(f"Content object type: {type(content_obj)}, has parts: {hasattr(content_obj, 'parts')}")
            
            # Now extract text from the Content object's parts
            if hasattr(content_obj, 'parts'):
                logger.info(f"Extracting text from {len(content_obj.parts)} parts")
                for idx, part in enumerate(content_obj.parts):
                    if hasattr(part, 'text'):
                        result_text += part.text
                    else:
                        logger.warning(f"Part {idx} has no text attribute: {type(part)}")
            elif hasattr(content_obj, 'text'):
                result_text = content_obj.text
            elif isinstance(content_obj, str):
                result_text = content_obj
            elif isinstance(content_obj, dict):
                result_text = content_obj.get('text', str(content_obj))
            else:
                result_text = str(content_obj)
            
            logger.info(f"Extracted text type: {type(result_text)}, length: {len(result_text) if isinstance(result_text, str) else 0}")
            logger.info(f"Extracted text content preview: {result_text[:500]}")  # Log first 500 chars
            
            if not result_text or not isinstance(result_text, str):
                raise ValueError(f"No valid text string extracted. Got type: {type(result_text)}")
            
            # Strip markdown code block wrappers if present
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]  # Remove ```json
            if result_text.startswith('```'):
                result_text = result_text[3:]  # Remove ```
            if result_text.endswith('```'):
                result_text = result_text[:-3]  # Remove trailing ```
            result_text = result_text.strip()
            
            # Try to parse as JSON first (if agent returned structured output)
            import json
            try:
                parsed_result = json.loads(result_text) if isinstance(result_text, str) else result_text
                
                # Check if it's already in our expected format
                if isinstance(parsed_result, dict) and 'search_results' in parsed_result:
                    headlines = parsed_result['search_results'].get('headlines', [])
                    meta = parsed_result['search_results'].get('meta', {
                        "query": request.query,
                        "count": len(headlines),
                        "status": "success"
                    })
                    response_data = {
                        "headlines": headlines,
                        "meta": meta
                    }
                    logger.info(f"Search completed successfully with {len(headlines)} results")
                    return response_data
            except (json.JSONDecodeError, AttributeError, KeyError) as parse_error:
                logger.warning(f"Could not parse as JSON, falling back to text parsing: {parse_error}")
            
            # Fallback: parse text response line by line
            headlines = []
            lines = [line.strip().lstrip('-').lstrip('*').strip() for line in result_text.split('\n') if line.strip()]
            
            # Filter out introductory text
            intro_keywords = [
                'here are', 'here is', 'following', 'recent news', 'headlines', 
                'search results', 'based on', 'regarding', 'about', 'related to'
            ]
            
            for line in lines[:25]:
                if line and len(line) > 10:
                    line_lower = line.lower()
                    is_intro = any(keyword in line_lower for keyword in intro_keywords)
                    
                    if is_intro and (line.endswith(':') or len(line.split()) < 4):
                        continue
                    
                    headlines.append({
                        "title": line,
                        "query": request.query
                    })
                    
                    if len(headlines) >= 10:
                        break
            
            if not headlines:
                headlines.append({
                    "title": f"Search query: {request.query}",
                    "query": request.query,
                    "note": "No structured results, returning query confirmation"
                })
            
            response_data = {
                "headlines": headlines,
                "meta": {
                    "query": request.query,
                    "count": len(headlines),
                    "status": "success"
                }
            }
            
            logger.info(f"Search completed successfully with {len(headlines)} results")
            return response_data
            
        except Exception as search_error:
            logger.error(f"ADK Runner search error: {str(search_error)}", exc_info=True)
            # Return fallback response
            return {
                "headlines": [{
                    "title": f"Search completed for: {request.query}",
                    "query": request.query,
                    "note": f"ADK error: {str(search_error)}"
                }],
                "meta": {
                    "query": request.query,
                    "count": 1,
                    "status": "error"
                }
            }
        
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing search agent: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
