from datetime import datetime

from dotenv import load_dotenv

from chatbot import build_provider
from src.agent.agent_v2 import ReActAgentV2
from src.telemetry.logger import logger
from src.tools.registry import build_registry


def main() -> None:
    load_dotenv()
    logger.set_console_quiet(True)
    llm = build_provider()
    registry = build_registry()
    agent = ReActAgentV2(llm=llm, tools=registry.as_agent_tools(), max_steps=8)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    question_idx = 1
    history = []

    print("=== Agent v2 Chat ===")
    print(f"Provider model: {llm.model_name}")
    print("Type 'exit' to stop, 'reset' to clear conversation.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if user_input.lower() == "reset":
            history = []
            question_idx = 1
            print("Conversation memory reset.\n")
            continue
        if not user_input:
            continue

        history.append(f"User: {user_input}")
        context_prompt = (
            "Continue the same conversation using previous turns as context.\n\n"
            + "\n".join(history)
        )

        question_id = f"question_{question_idx}"
        logger.set_context(run_id=run_id, question_id=question_id)
        print("Dang suy nghi...")
        answer = agent.run(context_prompt)
        logger.clear_context()

        history.append(f"Agent: {answer}")
        print(f"\nAgent:\n{answer}\n")
        question_idx += 1


if __name__ == "__main__":
    main()
