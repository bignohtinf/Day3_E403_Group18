from src.tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    """Evaluate simple math expressions for totals/taxes."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description=(
                "Evaluate a basic math expression with numbers and operators (+, -, *, /, parentheses). "
                "Input should be a single expression string, e.g. '(1200*2)*1.1'."
            ),
        )

    def execute(self, query: str) -> str:
        expression = query.strip()
        if not expression:
            return "Error: provide a math expression."

        allowed_chars = set("0123456789.+-*/() ")
        if any(ch not in allowed_chars for ch in expression):
            return "Error: expression contains unsupported characters."

        try:
            value = eval(expression, {"__builtins__": {}}, {})
            return f"{value}"
        except Exception as exc:
            return f"Error evaluating expression: {exc}"
