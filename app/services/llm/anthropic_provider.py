from __future__ import annotations

from typing import TYPE_CHECKING

from app.services.llm.provider import LLMProvider

if TYPE_CHECKING:
    from anthropic import Anthropic as _AnthropicClient


class AnthropicLLMProvider(LLMProvider):
    """Anthropic Claude provider.

    Lazy-imports the `anthropic` SDK so the rest of the app can start
    even if the package is not installed (e.g. LLM_ENABLED=false).
    """

    DEFAULT_MODEL = "claude-opus-4-6"
    MAX_TOKENS = 4096

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model or self.DEFAULT_MODEL
        self._client: _AnthropicClient | None = None

    @property
    def name(self) -> str:
        return f"anthropic/{self._model}"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def _get_client(self) -> _AnthropicClient:
        if self._client is None:
            from anthropic import Anthropic  # type: ignore[import]

            self._client = Anthropic(api_key=self._api_key)
        return self._client

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        workflow: str | None = None,
    ) -> str:
        client = self._get_client()
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self.MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

        message = client.messages.create(**kwargs)
        return message.content[0].text  # type: ignore[index]
