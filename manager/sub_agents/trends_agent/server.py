"""
FastAPI server for Google Trends Agent.
"""
import os
import logging
import base64
import json
import uuid
from io import BytesIO
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pytrends.request import TrendReq
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

# Load environment variables from .env file if it exists
from pathlib import Path
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

from agent import google_trends_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Note: genai configuration is handled by ADK Runner

# Create FastAPI app
app = FastAPI(
    title="Google Trends Agent Service",
    description="Analyzes Google Trends data for keywords",
    version="1.0.0"
)

# Initialize ADK Runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="trends_agent_app",
    agent=google_trends_agent,
    session_service=session_service
)


class TrendsRequest(BaseModel):
    """Request model for trends analysis."""
    keyword: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "artificial intelligence"
            }
        }


class TrendsResponse(BaseModel):
    """Response model for trends analysis."""
    keyword: str
    trend_analysis: Dict[str, Any]
    raw_response: str
    plot_data: Dict[str, Any]  # Timeline data and plot image


def fetch_trends_data(keyword: str, timeframe: str = 'today 12-m') -> Dict[str, Any]:
    """
    Fetch Google Trends data and generate a plot.
    
    Args:
        keyword: Keyword to analyze
        timeframe: Time period (default: last 12 months)
        
    Returns:
        Dict with timeline data and base64-encoded plot image
    """
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Build payload
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
        
        # Get interest over time
        interest_df = pytrends.interest_over_time()
        
        if interest_df.empty:
            return {
                "error": "No data available for this keyword",
                "timeline": [],
                "plot_base64": None
            }
        
        # Remove 'isPartial' column if it exists
        if 'isPartial' in interest_df.columns:
            interest_df = interest_df.drop(columns=['isPartial'])
        
        # Extract timeline data
        timeline_data = []
        for date, value in interest_df[keyword].items():
            timeline_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "value": int(value)
            })
        
        # Generate plot
        fig = plt.figure(figsize=(12, 6))
        plt.plot(interest_df.index, interest_df[keyword], linewidth=2, color='#667eea')
        plt.fill_between(interest_df.index, interest_df[keyword], alpha=0.3, color='#667eea')
        plt.title(f'Google Trends: "{keyword}" - Search Interest Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Search Interest (Relative)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert plot to base64
        buffer = BytesIO()
        try:
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_data = buffer.read()
            plot_base64 = base64.b64encode(image_data).decode('utf-8')
            logger.info(f"Plot generated successfully, base64 length: {len(plot_base64)}")
        finally:
            buffer.close()
            plt.close(fig)
        
        # Calculate statistics
        max_value = int(interest_df[keyword].max())
        min_value = int(interest_df[keyword].min())
        avg_value = int(interest_df[keyword].mean())
        current_value = int(interest_df[keyword].iloc[-1])
        
        # Determine trend direction
        recent_avg = interest_df[keyword].iloc[-4:].mean()  # Last 4 data points
        older_avg = interest_df[keyword].iloc[-8:-4].mean()  # Previous 4 data points
        
        if recent_avg > older_avg * 1.1:
            trend_direction = "rising"
        elif recent_avg < older_avg * 0.9:
            trend_direction = "falling"
        else:
            trend_direction = "stable"
        
        return {
            "timeline": timeline_data,
            "plot_base64": plot_base64,
            "statistics": {
                "max": max_value,
                "min": min_value,
                "average": avg_value,
                "current": current_value,
                "trend_direction": trend_direction
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching trends data: {str(e)}")
        return {
            "error": str(e),
            "timeline": [],
            "plot_base64": None
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "trends_agent"}


@app.post("/run", response_model=TrendsResponse)
async def analyze_trends(request: TrendsRequest) -> TrendsResponse:
    """
    Fetch Google Trends data using ADK Runner.
    
    Args:
        request: TrendsRequest with keyword
        
    Returns:
        TrendsResponse with trend plot and statistics
    """
    try:
        logger.info(f"Fetching Google Trends data for keyword: {request.keyword}")
        
        # Fetch plot data (keep existing visualization)
        plot_data = fetch_trends_data(request.keyword)
        
        # Use ADK Runner for analysis
        try:
            # Create session
            user_id = "default_user"
            session_id = str(uuid.uuid4())
            await runner.session_service.create_session(
                app_name="trends_agent_app",
                user_id=user_id,
                session_id=session_id
            )
            
            # Create message with proper Content object
            message_content = types.Content(
                role="user",
                parts=[types.Part(text=f"Analyze Google Trends for keyword: {request.keyword}")]
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
            
            # Extract analysis from ADK response
            keyword = parsed_result.get('keyword', request.keyword)
            trend_direction = parsed_result.get('trend_direction', 'unknown')
            summary = parsed_result.get('summary', '')
            statistics = parsed_result.get('statistics', {})
            
            trend_analysis = {
                "keyword": keyword,
                "analysis": summary,
                "status": "completed",
                "trend_direction": trend_direction,
                "statistics": statistics
            }
            
        except Exception as adk_error:
            logger.error(f"ADK Runner error: {str(adk_error)}", exc_info=True)
            # Fallback to basic analysis
            stats = plot_data.get("statistics", {})
            trend_direction = stats.get("trend_direction", "unknown")
            trend_analysis = {
                "keyword": request.keyword,
                "analysis": f"Trend direction: {trend_direction}. ADK error: {str(adk_error)}",
                "status": "fallback",
                "trend_direction": trend_direction,
                "statistics": stats
            }
        
        logger.info(f"Trends analysis completed for: {request.keyword}")
        
        return TrendsResponse(
            keyword=request.keyword,
            trend_analysis=trend_analysis,
            raw_response=trend_analysis.get("analysis", ""),
            plot_data=plot_data
        )
        
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Trends fetch failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
