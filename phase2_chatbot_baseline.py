import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from chatbot import build_provider


TEST_CASES: List[Dict[str, str]] = [
    {
        "id": "case_01_price_tax",
        "prompt": (
            "Find the cheapest price of iPhone 15 from 3 stores in Vietnam, then calculate "
            "total cost for 2 units with 10% tax. Show exact store names and source links."
        ),
        "failure_signal": "Likely hallucinates store prices or sources.",
    },
    {
        "id": "case_02_shipping_discount",
        "prompt": (
            "I want to buy 2 iPhones using code WINNER and ship to Hanoi. "
            "Compute final total: item price + shipping - discount. Show each step."
        ),
        "failure_signal": "No real shipping API/tool call; numbers are guessed.",
    },
    {
        "id": "case_03_stock_then_total",
        "prompt": (
            "Check if MacBook Air M3 is in stock in 3 stores, pick the cheapest available one, "
            "then calculate total for 3 units including VAT 8%."
        ),
        "failure_signal": "Cannot verify real stock status without tools.",
    },
    {
        "id": "case_04_fx_import_tax",
        "prompt": (
            "Compare Nintendo Switch OLED prices from Amazon US, Rakuten Japan, and a Vietnam store. "
            "Convert all prices to VND using today's exchange rates, add 5% import tax and 10% VAT, "
            "then tell me the cheapest final option with source links."
        ),
        "failure_signal": "Exchange rates and source links are often fabricated without external tools.",
    },
    {
        "id": "case_05_bundle_inventory_plan",
        "prompt": (
            "Plan a purchase for a coding club: 12 mechanical keyboards and 12 mice. "
            "Use 3 stores, ensure each store has enough stock, apply any bulk discount rules, "
            "include shipping to Da Nang, and output the cheapest valid purchasing plan."
        ),
        "failure_signal": "Cannot reliably verify stock/discount/shipping constraints in one shot.",
    },
]


def run_phase2() -> None:
    load_dotenv()
    llm = build_provider()
    output_dir = Path("logs")
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"phase2_chatbot_baseline_{run_id}.json"

    print("=== Phase 2: Chatbot Baseline Evaluation ===")
    print(f"Model: {llm.model_name}")
    print(f"Saving outputs to: {output_file}\n")

    all_results = []
    system_prompt = (
        "You are a helpful chatbot. Answer directly with your best guess. "
        "You do not have external tools, APIs, or web browsing."
    )

    for idx, case in enumerate(TEST_CASES, start=1):
        print(f"[{idx}/{len(TEST_CASES)}] {case['id']}")
        print(f"Prompt: {case['prompt']}")

        result = llm.generate(case["prompt"], system_prompt=system_prompt)
        content = result.get("content", "")
        usage = result.get("usage", {})

        print("Assistant output:")
        print(content)
        print(
            f"[usage] prompt={usage.get('prompt_tokens', 0)} "
            f"completion={usage.get('completion_tokens', 0)} "
            f"latency_ms={result.get('latency_ms', 0)}"
        )
        print(f"Expected failure signal: {case['failure_signal']}\n")

        all_results.append(
            {
                "case_id": case["id"],
                "prompt": case["prompt"],
                "failure_signal": case["failure_signal"],
                "response": content,
                "usage": usage,
                "latency_ms": result.get("latency_ms", 0),
                "provider": result.get("provider", "unknown"),
                "model": llm.model_name,
            }
        )

    output_payload = {
        "run_id": run_id,
        "mode": "chatbot_baseline_no_tools",
        "results": all_results,
    }

    output_file.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Done. Review the saved JSON and highlight hallucinations/missing verifiability in class.")


if __name__ == "__main__":
    run_phase2()
