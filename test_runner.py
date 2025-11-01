#!/usr/bin/env python3
"""Test script to debug the Runner behavior"""

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from manager.sub_agents.search_agent.agent import search_agent
import uuid

# Initialize the runner
runner = Runner(
    app_name="test_app",
    agent=search_agent,
    session_service=InMemorySessionService()
)

# Test query
user_id = "test_user"
session_id = str(uuid.uuid4())
query = "OpenAI latest news"

# Create session first
session_service = runner.session_service
session_service.create_session(user_id=user_id, session_id=session_id, app_name="test_app")

print(f"Testing query: {query}")
print("=" * 60)

event_count = 0
for event in runner.run(
    user_id=user_id,
    session_id=session_id,
    new_message=query
):
    event_count += 1
    print(f"\n--- Event {event_count} ---")
    print(f"Type: {type(event)}")
    print(f"Has content: {hasattr(event, 'content')}")
    
    if hasattr(event, 'content') and event.content:
        print(f"Content: {event.content}")
    
    if hasattr(event, 'turn_complete'):
        print(f"Turn complete: {event.turn_complete}")
    
    if hasattr(event, 'finish_reason'):
        print(f"Finish reason: {event.finish_reason}")
    
    if hasattr(event, 'error_message') and event.error_message:
        print(f"Error: {event.error_message}")
    
    # Print all non-None fields
    print("All fields:")
    for field_name in event.model_fields.keys():
        value = getattr(event, field_name, None)
        if value is not None:
            print(f"  {field_name}: {value}")

print(f"\n{'=' * 60}")
print(f"Total events: {event_count}")
