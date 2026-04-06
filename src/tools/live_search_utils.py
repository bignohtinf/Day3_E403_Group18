import re
from html import unescape
from typing import Dict, List, Optional

import requests


class LiveSearchUtils:
    """Helper methods for live web retrieval/parsing."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    DDG_HTML_URL = "https://html.duckduckgo.com/html/"

    @classmethod
    def search(cls, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        response = requests.post(
            cls.DDG_HTML_URL,
            data={"q": query},
            headers=cls.HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        html = response.text

        link_matches = re.findall(
            r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        snippet_matches = re.findall(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>|'
            r'<div[^>]*class="result__snippet"[^>]*>(.*?)</div>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        parsed: List[Dict[str, str]] = []
        for i, (href, title_html) in enumerate(link_matches):
            title = unescape(re.sub(r"<.*?>", "", title_html).strip())
            link = unescape(href)
            snippet = ""
            if i < len(snippet_matches):
                raw_snippet = snippet_matches[i][0] or snippet_matches[i][1]
                snippet = unescape(re.sub(r"<.*?>", "", raw_snippet).strip())

            # Resolve DDG redirect links.
            redirect = re.search(r"[?&]uddg=([^&]+)", link)
            if redirect:
                link = requests.utils.unquote(redirect.group(1))

            # Skip obvious ad tracking endpoints.
            if "duckduckgo.com/y.js" in link or "ad_provider=" in link:
                continue

            parsed.append(
                {
                    "title": title or "N/A",
                    "snippet": snippet or "No snippet.",
                    "link": link,
                }
            )
            if len(parsed) >= max_results:
                break
        return parsed

    @classmethod
    def fetch_text(cls, url: str) -> str:
        resp = requests.get(url, headers=cls.HEADERS, timeout=10)
        resp.raise_for_status()
        text = resp.text
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def fetch_html(cls, url: str) -> str:
        resp = requests.get(url, headers=cls.HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def extract_vnd_prices(text: str) -> List[int]:
        # Supports patterns like: 18.490.000, 18,490,000, 18490000
        matches = re.findall(
            r"(\d{1,3}(?:[.,]\d{3}){1,4}|\d{6,10})\s*(?:₫|vnd|đ)?",
            text.lower(),
        )
        prices: List[int] = []
        for token in matches:
            number = token.replace(".", "").replace(",", "")
            if not number.isdigit():
                continue
            value = int(number)
            # Plausible retail price range in VND for this lab's products.
            if 100_000 <= value <= 500_000_000:
                prices.append(value)
        return prices

    @staticmethod
    def extract_structured_prices_from_html(html: str) -> List[int]:
        patterns = [
            r'itemprop=["\']price["\'][^>]*content=["\']([\d.,]+)["\']',
            r'"price"\s*:\s*"([\d.,]+)"',
            r'"price"\s*:\s*([\d.,]+)',
            r'data-price=["\']([\d.,]+)["\']',
        ]
        raw: List[str] = []
        for pattern in patterns:
            raw.extend(re.findall(pattern, html, flags=re.IGNORECASE))

        prices: List[int] = []
        for token in raw:
            cleaned = token.replace(".", "").replace(",", "")
            if cleaned.isdigit():
                prices.append(int(cleaned))
        return prices

    @staticmethod
    def first_result_for_domain(results: List[Dict[str, str]], domain: str) -> Optional[Dict[str, str]]:
        for item in results:
            if domain in item.get("link", ""):
                return item
        return results[0] if results else None
