import os
from dotenv import load_dotenv


def build_provider():
    provider = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    default_model = os.getenv("DEFAULT_MODEL", "").strip()

    if provider == "openai":
        from src.core.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model_name=default_model or "gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider in {"google", "gemini"}:
        from src.core.gemini_provider import GeminiProvider

        return GeminiProvider(
            model_name=default_model or "gemini-1.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    if provider == "local":
        from src.core.local_provider import LocalProvider

        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)

    raise ValueError("DEFAULT_PROVIDER must be one of: openai | google | local")


def run_demo():
    load_dotenv()
    llm = build_provider()

    print("=== Phase 01: Chatbot Baseline (No Tools) ===")
    print(f"Provider model: {llm.model_name}")
    print("Type 'exit' to stop.\n")

    default_prompt = (
        "Find the cheapest price of iPhone 15 from 3 stores, then calculate total "
        "cost for 2 units with 10% tax. Show your sources."
    )

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            user_input = default_prompt
            print(f"(Using demo prompt) {user_input}")

        system_prompt = (
            "You are a helpful chatbot. Answer directly with your best guess. "
            "You do not have external tools."
        )

        result = llm.generate(user_input, system_prompt=system_prompt)
        print(f"\nAssistant:\n{result['content']}\n")
        print(
            f"[usage] prompt={result['usage'].get('prompt_tokens', 0)} "
            f"completion={result['usage'].get('completion_tokens', 0)} "
            f"latency_ms={result.get('latency_ms', 0)}\n"
        )


if __name__ == "__main__":
    run_demo()
