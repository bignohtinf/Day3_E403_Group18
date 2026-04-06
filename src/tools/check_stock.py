from src.tools.base_tool import BaseTool


class CheckStockTool(BaseTool):
    """Return available stock quantity by product."""

    def __init__(self):
        super().__init__(
            name="check_stock",
            description=(
                "Check available stock for a product across stores. "
                "Input: product name, e.g. 'iphone 15'."
            ),
        )
        self._inventory = {
            "iphone 15": {"Store A": 4, "Store B": 10, "Store C": 0},
            "macbook air m3": {"Store A": 2, "Store B": 0, "Store C": 3},
            "mechanical keyboard": {"Store A": 30, "Store B": 12, "Store C": 8},
            "mouse": {"Store A": 50, "Store B": 20, "Store C": 15},
        }

    def execute(self, query: str) -> str:
        product = query.strip().lower()
        if not product:
            return "Error: provide a product name."

        stock = self._inventory.get(product)
        if not stock:
            supported = ", ".join(sorted(self._inventory.keys()))
            return f"No stock data for '{product}'. Supported products: {supported}."

        lines = [f"Stock for '{product}':"]
        for store, qty in stock.items():
            lines.append(f"- {store}: {qty} units")
        return "\n".join(lines)
