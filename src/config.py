from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mcp_server_name: str = "rto-kwikflows-mcp"
    api_auth_token: str = "rto$dash-board*prod"
    api_base_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/shopify/rto/analytics"
    kwikflows_api_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"
    kwikflows_impact_api_url: str = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/impact/metrics"

    # LLM settings — commented out, no longer needed for data-only mode
    # llm_api_key: str = ""
    # llm_model: str = "gemini-2.5-flash"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mcp_server_name=os.getenv("MCP_SERVER_NAME", "rto-kwikflows-mcp"),
            api_auth_token=os.getenv("API_AUTH_TOKEN", "rto$dash-board*prod"),
            api_base_url=os.getenv("API_BASE_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/shopify/rto/analytics"),
            kwikflows_api_url=os.getenv("KWIKFLOWS_API_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"),
            kwikflows_impact_api_url=os.getenv("KWIKFLOWS_IMPACT_API_URL", "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/impact/metrics"),
        )
