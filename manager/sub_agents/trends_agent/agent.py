"""
Google Trends Agent using Google ADK.
Fetches and visualizes Google Trends data for a given keyword.
"""

from google.adk.agents import Agent

google_trends_agent = Agent(
    name="google_trends_agent",
    model="gemini-2.5-flash",
    description="Fetches and visualizes Google Trends data for a keyword.",
    instruction=(
        "Given a keyword, analyze its Google search interest over time. "
        "Use the Google Trends API to fetch interest data and generate a trend summary. "
        "Provide insights about the trend pattern (rising, falling, stable). "
        "Return a detailed textual summary including: "
        "1. Current trend status (rising/falling/stable) "
        "2. Peak interest periods "
        "3. Overall trend direction "
        "4. Notable patterns or seasonality "
        "Format the response as a structured analysis."
    ),
)
