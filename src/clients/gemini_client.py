from __future__ import annotations

from langchain_openai import ChatOpenAI

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def build_chat_model(*, api_key: str, model: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=NVIDIA_BASE_URL,
        temperature=1,
        top_p=0.95,
        max_tokens=8192,
    )
