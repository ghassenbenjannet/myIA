from app.services.llm.provider import LLMProvider
from app.services.llm.stub import StubLLMProvider


def create_llm_provider() -> LLMProvider:
    """Return the configured LLM provider.

    Resolution order:
    1. If LLM_ENABLED is false → StubLLMProvider
    2. If LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY is set → AnthropicLLMProvider
    3. Fallback → StubLLMProvider (missing credentials)
    """
    from app.core import config  # local import avoids circular at module load

    if not config.LLM_ENABLED:
        return StubLLMProvider()

    if config.LLM_PROVIDER == "anthropic":
        api_key = config.ANTHROPIC_API_KEY
        if not api_key:
            return StubLLMProvider()
        from app.services.llm.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider(api_key=api_key, model=config.LLM_MODEL)

    return StubLLMProvider()
