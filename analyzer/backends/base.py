from abc import ABC, abstractmethod


class LLMBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from a prompt. Returns the generated text."""
        ...
