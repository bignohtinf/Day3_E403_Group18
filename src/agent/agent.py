import json
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """Build instructions for a strict ReAct loop."""
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return (
            "You are a ReAct agent. Solve tasks step-by-step using tools when needed.\n\n"
            "Available tools:\n"
            f"{tool_descriptions}\n\n"
            "Rules:\n"
            "1) If you need external information/calculation, choose one tool per step.\n"
            "2) Use EXACT action format: Action: tool_name(arguments)\n"
            "3) After seeing Observation, continue reasoning.\n"
            "4) When complete, output: Final Answer: <answer>\n"
            "5) Do not invent tool results.\n\n"
            "Output format:\n"
            "Thought: <reasoning>\n"
            "Action: <tool_name(arguments)> OR Final Answer: <answer>"
        )

    def run(self, user_input: str) -> str:
        """Run the ReAct loop until final answer or max step timeout."""
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        self.history = [f"User: {user_input}"]
        system_prompt = self.get_system_prompt()

        for step in range(1, self.max_steps + 1):
            prompt = "\n".join(self.history)
            result = self.llm.generate(prompt, system_prompt=system_prompt)
            content = (result.get("content") or "").strip()

            tracker.track_request(
                provider=result.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0),
            )
            logger.log_event("AGENT_STEP", {"step": step, "output": content})

            if content:
                self.history.append(content)

            final_answer = self._extract_final_answer(content)
            if final_answer:
                logger.log_event("AGENT_END", {"steps": step, "status": "success"})
                return final_answer

            # Graceful fallback only for very short small-talk responses.
            # Do not end early for task-oriented requests that still need tool execution.
            if self._is_smalltalk_response(content):
                logger.log_event("AGENT_END", {"steps": step, "status": "direct_response"})
                return content

            parsed = self._parse_action(content)
            if not parsed:
                observation = (
                    "Could not parse Action. Use format: Action: tool_name(arguments) "
                    "or return Final Answer."
                )
                self.history.append(f"Observation: {observation}")
                logger.log_event("PARSER_ERROR", {"step": step, "output": content})
                continue

            tool_name, args = parsed
            tool_result = self._execute_tool(tool_name, args)
            self.history.append(f"Observation: {tool_result}")
            logger.log_event(
                "TOOL_CALL",
                {"step": step, "tool": tool_name, "args": args, "result": tool_result},
            )

        logger.log_event("AGENT_END", {"steps": self.max_steps, "status": "max_steps_reached"})
        return "I could not complete the task within max steps. Please refine the question."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """Execute a tool by name.

        Supported tool definitions:
        - {'name': 'x', 'executor': callable_or_object}
        - {'name': 'x', 'func': callable}
        - {'name': 'x', 'tool': object_with_execute}
        """
        for tool in self.tools:
            if tool.get("name") != tool_name:
                continue

            candidate = (
                tool.get("executor")
                or tool.get("func")
                or tool.get("callable")
                or tool.get("tool")
            )

            if candidate is None:
                return f"Tool '{tool_name}' is configured without an executor."

            try:
                if hasattr(candidate, "execute"):
                    return str(candidate.execute(args))
                if callable(candidate):
                    return str(candidate(args))
                return f"Tool '{tool_name}' executor is not callable."
            except Exception as exc:
                return f"Tool '{tool_name}' error: {exc}"

        return f"Tool {tool_name} not found."

    def _parse_action(self, text: str) -> Optional[tuple[str, str]]:
        """Parse action from either function-call style or JSON style."""
        func_style = re.search(r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)\s*$", text, re.DOTALL)
        if func_style:
            tool_name = func_style.group(1).strip()
            args = func_style.group(2).strip()
            return tool_name, self._strip_quotes(args)

        json_style = re.search(r"Action:\s*(\{.*?\})", text, re.DOTALL)
        if json_style:
            try:
                payload = json.loads(json_style.group(1))
                tool_name = str(payload.get("tool", "")).strip()
                args = str(payload.get("args", "")).strip()
                if tool_name:
                    return tool_name, args
            except json.JSONDecodeError:
                return None

        return None

    @staticmethod
    def _extract_final_answer(text: str) -> Optional[str]:
        match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
        if not match:
            return None
        return match.group(1).strip() or None

    @staticmethod
    def _strip_quotes(value: str) -> str:
        stripped = value.strip()
        if (stripped.startswith('"') and stripped.endswith('"')) or (
            stripped.startswith("'") and stripped.endswith("'")
        ):
            return stripped[1:-1]
        return stripped

    @staticmethod
    def _is_smalltalk_response(text: str) -> bool:
        lower = text.lower()
        has_react_markers = any(marker in lower for marker in ["thought:", "action:", "observation:"])
        if has_react_markers:
            return False
        if not text.strip():
            return False

        # If the model mentions a plan/step, it's task-oriented, not small-talk.
        tasky_markers = [
            "i'll",
            "i will",
            "first",
            "next",
            "calculate",
            "check",
            "search",
            "tool",
            "gia",
            "mua",
            "so sanh",
            "shipping",
            "discount",
            "coupon",
        ]
        if any(token in lower for token in tasky_markers):
            return False

        # Small-talk/greeting intents only.
        smalltalk_markers = [
            "hello",
            "hi",
            "hey",
            "xin chao",
            "chao",
            "ban la ai",
            "bạn là ai",
            "how are you",
        ]
        is_short = len(lower) <= 220
        return is_short and any(token in lower for token in smalltalk_markers)
