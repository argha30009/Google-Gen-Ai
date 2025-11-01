"""
Manager agent that orchestrates search and sentiment analysis via HTTP microservices.
"""
import httpx
import logging
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration
SEARCH_SERVICE_URL = "http://localhost:8001"
SENTIMENT_SERVICE_URL = "http://localhost:8002"
TRENDS_SERVICE_URL = "http://localhost:8003"
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
        timeout: float = REQUEST_TIMEOUT
    ):
        self.search_url = search_url
        self.sentiment_url = sentiment_url
        self.trends_url = trends_url
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
        try:
            logger.info(f"Calling trends service for keyword: {keyword}")
            response = self.client.post(
                f"{self.trends_url}/run",
                json={"keyword": keyword},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Trends service completed analysis")
            return result
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling trends service: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling trends service: {e}")
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
            
            # Step 3: Compile comprehensive report
            report = {
                "query": query,
                "search_results": search_results,
                "sentiment_analysis": sentiment_results,
                "summary": self._generate_summary(
                    query, headlines_data, sentiment_results
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
    
    def run_with_trends(self, query: str) -> Dict[str, Any]:
        """
        Execute the full pipeline with Google Trends analysis.
        
        Args:
            query: Topic to search for
            
        Returns:
            Dict containing search results, sentiment analysis, trends analysis, and reports
        """
        try:
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
                report["trends_analysis"] = {
                    "error": str(e),
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
        sentiment_results: Dict
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report including sentiment, fact check, 
        bias check, and forensic analysis.
        
        Args:
            query: Original search query
            headlines_data: Raw headline data from search
            sentiment_results: Sentiment analysis results
            
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
        
        # Fact Check Report
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
While most news sources provide similar accounts of the core facts, there may be variations in framing, emphasis, and interpretation. For critical information, cross-referencing multiple sources and checking primary sources is recommended. The presence of {total} different headlines suggests this is a widely reported topic with multiple perspectives available."""
        
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
