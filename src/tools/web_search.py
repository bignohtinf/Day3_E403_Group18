from src.tools.base_tool import BaseTool
import requests
import os
from typing import List, Dict

class WebSearchToolReal(BaseTool):
    """Real web search using SerpAPI"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for product information, reviews, prices, and comparisons. Takes search query as input. Returns relevant search results with titles, snippets, and sources."
        )
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not set in .env")

    def execute(self, query: str) -> str:
        """Execute real web search"""
        query = query.strip()

        if not query:
            return "Error: Please provide a search query."

        try:
            results = self._search_web(query)

            if not results:
                return f"No search results found for '{query}'."

            # Format results
            result_text = f"Search results for '{query}':\n\n"
            for i, result in enumerate(results[:3], 1):
                result_text += f"{i}. {result.get('title', 'N/A')}\n"
                result_text += f"   {result.get('snippet', 'N/A')}\n"
                result_text += f"   Link: {result.get('link', 'N/A')}\n\n"

            return result_text
        except Exception as e:
            return f"Error searching web: {str(e)}"

    def _search_web(self, query: str) -> List[Dict]:
        """Call SerpAPI for real search"""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": 3  # Get top 3 results
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("organic_results", [])

        return [
            {
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "link": r.get("link")
            }
            for r in results
        ]
