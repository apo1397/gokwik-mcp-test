from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str = "deepseek-ai/deepseek-v3.2"
    analysis_today: str = "2026-03-24"
    mcp_server_name: str = "rto-mcp"
    api_auth_token: str = "rto$dash-board*prod"

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required. Add it to your environment or .env file.")
        return cls(
            gemini_api_key=api_key,
            gemini_model=os.getenv("GEMINI_MODEL", "deepseek-ai/deepseek-v3.2"),
            analysis_today=os.getenv("ANALYSIS_TODAY", "2026-03-24"),
            mcp_server_name=os.getenv("MCP_SERVER_NAME", "rto-kwikflows-mcp"),
            api_auth_token=os.getenv("API_AUTH_TOKEN", "rto$dash-board*prod"),
        )
