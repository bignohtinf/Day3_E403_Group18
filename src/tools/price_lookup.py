from src.tools.base_tool import BaseTool
from src.tools.demo_data import DEMO_PRICES
from src.tools.live_search_utils import LiveSearchUtils


class PriceLookupTool(BaseTool):
    """Live web-based store price lookup."""

    def __init__(self):
        super().__init__(
            name="price_lookup",
            description=(
                "Find live product prices from real store pages and return source links. "
                "Input: product name (currently supports mapped products like 'iphone 15')."
            ),
        )
        self._product_urls = {
            "iphone 15": {
                "CellphoneS": "https://cellphones.com.vn/mobile/apple/iphone-15.html",
                "FPT Shop": "https://fptshop.com.vn/dien-thoai/iphone-15",
                "Viettel Store": "https://viettelstore.vn/dtdd/apple/iphone-15",
            },
            "macbook air m3": {
                "CellphoneS": "https://cellphones.com.vn/laptop/macbook-air-m3.html",
                "FPT Shop": "https://fptshop.com.vn/may-tinh-xach-tay/macbook-air-m3-13-inch-8gb-256gb",
                "Viettel Store": "https://viettelstore.vn/laptop/macbook-air-m3",
            },
        }

    def execute(self, query: str) -> str:
        product = query.strip().lower()
        if not product:
            return "Error: provide a product name."

        stores = self._product_urls.get(product)
        if not stores:
            demo = DEMO_PRICES.get(product)
            if demo:
                return self._format_demo_prices(product, demo)
            supported = ", ".join(sorted(set(self._product_urls.keys()) | set(DEMO_PRICES.keys())))
            return f"Error: unsupported product '{product}'. Supported products: {supported}."

        lines = [f"Live prices for '{product}' (from store pages):"]
        found_any = False
        min_price, max_price = self._price_range(product)

        for store_name, url in stores.items():
            try:
                page_html = LiveSearchUtils.fetch_html(url)
                structured = LiveSearchUtils.extract_structured_prices_from_html(page_html)
                page_text = LiveSearchUtils.fetch_text(url)
                text_prices = LiveSearchUtils.extract_vnd_prices(page_text[:40000])

                candidate_prices = structured or text_prices
                candidate_prices = [p for p in candidate_prices if min_price <= p <= max_price]
                if not candidate_prices:
                    lines.append(f"- {store_name}: page fetched but no parsable price ({url})")
                    continue

                best_price = min(candidate_prices)
                found_any = True
                lines.append(f"- {store_name}: {best_price} VND (source: {url})")
            except Exception as exc:
                lines.append(f"- {store_name}: lookup error ({exc})")

        if not found_any:
            demo = DEMO_PRICES.get(product)
            if demo:
                return self._format_demo_prices(product, demo)
            return (
                "No live price could be parsed from current web results. "
                "Try a more specific query like 'iphone 15 128gb'.\n" + "\n".join(lines)
            )
        return "\n".join(lines)

    @staticmethod
    def _price_range(product: str) -> tuple[int, int]:
        if "iphone" in product:
            return 5_000_000, 60_000_000
        if "macbook" in product:
            return 10_000_000, 120_000_000
        return 500_000, 200_000_000

    @staticmethod
    def _format_demo_prices(product: str, prices: dict) -> str:
        lines = [f"Demo prices for '{product}' (fallback data):"]
        for store, amount in prices.items():
            lines.append(f"- {store}: {amount} VND")
        return "\n".join(lines)
