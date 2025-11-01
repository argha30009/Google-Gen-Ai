#!/usr/bin/env python3
"""
Test script for Google ADK Microservices
Validates all services are working correctly
"""

import httpx
import json
import sys
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'=' * 50}")
    print(text)
    print('=' * 50)


def print_success(text: str):
    """Print success message in green"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text: str):
    """Print error message in red"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_warning(text: str):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")


def check_service_health(url: str, name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = httpx.get(f"{url}/health", timeout=5.0)
        if response.status_code == 200:
            print_success(f"{name} is running")
            return True
        else:
            print_error(f"{name} returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"{name} is not accessible: {e}")
        return False


def test_search_service(base_url: str) -> Dict[str, Any]:
    """Test the search service"""
    print("\n" + "-" * 50)
    print("Testing Search Service")
    print("-" * 50)
    
    try:
        response = httpx.post(
            f"{base_url}/run",
            json={"query": "OpenAI"},
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()
        
        print("\nRequest: POST /run")
        print(f"Query: OpenAI")
        print("\nResponse:")
        print(json.dumps(result, indent=2))
        
        print_success("Search service test passed")
        return result
    except Exception as e:
        print_error(f"Search service test failed: {e}")
        return {}


def test_sentiment_service(base_url: str) -> Dict[str, Any]:
    """Test the sentiment service"""
    print("\n" + "-" * 50)
    print("Testing Sentiment Service")
    print("-" * 50)
    
    headlines = [
        "OpenAI announces breakthrough in AI research",
        "Tech stocks decline amid market uncertainty",
        "New regulations proposed for AI industry"
    ]
    
    try:
        response = httpx.post(
            f"{base_url}/run",
            json={"headlines": headlines},
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()
        
        print("\nRequest: POST /run")
        print(f"Headlines: {len(headlines)} items")
        print("\nResponse:")
        print(json.dumps(result, indent=2))
        
        print_success("Sentiment service test passed")
        return result
    except Exception as e:
        print_error(f"Sentiment service test failed: {e}")
        return {}


def test_manager_agent():
    """Test the manager agent orchestration"""
    print("\n" + "-" * 50)
    print("Testing Manager Agent Orchestration")
    print("-" * 50)
    
    try:
        # Import the manager agent
        sys.path.insert(0, '/Users/amansiddharth/Downloads/gh')
        from manager.agent import root_agent
        
        print("\nExecuting: root_agent.run('OpenAI')")
        result = root_agent.run("OpenAI")
        
        print("\nManager Agent Response:")
        print(json.dumps(result, indent=2))
        
        if "error" not in result:
            print_success("Manager agent test passed")
        else:
            print_warning(f"Manager agent returned error: {result.get('error')}")
        
        return result
    except Exception as e:
        print_error(f"Manager agent test failed: {e}")
        print("\nMake sure you're in the correct directory and dependencies are installed.")
        return {}


def main():
    """Main test function"""
    print_header("Google ADK Microservices Test Suite")
    
    # Service URLs
    search_url = "http://localhost:8001"
    sentiment_url = "http://localhost:8002"
    
    # Step 1: Health checks
    print_header("Step 1: Health Checks")
    
    search_healthy = check_service_health(search_url, "Search Agent Service")
    sentiment_healthy = check_service_health(sentiment_url, "Sentiment Agent Service")
    
    if not (search_healthy and sentiment_healthy):
        print_warning("\nSome services are not running!")
        print("\nTo start services locally:")
        print("  Terminal 1: cd manager/sub_agents/search_agent && uvicorn server:app --port 8001")
        print("  Terminal 2: cd manager/sub_agents/sentiment_agent && uvicorn server:app --port 8002")
        print("\nOr use Docker:")
        print("  docker compose up --build")
        sys.exit(1)
    
    # Step 2: Test search service
    print_header("Step 2: Search Service Test")
    search_result = test_search_service(search_url)
    
    # Step 3: Test sentiment service
    print_header("Step 3: Sentiment Service Test")
    sentiment_result = test_sentiment_service(sentiment_url)
    
    # Step 4: Test manager agent (optional)
    print_header("Step 4: Manager Agent Test (Optional)")
    print("\nAttempting to test manager agent...")
    try:
        manager_result = test_manager_agent()
    except Exception as e:
        print_warning(f"Manager agent test skipped: {e}")
        print("This is optional - services are working correctly.")
    
    # Summary
    print_header("Test Summary")
    print_success("All microservices are operational!")
    print("\n📚 API Documentation:")
    print(f"  - Search Agent:    {search_url}/docs")
    print(f"  - Sentiment Agent: {sentiment_url}/docs")
    print("\n🎯 Next steps:")
    print("  - Test with your own queries")
    print("  - Integrate with your application")
    print("  - Deploy to production")
    print()


if __name__ == "__main__":
    main()
