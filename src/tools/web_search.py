from src.tools.base_tool import BaseTool
import requests
from typing import List, Dict
import re
from html import unescape

class WebSearchTool(BaseTool):
    """Real web search using DuckDuckGo (no API key required)"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for product information, reviews, prices, and comparisons. Takes search query as input. Returns relevant search results with titles, snippets, and sources."
        )
        # DuckDuckGo endpoints
        self.instant_answer_url = "https://api.duckduckgo.com/"
        self.html_search_url = "https://html.duckduckgo.com/html/"
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
        """Call DuckDuckGo for real search results."""
        try:
            # 1) Try instant-answer API first (can be empty for many queries).
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }

            response = requests.get(
                self.instant_answer_url,
                params=params,
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            results = []

            if data.get("Results"):
                for result in data.get("Results", [])[:3]:
                    results.append({
                        "title": result.get("Title", ""),
                        "snippet": result.get("Text", ""),
                        "link": result.get("FirstURL", "")
                    })

            if not results and data.get("RelatedTopics"):
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1],
                            "snippet": topic.get("Text", ""),
                            "link": topic.get("FirstURL", "")
                        })

            if results:
                return results

            # 2) Fallback to DuckDuckGo HTML SERP parsing for regular web results.
            html_response = requests.post(
                self.html_search_url,
                data={"q": query},
                headers=self.headers,
                timeout=8
            )
            html_response.raise_for_status()
            html = html_response.text

            link_matches = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                html,
                flags=re.IGNORECASE | re.DOTALL,
            )
            snippet_matches = re.findall(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>|<div[^>]*class="result__snippet"[^>]*>(.*?)</div>',
                html,
                flags=re.IGNORECASE | re.DOTALL,
            )

            parsed_results = []
            for i, (link, title_html) in enumerate(link_matches[:5]):
                title = re.sub(r"<.*?>", "", title_html).strip()
                title = unescape(title)
                link = unescape(link)
                snippet = ""
                if i < len(snippet_matches):
                    snippet_html = snippet_matches[i][0] or snippet_matches[i][1]
                    snippet = unescape(re.sub(r"<.*?>", "", snippet_html).strip())

                # DuckDuckGo can return redirect links (/l/?uddg=...)
                uddg_match = re.search(r"[?&]uddg=([^&]+)", link)
                if uddg_match:
                    link = requests.utils.unquote(uddg_match.group(1))

                parsed_results.append({
                    "title": title or "N/A",
                    "snippet": snippet or "No snippet available.",
                    "link": link or "N/A",
                })

            return parsed_results
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.RequestException as e:
            raise Exception(f"DuckDuckGo API error: {str(e)}")

