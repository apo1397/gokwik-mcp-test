from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI


def build_chat_model(*, api_key: str, model: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0,
        timeout=120,
        max_retries=1,
    )
