#!/usr/bin/env python3
"""Test script for query validation."""

import requests
import json

def test_query(query):
    """Test a query against the manager service."""
    print(f"\n{'='*60}")
    print(f"Testing query: '{query}'")
    print('='*60)
    
    try:
        response = requests.post(
            "http://localhost:8000/run",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nStatus: {result.get('status', 'success')}")
            print(f"\nSearch Results:")
            print(f"  Message: {result.get('search_results', {}).get('message', 'N/A')}")
            print(f"  Headlines: {len(result.get('search_results', {}).get('headlines', []))}")
            
            print(f"\nSentiment Analysis:")
            sentiment = result.get('sentiment_analysis', {})
            print(f"  Message: {sentiment.get('message', 'N/A')}")
            summary = sentiment.get('sentiment_summary', {})
            print(f"  Total Analyzed: {summary.get('total_analyzed', 0)}")
            
            print(f"\nTrends Analysis:")
            trends = result.get('trends_analysis', {})
            print(f"  Message: {trends.get('message', 'N/A')}")
            
            print(f"\nSummary:")
            summary_section = result.get('summary', {})
            print(f"  Overview: {summary_section.get('overview', 'N/A')}")
            print(f"  Sentiment Summary: {summary_section.get('sentiment_summary', 'N/A')[:100]}...")
        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test non-news queries
    test_queries = [
        "2 + 2",
        "solve x^2 + 5x + 6 = 0",
        "recipe for chocolate cake",
        "how to make pasta",
        "write code for bubble sort",
        "python function to reverse string",
        # Test news queries to ensure they still work
        "AI news",
        "latest technology updates"
    ]
    
    for query in test_queries:
        test_query(query)
    
    print(f"\n{'='*60}")
    print("All tests completed!")
    print('='*60)
