from src.tools.base_tool import BaseTool
from src.tools.demo_data import DEMO_STOCK
from src.tools.live_search_utils import LiveSearchUtils


class CheckStockTool(BaseTool):
    """Infer live stock status from store product pages."""

    def __init__(self):
        super().__init__(
            name="check_stock",
            description=(
                "Check live stock status from real store product pages "
                "(in_stock / out_of_stock / unknown)."
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
        self._in_stock_keywords = ["còn hàng", "in stock", "available", "còn tại cửa hàng"]
        self._out_stock_keywords = ["hết hàng", "out of stock", "tạm hết hàng", "ngừng kinh doanh"]

    def execute(self, query: str) -> str:
        product = query.strip().lower()
        if not product:
            return "Error: provide a product name."

        stores = self._product_urls.get(product)
        if not stores:
            demo = DEMO_STOCK.get(product)
            if demo:
                return self._format_demo_stock(product, demo)
            supported = ", ".join(sorted(set(self._product_urls.keys()) | set(DEMO_STOCK.keys())))
            return f"Error: unsupported product '{product}'. Supported products: {supported}."

        lines = [f"Live stock status for '{product}' (from store pages):"]
        for store_name, url in stores.items():
            try:
                status = "unknown"
                try:
                    page_text = LiveSearchUtils.fetch_text(url).lower()[:50000]
                except Exception:
                    lines.append(f"- {store_name}: page fetch failed ({url})")
                    continue

                if any(word in page_text for word in self._out_stock_keywords):
                    status = "out_of_stock"
                elif any(word in page_text for word in self._in_stock_keywords):
                    status = "in_stock"

                lines.append(f"- {store_name}: {status} (source: {url})")
            except Exception as exc:
                lines.append(f"- {store_name}: lookup error ({exc})")
        # If all stores unknown/failed, use demo fallback if available.
        has_signal = any(("in_stock" in x) or ("out_of_stock" in x) for x in lines)
        if not has_signal and product in DEMO_STOCK:
            return self._format_demo_stock(product, DEMO_STOCK[product])
        return "\n".join(lines)

    @staticmethod
    def _format_demo_stock(product: str, stock: dict) -> str:
        lines = [f"Demo stock status for '{product}' (fallback data):"]
        for store, status in stock.items():
            lines.append(f"- {store}: {status}")
        return "\n".join(lines)
