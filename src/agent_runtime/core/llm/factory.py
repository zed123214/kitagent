from agent_runtime.core.config import LlmConfig
from agent_runtime.core.llm.base import LLMProvider
from agent_runtime.core.llm.provider import AnthropicProvider


def create_provider(config: LlmConfig) -> LLMProvider:
    if config.provider == "openai":
        from agent_runtime.core.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(config.model)
    return AnthropicProvider(config.model)
