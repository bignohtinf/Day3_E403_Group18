import json
import os

import requests
from src.tools.base_tool import BaseTool


class CalcShippingTool(BaseTool):
    """Calculate shipping via live GHN API (requires env config)."""

    def __init__(self):
        super().__init__(
            name="calc_shipping",
            description=(
                "Calculate live shipping fee with GHN API. "
                "Input format: '<weight_kg>, <destination>' (destination city mapped by env)."
            ),
        )
        self._api_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee"
        self._demo_zone_fee = {
            "hanoi": 25000,
            "ho chi minh city": 30000,
            "da nang": 35000,
            "can tho": 38000,
        }

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

        token = os.getenv("GHN_API_TOKEN")
        shop_id = os.getenv("GHN_SHOP_ID")
        from_district_id = os.getenv("GHN_FROM_DISTRICT_ID")
        raw_map = os.getenv("GHN_TO_DISTRICT_MAP", "{}")

        if not token or not shop_id or not from_district_id:
            return self._demo_shipping(weight_kg, destination_text)

        try:
            to_map = json.loads(raw_map)
        except json.JSONDecodeError:
            return "Error: GHN_TO_DISTRICT_MAP must be valid JSON object."

        destination_key = destination_text.strip().lower()
        to_district_id = to_map.get(destination_key)
        if not to_district_id:
            return (
                f"Error: destination '{destination_text}' not found in GHN_TO_DISTRICT_MAP. "
                "Example: {\"hanoi\": 1454, \"da nang\": 1563}"
            )

        payload = {
            "service_type_id": 2,
            "from_district_id": int(from_district_id),
            "to_district_id": int(to_district_id),
            "weight": int(weight_kg * 1000),
            "length": 20,
            "width": 20,
            "height": 10,
            "insurance_value": 0,
            "coupon": None,
        }
        headers = {"Token": token, "ShopId": str(shop_id)}

        try:
            response = requests.post(self._api_url, json=payload, headers=headers, timeout=12)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return f"Live API failed ({exc}). {self._demo_shipping(weight_kg, destination_text)}"

        if data.get("code") != 200:
            return f"GHN API error: {data}"

        fee = data.get("data", {}).get("total")
        if fee is None:
            return f"GHN API response missing total fee: {data}"

        return (
            f"Live shipping to {destination_text}: {fee} VND "
            f"(weight={int(weight_kg * 1000)}g, provider=GHN)."
        )

    def _demo_shipping(self, weight_kg: float, destination_text: str) -> str:
        dest = destination_text.strip().lower()
        zone_fee = self._demo_zone_fee.get(dest, 45000)
        base_fee = 15000
        per_kg = 12000
        total = base_fee + int(weight_kg * per_kg) + zone_fee
        return (
            f"Demo shipping to {destination_text}: {total} VND "
            f"(fallback data; base={base_fee}, weight_fee={int(weight_kg * per_kg)}, zone_fee={zone_fee})."
        )
