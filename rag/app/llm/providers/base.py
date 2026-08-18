from abc import ABC, abstractmethod
from collections.abc import Iterator


class LLMProvider(ABC):
    name = "base"

    @abstractmethod
    def generate(self, messages: list[dict], model: str | None = None) -> Iterator[str]:
        """Stream text tokens for a chat message list."""

    @abstractmethod
    def complete(self, messages: list[dict], model: str | None = None, *, json_mode: bool = False) -> str:
        """Non-streaming completion (structured extraction, verification)."""