from typing import Any, Dict, List

from src.agent.agent import ReActAgent
from src.telemetry.logger import logger


class ReActAgentV2(ReActAgent):
    """Improved Agent v2 with stronger tool-use constraints and recovery."""

    def __init__(self, llm, tools: List[Dict[str, Any]], max_steps: int = 8):
        super().__init__(llm=llm, tools=tools, max_steps=max_steps)

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return (
            "You are ReActAgent v2. Be reliable, concise, and tool-grounded.\n\n"
            "Available tools:\n"
            f"{tool_descriptions}\n\n"
            "Strict policy:\n"
            "0) Only handle e-commerce shopping requests (product recommendation, pricing, stock, discount, shipping, total-cost calculations).\n"
            "   If the request is outside e-commerce shopping domain, respond with Final Answer and politely refuse.\n"
            "1) Use at most ONE tool call per step.\n"
            "2) If an Observation contains an error or missing data, adapt arguments and retry.\n"
            "3) Do not switch to unrelated products to continue the flow.\n"
            "4) Prefer calculation with calculator after collecting numeric facts.\n"
            "5) Stop only with: Final Answer: <answer with assumptions clearly stated>\n"
            "6) For web_search, use short queries (2-8 words), avoid long URL-in-query prompts.\n\n"
            "Output format:\n"
            "Thought: <brief reason>\n"
            "Action: tool_name(arguments)\n"
            "OR\n"
            "Final Answer: <final response>"
        )

    def run(self, user_input: str) -> str:
        if not self._is_in_domain(user_input):
            refusal = (
                "Xin loi, toi chi ho tro cac cau hoi thuoc chu de e-commerce "
                "(goi y san pham, so sanh gia, ton kho, giam gia, van chuyen, tinh tong chi phi). "
                "Ban hay dat cau hoi mua sam (vd: laptop, iphone, phu kien...) de minh ho tro."
            )
            logger.log_event(
                "OUT_OF_DOMAIN_BLOCK",
                {"input": user_input, "reason": "outside_ecommerce_scope"},
            )
            return refusal

        answer = super().run(user_input)
        if "I could not complete the task within max steps" in answer:
            logger.log_event(
                "V2_RECOVERY_HINT",
                {
                    "hint": (
                        "Increase max_steps, narrow tool scope, and improve tool data coverage "
                        "for requested products."
                    )
                },
            )
        return answer

    @staticmethod
    def _is_in_domain(user_input: str) -> bool:
        text = user_input.lower()

        # Must mention at least one shopping intent word.
        intent_keywords = [
            "buy",
            "purchase",
            "recommend",
            "suggest",
            "shop",
            "price",
            "pricing",
            "discount",
            "coupon",
            "stock",
            "shipping",
            "compare",
            "cost",
            "e-commerce",
            "mua",
            "gia",
            "khuyen mai",
            "giam gia",
            "ton kho",
            "van chuyen",
            "so sanh",
            "goi y",
            "dat mua",
        ]
        has_intent = any(k in text for k in intent_keywords)

        # Should mention a product-ish term to avoid broad unrelated requests.
        product_keywords = [
            "laptop",
            "iphone",
            "phone",
            "smartphone",
            "macbook",
            "tablet",
            "headphone",
            "keyboard",
            "mouse",
            "monitor",
            "camera",
            "switch",
            "nintendo",
            "product",
            "san pham",
            "dien thoai",
            "tai nghe",
            "ban phim",
            "man hinh",
            "chuot",
            "may tinh",
        ]
        has_product = any(k in text for k in product_keywords)

        return has_intent and has_product
