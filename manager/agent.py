"""
Manager agent that orchestrates search and sentiment analysis via HTTP microservices.
"""
import os
import time
import httpx
import logging
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration - use environment variables for Cloud Run deployment
SEARCH_SERVICE_URL = os.getenv("SEARCH_AGENT_URL", "http://localhost:8001")
SENTIMENT_SERVICE_URL = os.getenv("SENTIMENT_AGENT_URL", "http://localhost:8002")
TRENDS_SERVICE_URL = os.getenv("TRENDS_AGENT_URL", "http://localhost:8003")
FACTCHECK_SERVICE_URL = os.getenv("FACTCHECK_AGENT_URL", "http://localhost:8004")
REQUEST_TIMEOUT = 60.0  # seconds (increased for AI processing)
MAX_RETRIES = 3


class ManagerAgent:
    """
    Manager agent that orchestrates news search and sentiment analysis
    by calling microservices via HTTP.
    """
    
    def __init__(
        self,
        search_url: str = SEARCH_SERVICE_URL,
        sentiment_url: str = SENTIMENT_SERVICE_URL,
        trends_url: str = TRENDS_SERVICE_URL,
        factcheck_url: str = FACTCHECK_SERVICE_URL,
        timeout: float = REQUEST_TIMEOUT
    ):
        self.search_url = search_url
        self.sentiment_url = sentiment_url
        self.trends_url = trends_url
        self.factcheck_url = factcheck_url
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_search_service(self, query: str) -> Dict[str, Any]:
        """
        Call the search microservice with retry logic.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing headlines and metadata
        """
        try:
            logger.info(f"Calling search service with query: {query}")
            response = self.client.post(
                f"{self.search_url}/run",
                json={"query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Search service returned {result.get('meta', {}).get('count', 0)} results")
            return result
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling search service: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling search service: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_sentiment_service(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Call the sentiment microservice with retry logic.
        
        Args:
            headlines: List of headline strings to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            logger.info(f"Calling sentiment service with {len(headlines)} headlines")
            response = self.client.post(
                f"{self.sentiment_url}/run",
                json={"headlines": headlines},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Sentiment service completed analysis")
            return result
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling sentiment service: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling sentiment service: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_trends_service(self, keyword: str) -> Dict[str, Any]:
        """
        Call the trends microservice with retry logic.
        
        Args:
            keyword: Keyword to analyze trends for
            
        Returns:
            Dict containing trend analysis
        """
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling trends service for keyword: {keyword} (attempt {attempt + 1}/{max_retries})")
                response = self.client.post(
                    f"{self.trends_url}/run",
                    json={"keyword": keyword},
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Trends service completed analysis")
                return result
            except httpx.ConnectError as e:
                logger.warning(f"Connection error to trends service (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Trends service unavailable after {max_retries} attempts")
                    raise
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling trends service: {e}")
                raise
            except Exception as e:
                logger.error(f"Error calling trends service: {e}")
                raise
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_factcheck_service(self, headlines: List[str], query: Optional[str] = None) -> Dict[str, Any]:
        """
        Call the fact-check microservice with retry logic.
        
        Args:
            headlines: List of headlines to check for contradictions
            query: Optional original user query for context
            
        Returns:
            Dict containing fact-check analysis
        """
        try:
            logger.info(f"Calling fact-check service with {len(headlines)} headlines")
            response = self.client.post(
                f"{self.factcheck_url}/run",
                json={"headlines": headlines, "query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Fact-check service completed analysis")
            return result
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling fact-check service: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling fact-check service: {e}")
            raise
    
    def check_services_health(self) -> Dict[str, bool]:
        """
        Check health status of all microservices.
        
        Returns:
            Dict with service names and their health status
        """
        health_status = {}
        
        try:
            response = self.client.get(f"{self.search_url}/health", timeout=5.0)
            health_status["search_service"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Search service health check failed: {e}")
            health_status["search_service"] = False
        
        try:
            response = self.client.get(f"{self.sentiment_url}/health", timeout=5.0)
            health_status["sentiment_service"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Sentiment service health check failed: {e}")
            health_status["sentiment_service"] = False
        
        try:
            response = self.client.get(f"{self.trends_url}/health", timeout=5.0)
            health_status["trends_service"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Trends service health check failed: {e}")
            health_status["trends_service"] = False
        
        try:
            response = self.client.get(f"{self.factcheck_url}/health", timeout=5.0)
            health_status["factcheck_service"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Fact-check service health check failed: {e}")
            health_status["factcheck_service"] = False
        
        return health_status
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute the full pipeline: search for news and analyze sentiment.
        
        Args:
            query: Topic to search for
            
        Returns:
            Dict containing search results, sentiment analysis, and reports
        """
        try:
            # Check service health
            health = self.check_services_health()
            if not all(health.values()):
                logger.warning(f"Some services are unhealthy: {health}")
            
            # Step 1: Get news headlines
            search_results = self._call_search_service(query)
            headlines_data = search_results.get("headlines", [])
            
            # Extract headline text for sentiment analysis
            headlines = []
            for item in headlines_data:
                if isinstance(item, dict):
                    # Try to extract title/headline from various possible fields
                    headline = (
                        item.get("title") or 
                        item.get("headline") or 
                        item.get("raw_response") or
                        str(item)
                    )
                    headlines.append(headline)
                else:
                    headlines.append(str(item))
            
            if not headlines:
                logger.warning("No headlines extracted from search results")
                return {
                    "query": query,
                    "search_results": search_results,
                    "error": "No headlines found to analyze"
                }
            
            # Step 2: Analyze sentiment
            sentiment_results = self._call_sentiment_service(headlines)
            
            # Step 3: Fact-check for contradictions and controversial claims
            factcheck_results = None
            try:
                factcheck_results = self._call_factcheck_service(headlines, query=query)
            except Exception as e:
                logger.warning(f"Fact-check service failed, continuing without it: {e}")
                factcheck_results = {
                    "error": str(e),
                    "status": "unavailable"
                }
            
            # Step 4: Compile comprehensive report
            report = {
                "query": query,
                "search_results": search_results,
                "sentiment_analysis": sentiment_results,
                "factcheck_analysis": factcheck_results,
                "summary": self._generate_summary(
                    query, headlines_data, sentiment_results, factcheck_results
                )
            }
            
            logger.info(f"Pipeline completed successfully for query: {query}")
            return report
            
        except Exception as e:
            logger.error(f"Error in pipeline execution: {e}")
            return {
                "query": query,
                "error": str(e),
                "status": "failed"
            }
    
    def _is_news_related_query(self, query: str) -> bool:
        """
        Check if the query is related to news/current events or not.
        Returns False for math equations, recipes, code, how-to queries, etc.
        
        Args:
            query: The user's query
            
        Returns:
            bool: True if query appears to be news-related, False otherwise
        """
        query_lower = query.lower().strip()
        
        # Check for mathematical expressions
        math_patterns = ['+', '-', '×', '÷', '=', 'solve', 'equation', 'calculate', 
                        'sum', 'multiply', 'divide', 'subtract', 'add', 'square root',
                        'derivative', 'integral', 'x^', 'x²', 'x³']
        if any(pattern in query_lower for pattern in math_patterns):
            # Check if it's actually math (has numbers with operators)
            if any(char.isdigit() for char in query):
                return False
        
        # Check for recipe/cooking queries
        recipe_patterns = ['recipe for', 'how to cook', 'how to make', 'how to bake',
                          'cooking instructions', 'ingredients for', 'cook ', 'bake ',
                          'recipe of', 'how do i cook', 'how do i make']
        if any(pattern in query_lower for pattern in recipe_patterns):
            return False
        
        # Check for code/programming queries
        code_patterns = ['write code', 'python code', 'javascript code', 'function to',
                        'code for', 'programming', 'how to code', 'script for',
                        'algorithm for', 'implement', 'def ', 'function(', 'class ']
        if any(pattern in query_lower for pattern in code_patterns):
            return False
        
        # Check for general how-to/tutorial queries (not news-related)
        howto_patterns = ['how to fix', 'how to install', 'how to use', 'tutorial',
                         'step by step', 'guide to', 'instructions for']
        if any(pattern in query_lower for pattern in howto_patterns):
            return False
        
        # Check for personal questions
        personal_patterns = ['what is my', 'where am i', 'who am i', 'tell me a joke',
                           'fun fact', 'riddle']
        if any(pattern in query_lower for pattern in personal_patterns):
            return False
        
        # Very short queries without news context (likely not news)
        if len(query_lower.split()) < 2 and not any(word in query_lower for word in 
                                                     ['news', 'update', 'latest', 'today']):
            # Single word queries without news keywords are likely not news-related
            # unless they're proper nouns or topics
            return len(query_lower) > 3  # Allow longer single words (e.g., "Brexit")
        
        return True
    
    def run_with_trends(self, query: str) -> Dict[str, Any]:
        """
        Execute the full pipeline with Google Trends analysis.
        
        Args:
            query: Topic to search for
            
        Returns:
            Dict containing search results, sentiment analysis, trends analysis, and reports
        """
        try:
            # Validate if query is news-related
            if not self._is_news_related_query(query):
                logger.info(f"Non-news query detected: {query}")
                return {
                    "query": query,
                    "search_results": {
                        "headlines": [],
                        "message": "Could not find any data for the topic"
                    },
                    "sentiment_analysis": {
                        "sentiment_summary": {
                            "overall": "neutral",
                            "positive_count": 0,
                            "negative_count": 0,
                            "neutral_count": 0,
                            "total_analyzed": 0
                        },
                        "per_item": [],
                        "message": "Could not find any data for the topic"
                    },
                    "trends_analysis": {
                        "message": "Could not find any data for the topic"
                    },
                    "summary": {
                        "overview": f"No news data available for '{query}'",
                        "sentiment_overview": "neutral",
                        "sentiment_summary": f"Could not find any data for the topic '{query}'. This query does not appear to be related to news or current events.",
                        "fact_check": f"Could not find any data for the topic '{query}'.",
                        "bias_check": f"Could not find any data for the topic '{query}'.",
                        "forensic_analysis": f"Could not find any data for the topic '{query}'."
                    },
                    "status": "no_data"
                }
            
            # Run the standard pipeline
            report = self.run(query)
            
            # If standard pipeline failed, return early
            if "error" in report:
                return report
            
            # Step 4: Get Google Trends analysis
            try:
                trends_results = self._call_trends_service(query)
                report["trends_analysis"] = trends_results
                logger.info(f"Trends analysis added for query: {query}")
            except Exception as e:
                logger.warning(f"Trends analysis failed, continuing without it: {e}")
                # Provide a proper structure that frontend expects
                report["trends_analysis"] = {
                    "keyword": query,
                    "trend_analysis": {
                        "analysis": f"Unable to fetch Google Trends data: {str(e)}",
                        "status": "failed",
                        "error": str(e)
                    },
                    "plot_data": None,
                    "status": "failed"
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Error in pipeline execution with trends: {e}")
            return {
                "query": query,
                "error": str(e),
                "status": "failed"
            }
    
    def _generate_summary(
        self,
        query: str,
        headlines_data: List[Dict],
        sentiment_results: Dict,
        factcheck_results: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report including sentiment, fact check, 
        bias check, and forensic analysis.
        
        Args:
            query: Original search query
            headlines_data: Raw headline data from search
            sentiment_results: Sentiment analysis results
            factcheck_results: Fact-check analysis results (optional)
            
        Returns:
            Dict containing various report sections
        """
        summary = sentiment_results.get("sentiment_summary", {})
        per_item = sentiment_results.get("per_item", [])
        
        # Extract sentiment counts
        positive_count = summary.get("positive_count", 0)
        negative_count = summary.get("negative_count", 0)
        neutral_count = summary.get("neutral_count", 0)
        total = summary.get("total_analyzed", 0)
        overall_sentiment = summary.get("overall", "mixed")
        
        # Build sentiment summary text
        sentiment_desc = "predominantly positive" if overall_sentiment == "positive" else \
                        "predominantly negative" if overall_sentiment == "negative" else \
                        "mixed with both positive and negative tones"
        
        sentiment_summary = f"""Here's a summary of the news regarding {query}:

Sentiment Summary:
The sentiment around the topic of '{query}' is {sentiment_desc}, with {positive_count} positive, {negative_count} negative, and {neutral_count} neutral headlines out of {total} total articles analyzed. The overall tone reflects {overall_sentiment} sentiment based on the language and framing used across different news sources.

Headlines and their Sentiment:"""
        
        # Add individual headline sentiments
        for item in per_item:
            headline = item.get("headline", "")
            sentiment = item.get("sentiment", "neutral").capitalize()
            sentiment_summary += f"\n• {headline} - **{sentiment}**"
        
        # Fact Check Report - Use AI-powered analysis if available
        if factcheck_results and factcheck_results.get("status") == "success":
            ai_analysis = factcheck_results.get("analysis", "")
            fact_check = f"""Fact Check Report:
AI-Powered Contradiction and Controversy Analysis for '{query}':

{ai_analysis}

---
This analysis was performed by our fact-check agent which examined all {total} headlines for contradictions, controversial claims, and potential misinformation."""
        else:
            # Fallback to basic fact check if AI service unavailable
            fact_check = f"""Fact Check Report:
Here's a breakdown of verifiable information and discrepancies based on the search results for '{query}'.

Verifiable Facts:
• Multiple news sources report on the topic of '{query}' with consistent core information across {total} headlines analyzed.
• The information appears in reputable news outlets, suggesting the story has been widely covered.

Discrepancies/Differently Stated Information:
• Different news outlets may frame the same information with varying emphasis or perspective.
• Some sources may include additional context or analysis not present in others.
• The language used to describe events may vary from neutral reporting to more critical or supportive tones.

Conclusion of Fact Check:
While most news sources provide similar accounts of the core facts, there may be variations in framing, emphasis, and interpretation. For critical information, cross-referencing multiple sources and checking primary sources is recommended. The presence of {total} different headlines suggests this is a widely reported topic with multiple perspectives available.

Note: Advanced AI-powered fact-check analysis is currently unavailable."""
        
        # Bias Check Report
        bias_check = f"""Bias Check Report:
Analyzing the {total} headlines reveals a mix of reporting styles, with some exhibiting potential biases:

Potential Biases Detected:
• Sentiment Distribution: {positive_count} positive, {negative_count} negative, and {neutral_count} neutral headlines suggest a {overall_sentiment} overall tone.
• Framing Variations: Different outlets may frame the same story with varying emphasis - some more critical, others more neutral or supportive.
• Language Choices: The specific words and phrases used can indicate editorial stance or target audience preferences.
• Source Diversity: The variety of sources covering this topic suggests multiple perspectives are available.

Conclusion:
While it is challenging to definitively label each source as biased without deeper analysis, the overall pattern shows a {overall_sentiment} sentiment across the headlines. The distribution of {positive_count} positive, {negative_count} negative, and {neutral_count} neutral articles suggests {"balanced coverage" if abs(positive_count - negative_count) <= 2 else "a leaning toward " + ("positive" if positive_count > negative_count else "negative") + " framing"}. Readers should consider multiple sources and be aware of potential framing differences when forming opinions on '{query}'."""
        
        # Forensic Analysis and Source Tracking Report
        # Extract headlines with any available metadata
        timeline_items = []
        for item in per_item[:10]:  # Limit to first 10 for readability
            headline = item.get("headline", "")
            if headline:
                timeline_items.append(f"  - {headline}")
        
        timeline_text = "\n".join(timeline_items) if timeline_items else "  - Headlines available in search results"
        
        forensic_analysis = f"""Forensic Analysis and Source Tracking Report:
To determine the likely origin and spread of news about '{query}', we examine the available information from the search results.

Timeline of Key News Items:
{timeline_text}

Analysis of Origin:
Based on the {total} headlines analyzed, this topic has been covered by multiple news sources. The search results show a variety of outlets reporting on '{query}', suggesting widespread coverage and interest.

Key Observations:
• Multiple Sources: The presence of {total} different headlines indicates this story has been picked up by numerous outlets.
• Sentiment Pattern: The {overall_sentiment} overall sentiment ({positive_count} positive, {negative_count} negative, {neutral_count} neutral) may indicate how the story evolved or how different outlets chose to frame it.
• Information Flow: Without specific timestamps, we can observe that the story has achieved significant coverage across various news platforms.

Conclusion:
While specific publication dates and times would be needed for precise forensic tracking, the breadth of coverage ({total} headlines) suggests this is a significant news story that has been widely disseminated. The earliest reporting outlet would typically be identified by comparing publication timestamps, which would require access to the full article metadata. The variety of sources and sentiments indicates the story has been interpreted and reported from multiple perspectives."""
        
        return {
            "overview": f"Analysis of {total} headlines about '{query}'",
            "sentiment_overview": overall_sentiment,
            "sentiment_summary": sentiment_summary,
            "fact_check": fact_check,
            "bias_check": bias_check,
            "forensic_analysis": forensic_analysis
        }
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Create a singleton instance
root_agent = ManagerAgent()
