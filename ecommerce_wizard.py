from datetime import datetime
from typing import List, Dict

import gradio as gr
from dotenv import load_dotenv

from chatbot import build_provider
from src.agent.agent_v2 import ReActAgentV2
from src.telemetry.logger import logger
from src.tools.registry import build_registry


load_dotenv()
logger.set_console_quiet(True)

_llm = build_provider()
_registry = build_registry()
_agent = ReActAgentV2(llm=_llm, tools=_registry.as_agent_tools(), max_steps=8)


def _build_context(history: List[Dict[str, str]], user_message: str) -> str:
    lines = ["Continue the same e-commerce conversation with context.\n"]
    pending_user = None
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            pending_user = content
        elif role == "assistant":
            if pending_user is not None:
                lines.append(f"User: {pending_user}")
                pending_user = None
            lines.append(f"Agent: {content}")
    if pending_user is not None:
        lines.append(f"User: {pending_user}")
    lines.append(f"User: {user_message}")
    return "\n".join(lines)


def chat_fn(
    user_message: str,
    history: List[Dict[str, str]],
    run_id: str,
    question_idx: int,
):
    user_message = (user_message or "").strip()
    if not user_message:
        return history, run_id, question_idx, ""

    context_prompt = _build_context(history, user_message)
    question_id = f"question_{question_idx}"

    logger.set_context(run_id=run_id, question_id=question_id)
    answer = _agent.run(context_prompt)
    logger.clear_context()

    history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]
    return history, run_id, question_idx + 1, ""


def reset_chat():
    new_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return [], new_run_id, 1, ""


with gr.Blocks(title="E-commerce Wizard") as demo:
    gr.Markdown(
        "## E-commerce Wizard\n"
    )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversation",
                height=520,
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Vi du: Tim gia iPhone 15 re nhat va tinh tong chi phi cho 2 may.",
                    lines=3,
                )
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("New Conversation")

        with gr.Column(scale=1):
            gr.Markdown(
                "### Agent\n"
                f"- Model: `{_llm.model_name}`\n"
                f"- Max steps: `{_agent.max_steps}`\n"
                f"- Tools: `{', '.join(_registry.names())}`\n\n"

                
            )

    run_state = gr.State(datetime.now().strftime("%Y%m%d_%H%M%S"))
    idx_state = gr.State(1)

    send_btn.click(
        fn=chat_fn,
        inputs=[msg, chatbot, run_state, idx_state],
        outputs=[chatbot, run_state, idx_state, msg],
    )
    msg.submit(
        fn=chat_fn,
        inputs=[msg, chatbot, run_state, idx_state],
        outputs=[chatbot, run_state, idx_state, msg],
    )
    clear_btn.click(
        fn=reset_chat,
        inputs=[],
        outputs=[chatbot, run_state, idx_state, msg],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
