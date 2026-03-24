from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    analysis_today: str = "2026-03-24"
    metric_analysis_input_path: str = "sample_data/risk_flag_summary.csv"
    mcp_server_name: str = "rto-mcp"

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required. Add it to your environment or .env file.")
        return cls(
            gemini_api_key=api_key,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            analysis_today=os.getenv("ANALYSIS_TODAY", "2026-03-24"),
            metric_analysis_input_path=os.getenv("METRIC_ANALYSIS_INPUT_PATH", "sample_data/risk_flag_summary.csv"),
            mcp_server_name=os.getenv("MCP_SERVER_NAME", "rto-kwikflows-mcp"),
        )
