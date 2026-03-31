from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_model: str = "gemini-2.5-flash"
    mcp_server_name: str = "rto-mcp"
    api_auth_token: str = "rto$dash-board*prod"
    api_base_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/shopify/rto/analytics"
    kwikflows_api_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"
    kwikflows_impact_api_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/impact/metrics"

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("LLM_API_KEY (or GEMINI_API_KEY) is required. Add it to your environment or .env file.")
        return cls(
            llm_api_key=api_key,
            llm_model=os.getenv("LLM_MODEL") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            mcp_server_name=os.getenv("MCP_SERVER_NAME", "rto-kwikflows-mcp"),
            api_auth_token=os.getenv("API_AUTH_TOKEN", "rto$dash-board*prod"),
            api_base_url=os.getenv("API_BASE_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/shopify/rto/analytics"),
            kwikflows_api_url=os.getenv("KWIKFLOWS_API_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"),
            kwikflows_impact_api_url=os.getenv("KWIKFLOWS_IMPACT_API_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/impact/metrics"),
        )
