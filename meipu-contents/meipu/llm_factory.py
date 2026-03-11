import os

from .gemini import Gemini
from .ollama import Ollama


def _is_truthy(raw_value: str) -> bool:
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def create_llm_client(first_assistant_content=None):
    if _is_truthy(os.environ.get("USE_OLLAMA", "false")):
        return Ollama(first_assistant_content)

    return Gemini(first_assistant_content)
