from src.tools.base_tool import BaseTool


class GetDiscountTool(BaseTool):
    """Return discount percentage from coupon code."""

    def __init__(self):
        super().__init__(
            name="get_discount",
            description=(
                "Get discount percentage for a coupon code. "
                "Input: coupon code string, e.g. 'WINNER'."
            ),
        )
        self._coupons = {
            "WINNER": 0.12,
            "STUDENT10": 0.10,
            "SHIPFREE": 0.00,
            "SPRING5": 0.05,
        }

    def execute(self, query: str) -> str:
        code = query.strip().upper()
        if not code:
            return "Error: provide a coupon code."

        discount = self._coupons.get(code, 0.0)
        percent = int(discount * 100)
        if discount == 0.0 and code not in self._coupons:
            return f"Coupon '{code}' is invalid. Discount: 0%."
        return f"Coupon '{code}' discount: {percent}%."
