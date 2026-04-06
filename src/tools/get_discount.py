from src.tools.base_tool import BaseTool
import re

from src.tools.demo_data import DEMO_DISCOUNTS
from src.tools.live_search_utils import LiveSearchUtils


class GetDiscountTool(BaseTool):
    """Find live coupon references and discount percentages."""

    def __init__(self):
        super().__init__(
            name="get_discount",
            description=(
                "Find live discount info for a coupon code from web results. "
                "Input: coupon code string, e.g. 'WINNER'."
            ),
        )

    def execute(self, query: str) -> str:
        code = query.strip().upper()
        if not code:
            return "Error: provide a coupon code."

        try:
            results = LiveSearchUtils.search(f"{code} coupon discount Vietnam", max_results=5)
        except Exception as exc:
            if code in DEMO_DISCOUNTS:
                return f"Demo discount for '{code}': {DEMO_DISCOUNTS[code]}% (fallback data)."
            return f"Error fetching live discount info: {exc}"

        lines = [f"Live discount references for coupon '{code}':"]
        best_percent = None

        for item in results[:3]:
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            percents = re.findall(r"(\d{1,2})\s*%", text)
            percent = max((int(p) for p in percents), default=None)
            if percent is not None:
                best_percent = max(best_percent or 0, percent)
                lines.append(f"- {percent}% (source: {item.get('link', 'N/A')})")
            else:
                lines.append(f"- no explicit % found (source: {item.get('link', 'N/A')})")

        if best_percent is None:
            if code in DEMO_DISCOUNTS:
                lines.append(f"Conclusion: fallback demo discount = {DEMO_DISCOUNTS[code]}%.")
            else:
                lines.append("Conclusion: no verifiable live percentage found.")
        else:
            lines.append(f"Conclusion: highest observed live discount = {best_percent}%.")
        return "\n".join(lines)
