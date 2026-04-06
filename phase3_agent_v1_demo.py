from dotenv import load_dotenv

from chatbot import build_provider
from src.agent.agent import ReActAgent
from src.tools.registry import build_registry


def main() -> None:
    load_dotenv()
    llm = build_provider()
    registry = build_registry()
    agent = ReActAgent(llm=llm, tools=registry.as_agent_tools(), max_steps=5)

    print("=== Phase 3: ReAct Agent v1 Demo ===")
    print(f"Provider model: {llm.model_name}")
    print(f"Tools: {', '.join(registry.names())}")
    print("Type 'exit' to stop.\n")

    default_prompt = (
        "I want to buy 2 iPhones using code WINNER and ship to Hanoi. "
        "Find data using tools and compute final total with tax."
    )

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            user_input = default_prompt
            print(f"(Using demo prompt) {user_input}")

        answer = agent.run(user_input)
        print(f"\nAgent:\n{answer}\n")


if __name__ == "__main__":
    main()
