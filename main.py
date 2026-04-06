from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.tools.tool_registry import get_tools

if __name__ == "__main__":
    llm = LocalProvider(model_path="models/Phi-3-mini-4k-instruct-q4.gguf")
    tools = get_tools()
    agent = ReActAgent(llm, tools)
    while True:
        user_input = input("You: ")
        response = agent.run(user_input)
        print("Assistant: ", response)
        