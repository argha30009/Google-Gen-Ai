"""
Fact-Check Agent Server
FastAPI server for the fact-check microservice
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from agent import create_agent

app = FastAPI(
    title="Fact-Check Agent",
    description="Analyzes headlines for contradictions and controversial claims",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = create_agent()


class FactCheckRequest(BaseModel):
    """Request model for fact-check analysis."""
    headlines: List[str]
    query: str = None  # Optional original user query for context


class FactCheckResponse(BaseModel):
    """Response model for fact-check analysis."""
    analysis: str
    factcheck_summary: Dict[str, Any] = {}
    formatted_markdown: str = ""
    headlines_analyzed: int
    status: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fact-check-agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "factcheck_agent"}


@app.post("/run", response_model=FactCheckResponse)
async def run_factcheck(request: FactCheckRequest) -> Dict[str, Any]:
    """
    Analyze headlines for contradictions and controversial claims.
    
    Args:
        request: FactCheckRequest with headlines list
        
    Returns:
        FactCheckResponse with analysis results
    """
    try:
        if not request.headlines:
            raise HTTPException(status_code=400, detail="No headlines provided")
        
        result = agent.analyze(request.headlines, query=request.query)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )
