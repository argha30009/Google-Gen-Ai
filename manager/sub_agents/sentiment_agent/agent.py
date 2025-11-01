from google.adk.agents import Agent
from textblob import TextBlob

from typing import List, Dict, Any
from google.adk.agents import Agent
sentiment_agent = Agent(
    name="sentiment_agent",
    model="gemini-2.5-flash",
    description="Analyzes sentiment of news headlines.",
    instruction="Given some news headlines in a list, analyze the sentiment of each headline and provide an overall sentiment summary.",
)

