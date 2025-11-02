import os
import json
from typing import Any, Dict
from google.adk.agents import Agent
from google.adk.tools import google_search

SEARCH_RESULT_LIMIT = int(os.getenv("SEARCH_RESULT_LIMIT", 20))

# Create callable wrapper for google_search tool to fix "'GoogleSearchTool' object is not callable" error
def google_search_wrapper(query: str, num_results: int = SEARCH_RESULT_LIMIT) -> str:
    """
    Callable wrapper around ADK's google_search tool.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default from env)
        
    Returns:
        JSON string with search results
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f">>> google_search_wrapper CALLED with query='{query}', num_results={num_results}")
    
    try:
        # Call the google_search tool's execute method
        if hasattr(google_search, 'execute'):
            result = google_search.execute(query=query, num_results=num_results)
        elif hasattr(google_search, 'run'):
            result = google_search.run(query=query, num_results=num_results)
        elif hasattr(google_search, '__call__'):
            result = google_search(query=query, num_results=num_results)
        else:
            # Fallback: try calling it as a function
            result = google_search(query, num_results)
        
        # Ensure result is JSON serializable
        logger.info(f">>> google_search_wrapper SUCCESS, result type: {type(result)}")
        if isinstance(result, str):
            return result
        return json.dumps(result)
    except Exception as e:
        # Return error in JSON format
        logger.error(f">>> google_search_wrapper ERROR: {str(e)}")
        return json.dumps({
            "error": str(e),
            "query": query,
            "status": "failed"
        })

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    description="Fetches and structures recent news headlines for a given topic using Google Search.",
    instruction=f"""
You are a structured News Search Agent. 
Your job is to fetch and format relevant news headlines for a given query.

### Task:
1. Use the `google_search` tool to retrieve up to {SEARCH_RESULT_LIMIT} relevant and recent news headlines.
2. Each result must include:
   - title (headline text)
   - query (the topic that was searched)
3. Do NOT include extra commentary, markdown, or preamble text. e.g,  Here are some recent news headlines about Donald Trump's private jet:

### Output Format:
{{
  "query": "<original or rephrased query>",
  "search_results": {{
    "headlines": [
      {{
        "title": "<headline text>",
        "query": "<search query>"
      }}
    ],
    "meta": {{
      "query": "<search query>",
      "count": <number of headlines>,
      "status": "success"
    }}
  }}
}}

### Rules:
- Output strictly in JSON — no natural language sentences.
- Avoid phrases like "Here are some recent headlines".
- Return only high-quality, factual headlines (ignore irrelevant results).
- If fewer than 5 valid headlines are found, still return all available ones.
- Ensure the number in meta.count matches the number of headlines.

### Example Output:
{{
  "query": "trump jet news",
  "search_results": {{
    "headlines": [
      {{
        "title": "Trump to accept luxury jet from Qatar, reports say (May 11, 2025)",
        "query": "trump jet news"
      }},
      {{
        "title": "Fighter jets scrambled, flares fired after planes violate Trump airspace over Bedminster, New Jersey (August 4, 2025)",
        "query": "trump jet news"
      }},
      {{
        "title": "Trump, Hegseth unveil new fighter jets as details emerge on Musk's Pentagon visit (March 21, 2025)",
        "query": "trump jet news"
      }}
    ],
    "meta": {{
      "query": "trump jet news",
      "count": 3,
      "status": "success"
    }}
  }}
}}
""",
    tools=[google_search]  # ADK will handle tool calling internally
)
