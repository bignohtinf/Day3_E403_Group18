from src.tools.base_tool import BaseTool


class CalcShippingTool(BaseTool):
    """Calculate shipping cost using weight and destination."""

    def __init__(self):
        super().__init__(
            name="calc_shipping",
            description=(
                "Calculate shipping cost by weight and destination city. "
                "Input format: '<weight_kg>, <destination>', e.g. '2.5, Hanoi'."
            ),
        )
        self._destination_fee = {
            "hanoi": 25000,
            "ho chi minh city": 30000,
            "da nang": 35000,
            "can tho": 38000,
        }
        self._base_fee = 15000
        self._fee_per_kg = 12000

    def execute(self, query: str) -> str:
        raw = query.strip()
        if "," not in raw:
            return "Error: use '<weight_kg>, <destination>' format."

        weight_text, destination_text = [part.strip() for part in raw.split(",", 1)]
        try:
            weight_kg = float(weight_text)
        except ValueError:
            return "Error: weight must be a number."

        if weight_kg <= 0:
            return "Error: weight must be greater than 0."

        destination_key = destination_text.lower()
        zone_fee = self._destination_fee.get(destination_key, 45000)
        total = self._base_fee + int(weight_kg * self._fee_per_kg) + zone_fee

        return (
            f"Shipping to {destination_text}: {total} VND "
            f"(base={self._base_fee}, weight_fee={int(weight_kg * self._fee_per_kg)}, zone_fee={zone_fee})."
        )
