from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    text: str
    provider_name: str
    command: list[str]
    stdout: str = ""
    stderr: str = ""
    requested_provider: str = "gemini"
    used_fallback: bool = False
    fallback_reason: str = ""
    warnings: list[str] = field(default_factory=list)


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot generate a valid response."""


class LLMProvider(ABC):
    name = "base"

    @abstractmethod
    def generate(self, prompt: str) -> GenerationResult:
        """Generate text from a prompt."""
