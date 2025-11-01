from google.adk.agents import Agent
from google.adk.tools import google_search

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    description="Fetches news from Google Search",
    instruction="Use google_search to fetch headlines for a topic (you may rephrase to query to get better search results), along with their source name, and publish date and time.",
    tools=[google_search]
)
