import importlib
import inspect
import pkgutil
from typing import Dict, List

from src.tools.base_tool import BaseTool
import src.tools as tools_pkg


class ToolRegistry:
    """Discover, store, and execute tools from src.tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def discover(self) -> "ToolRegistry":
        skip_modules = {"base_tool", "registry", "__init__"}

        for module_info in pkgutil.iter_modules(tools_pkg.__path__):
            module_name = module_info.name
            if module_name in skip_modules:
                continue

            module = importlib.import_module(f"src.tools.{module_name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj is BaseTool:
                    continue
                if issubclass(obj, BaseTool):
                    tool = obj()
                    self._tools[tool.name] = tool

        return self

    def list_specs(self) -> List[dict]:
        return [tool.to_spec() for tool in self._tools.values()]

    def execute(self, tool_name: str, args: str) -> str:
        tool = self._tools.get(tool_name)
        if not tool:
            return f"Tool '{tool_name}' not found."
        return tool.execute(args)

    def names(self) -> List[str]:
        return sorted(self._tools.keys())


def build_registry() -> ToolRegistry:
    return ToolRegistry().discover()
