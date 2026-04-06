from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Base interface for all lab tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, query: str) -> str:
        """Run tool logic and return a string observation."""
        raise NotImplementedError

    def to_spec(self) -> dict:
        """Export tool metadata for agent prompts."""
        return {"name": self.name, "description": self.description}
