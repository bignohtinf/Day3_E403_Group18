from src.tools.base_tool import BaseTool


class PriceLookupTool(BaseTool):
    """Mock store price lookup for lab demos."""

    def __init__(self):
        super().__init__(
            name="price_lookup",
            description=(
                "Return mock prices for a product across stores. "
                "Input is product name, e.g. 'iphone 15'."
            ),
        )
        self._catalog = {
            "iphone 15": {
                "Store A": 18990000,
                "Store B": 18450000,
                "Store C": 19200000,
            },
            "macbook air m3": {
                "Store A": 28990000,
                "Store B": 27990000,
                "Store C": 29500000,
            },
        }

    def execute(self, query: str) -> str:
        product = query.strip().lower()
        if not product:
            return "Error: provide a product name."

        prices = self._catalog.get(product)
        if not prices:
            supported = ", ".join(sorted(self._catalog.keys()))
            return f"No mock data for '{product}'. Supported products: {supported}."

        lines = [f"Prices for '{product}':"]
        for store, amount in prices.items():
            lines.append(f"- {store}: {amount} VND")
        return "\n".join(lines)
