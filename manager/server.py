"""
FastAPI web server for the Manager Agent with interactive UI.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import logging
from agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="News Search & Sentiment Manager",
    description="Orchestrates news search and sentiment analysis",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://storage.googleapis.com",
        "http://news-analysis-frontend-1762108971.storage.googleapis.com",
        "http://clipse-app.storage.googleapis.com",
        "*"  # Allow all origins for production (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "OpenAI latest news"
            }
        }


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the interactive web UI."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>News Search & Sentiment Analysis</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .search-card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
            }
            
            .search-form {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .search-input {
                flex: 1;
                padding: 15px 20px;
                font-size: 1rem;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .search-input:focus {
                border-color: #667eea;
            }
            
            .search-button {
                padding: 15px 40px;
                font-size: 1rem;
                font-weight: 600;
                color: white;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .search-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .search-button:active {
                transform: translateY(0);
            }
            
            .search-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                display: none;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .results {
                display: none;
            }
            
            .result-section {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .result-section h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.5rem;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            
            .result-section h3 {
                color: #555;
                margin: 15px 0 10px;
                font-size: 1.2rem;
            }
            
            .headline-item {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            
            .sentiment-badge {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-left: 10px;
            }
            
            .sentiment-positive {
                background: #d4edda;
                color: #155724;
            }
            
            .sentiment-negative {
                background: #f8d7da;
                color: #721c24;
            }
            
            .sentiment-neutral {
                background: #d1ecf1;
                color: #0c5460;
            }
            
            .sentiment-mixed {
                background: #fff3cd;
                color: #856404;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #dc3545;
                display: none;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                color: #667eea;
            }
            
            .stat-label {
                color: #666;
                font-size: 0.9rem;
                margin-top: 5px;
            }
            
            pre {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 News Search & Sentiment Analysis</h1>
                <p>Powered by Google ADK Microservices</p>
            </div>
            
            <div class="search-card">
                <form id="searchForm" class="search-form">
                    <input 
                        type="text" 
                        id="queryInput" 
                        class="search-input" 
                        placeholder="Enter a topic to search for news (e.g., OpenAI, climate change, Tesla)"
                        required
                    >
                    <button type="submit" class="search-button" id="searchButton">
                        Search News
                    </button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Searching news and analyzing sentiment...</p>
                </div>
                
                <div class="error" id="error"></div>
                
                <div class="results" id="results">
                    <div class="result-section">
                        <h2>📊 Overview</h2>
                        <div id="overview"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>😊 Sentiment Analysis</h2>
                        <div class="stats" id="sentimentStats"></div>
                        <div id="sentimentDetails"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>📰 Headlines</h2>
                        <div id="headlines"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>✅ Fact Check Report</h2>
                        <div id="factCheck" style="white-space: pre-wrap; line-height: 1.6;"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>🔍 Bias Check Report</h2>
                        <div id="biasCheck" style="white-space: pre-wrap; line-height: 1.6;"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>🕵️ Forensic Analysis</h2>
                        <div id="forensicAnalysis" style="white-space: pre-wrap; line-height: 1.6;"></div>
                    </div>
                    
                    <div class="result-section" id="trendsSection" style="display: none;">
                        <h2>📈 Google Trends Analysis</h2>
                        <div id="trendsStats" class="stats" style="margin-bottom: 20px;"></div>
                        <div id="trendsPlot" style="text-align: center; margin: 20px 0;"></div>
                        <div id="trendsAnalysis" style="white-space: pre-wrap; line-height: 1.6; margin-top: 20px;"></div>
                    </div>
                    
                    <div class="result-section">
                        <h2>📋 Full Response</h2>
                        <pre id="fullResponse"></pre>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const form = document.getElementById('searchForm');
            const queryInput = document.getElementById('queryInput');
            const searchButton = document.getElementById('searchButton');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const results = document.getElementById('results');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const query = queryInput.value.trim();
                if (!query) return;
                
                // Reset UI
                loading.style.display = 'block';
                error.style.display = 'none';
                results.style.display = 'none';
                searchButton.disabled = true;
                
                // Clear previous trends data to prevent caching
                document.getElementById('trendsSection').style.display = 'none';
                document.getElementById('trendsStats').innerHTML = '';
                document.getElementById('trendsPlot').innerHTML = '';
                document.getElementById('trendsAnalysis').innerHTML = '';
                
                try {
                    const response = await fetch('/run', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Search failed');
                    }
                    
                    displayResults(data);
                    
                } catch (err) {
                    error.textContent = `Error: ${err.message}`;
                    error.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                    searchButton.disabled = false;
                }
            });
            
            function displayResults(data) {
                // Overview
                const summary = data.summary || {};
                document.getElementById('overview').innerHTML = `
                    <p><strong>Query:</strong> ${data.query}</p>
                    <p><strong>Summary:</strong> ${summary.overview || 'N/A'}</p>
                    <p><strong>Overall Sentiment:</strong> 
                        <span class="sentiment-badge sentiment-${summary.sentiment_overview || 'neutral'}">
                            ${(summary.sentiment_overview || 'unknown').toUpperCase()}
                        </span>
                    </p>
                `;
                
                // Sentiment Stats
                const sentimentSummary = data.sentiment_analysis?.sentiment_summary || {};
                document.getElementById('sentimentStats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${sentimentSummary.total_analyzed || 0}</div>
                        <div class="stat-label">Total Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #28a745;">${sentimentSummary.positive_count || 0}</div>
                        <div class="stat-label">Positive</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #6c757d;">${sentimentSummary.neutral_count || 0}</div>
                        <div class="stat-label">Neutral</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #dc3545;">${sentimentSummary.negative_count || 0}</div>
                        <div class="stat-label">Negative</div>
                    </div>
                `;
                
                // Sentiment Details
                const perItem = data.sentiment_analysis?.per_item || [];
                let sentimentHtml = '<h3>Per-Headline Analysis</h3>';
                perItem.forEach((item, idx) => {
                    const analysisText = item.analysis ? 
                        (typeof item.analysis === 'string' ? item.analysis.substring(0, 200) : '') : '';
                    sentimentHtml += `
                        <div class="headline-item">
                            <div style="display: flex; justify-content: space-between; align-items: start; gap: 10px;">
                                <div style="flex: 1;">
                                    <strong>${idx + 1}. ${item.headline}</strong>
                                </div>
                                <span class="sentiment-badge sentiment-${item.sentiment}">
                                    ${item.sentiment.toUpperCase()}
                                </span>
                            </div>
                            ${analysisText ? `<p style="margin-top: 10px; color: #666; font-size: 0.9rem;">${analysisText}...</p>` : ''}
                        </div>
                    `;
                });
                document.getElementById('sentimentDetails').innerHTML = sentimentHtml;
                
                // Headlines
                const headlines = data.search_results?.headlines || [];
                let headlinesHtml = '';
                if (headlines.length === 0) {
                    headlinesHtml = '<p>No headlines found.</p>';
                } else {
                    headlines.forEach((headline, idx) => {
                        const title = typeof headline === 'object' ? 
                            (headline.title || headline.headline || headline.raw_response || JSON.stringify(headline)) :
                            headline;
                        headlinesHtml += `
                            <div class="headline-item">
                                <strong>${idx + 1}.</strong> ${title}
                            </div>
                        `;
                    });
                }
                document.getElementById('headlines').innerHTML = headlinesHtml;
                
                // Fact Check
                document.getElementById('factCheck').textContent = summary.fact_check || 'No fact check available';
                
                // Bias Check
                document.getElementById('biasCheck').textContent = summary.bias_check || 'No bias check available';
                
                // Forensic Analysis
                document.getElementById('forensicAnalysis').textContent = summary.forensic_analysis || 'No forensic analysis available';
                
                // Trends Analysis
                const trendsSection = document.getElementById('trendsSection');
                
                if (data.trends_analysis && data.trends_analysis.plot_data) {
                    const trendsData = data.trends_analysis;
                    const plotData = trendsData.plot_data;
                    
                    // Check if there's an error or no data
                    if (plotData.error || !plotData.plot_base64) {
                        // Show error message
                        trendsSection.style.display = 'block';
                        document.getElementById('trendsStats').innerHTML = '';
                        document.getElementById('trendsPlot').innerHTML = `
                            <div style="padding: 40px; text-align: center; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dee2e6;">
                                <h3 style="color: #6c757d; margin-bottom: 10px;">📊 No Trends Data Available</h3>
                                <p style="color: #6c757d;">Unable to fetch Google Trends data for this query.</p>
                                <p style="color: #6c757d; font-size: 0.9em;">${plotData.error || 'No data found'}</p>
                            </div>
                        `;
                        document.getElementById('trendsAnalysis').innerHTML = '';
                    } else {
                        // Show trends section
                        trendsSection.style.display = 'block';
                        
                        // Display statistics
                        if (plotData.statistics) {
                            const stats = plotData.statistics;
                            document.getElementById('trendsStats').innerHTML = `
                                <div class="stat-card">
                                    <div class="stat-value" style="color: #667eea;">${stats.current}</div>
                                    <div class="stat-label">Current Interest</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" style="color: #28a745;">${stats.max}</div>
                                    <div class="stat-label">Peak Interest</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" style="color: #ffc107;">${stats.average}</div>
                                    <div class="stat-label">Average Interest</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" style="color: ${stats.trend_direction === 'rising' ? '#28a745' : stats.trend_direction === 'falling' ? '#dc3545' : '#6c757d'};">
                                        ${stats.trend_direction.toUpperCase()}
                                    </div>
                                    <div class="stat-label">Trend Direction</div>
                                </div>
                            `;
                        } else {
                            document.getElementById('trendsStats').innerHTML = '';
                        }
                        
                        // Display plot with unique key to force re-render
                        const timestamp = new Date().getTime();
                        const plotElement = document.getElementById('trendsPlot');
                        plotElement.innerHTML = '';  // Clear first
                        
                        const img = document.createElement('img');
                        img.src = `data:image/png;base64,${plotData.plot_base64}`;
                        img.alt = 'Google Trends Plot';
                        img.style.cssText = 'max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);';
                        img.setAttribute('data-timestamp', timestamp);
                        
                        plotElement.appendChild(img);
                        
                        // Display analysis
                        if (trendsData.trend_analysis && trendsData.trend_analysis.analysis) {
                            document.getElementById('trendsAnalysis').innerHTML = `
                                <h3>Analysis</h3>
                                <p style="line-height: 1.8; white-space: pre-wrap;">${trendsData.trend_analysis.analysis}</p>
                            `;
                        } else {
                            document.getElementById('trendsAnalysis').innerHTML = '';
                        }
                    }
                } else {
                    // Hide trends section if no data
                    trendsSection.style.display = 'none';
                }
                
                // Full Response
                document.getElementById('fullResponse').textContent = JSON.stringify(data, null, 2);
                
                results.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "manager_agent"}


@app.post("/run")
async def run_pipeline(request: QueryRequest) -> Dict[str, Any]:
    """
    Execute the full news search, sentiment analysis, and trends pipeline.
    
    Args:
        request: Query request containing the search topic
        
    Returns:
        Complete analysis results including search results, sentiment, summary, and trends
    """
    try:
        logger.info(f"Received query: {request.query}")
        result = root_agent.run_with_trends(request.query)
        
        if "error" in result:
            logger.error(f"Pipeline error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/services/health")
async def check_services():
    """Check health of all microservices."""
    try:
        health_status = root_agent.check_services_health()
        all_healthy = all(health_status.values())
        
        return {
            "manager": "ok",
            "services": health_status,
            "all_healthy": all_healthy
        }
    except Exception as e:
        logger.error(f"Error checking services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
