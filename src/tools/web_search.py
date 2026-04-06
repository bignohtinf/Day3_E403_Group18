from src.tools.base_tool import BaseTool
import requests
from typing import List, Dict
import re

class WebSearchTool(BaseTool):
    """Real web search using DuckDuckGo (no API key required)"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for product information, reviews, prices, and comparisons. Takes search query as input. Returns relevant search results with titles, snippets, and sources."
        )
        # DuckDuckGo API endpoint
        self.search_url = "https://api.duckduckgo.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def execute(self, query: str) -> str:
        """Execute real web search using DuckDuckGo"""
        query = query.strip()

        if not query:
            return "Error: Please provide a search query."

        try:
            results = self._search_web(query)

            if not results:
                return f"No search results found for '{query}'."

            # Format results
            result_text = f"Search results for '{query}':\n\n"
            for i, result in enumerate(results[:3], 1):  # Top 3 results
                result_text += f"{i}. {result.get('title', 'N/A')}\n"
                result_text += f"   {result.get('snippet', 'N/A')}\n"
                result_text += f"   Link: {result.get('link', 'N/A')}\n\n"

            return result_text
        except Exception as e:
            return f"Error searching web: {str(e)}"

    def _search_web(self, query: str) -> List[Dict]:
        """Call DuckDuckGo API for real search"""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }

            response = requests.get(
                self.search_url,
                params=params,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract results from DuckDuckGo response
            # DuckDuckGo returns results in 'Results' field
            if data.get("Results"):
                for result in data.get("Results", [])[:3]:
                    results.append({
                        "title": result.get("Title", ""),
                        "snippet": result.get("Text", ""),
                        "link": result.get("FirstURL", "")
                    })

            # If no results from Results, try RelatedTopics
            if not results and data.get("RelatedTopics"):
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1],
                            "snippet": topic.get("Text", ""),
                            "link": topic.get("FirstURL", "")
                        })

            return results
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.RequestException as e:
            raise Exception(f"DuckDuckGo API error: {str(e)}")

