from analyzer.backends.base import LLMBackend
from analyzer.backends.deepseek_api import DeepSeekBackend
from analyzer.backends.vllm_local import VLLMLocalBackend
from shared.config import settings


def get_backend() -> LLMBackend:
    if settings.llm_backend == "deepseek_api":
        return DeepSeekBackend(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    if settings.llm_backend == "vllm_local":
        return VLLMLocalBackend(base_url=settings.deepseek_base_url)
    raise ValueError(f"Unknown LLM backend: {settings.llm_backend}")
