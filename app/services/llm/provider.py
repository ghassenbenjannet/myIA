from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'stub', 'anthropic/claude-opus-4-6')."""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Whether the provider is configured and usable."""
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        workflow: str | None = None,
    ) -> str:
        """Generate a completion.

        Args:
            prompt: User-facing prompt (already rendered from template).
            system: Optional system-level instruction.
            workflow: Optional hint for stub providers ('analysis', 'ticket', 'documentation').

        Returns:
            Raw text response from the model (usually JSON for structured workflows).
        """
        ...
