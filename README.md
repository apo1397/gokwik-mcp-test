# GoKwik RTO & KwikFlows MCP Server

An Model Context Protocol (MCP) server that provides tools for analyzing Return to Origin (RTO) and KwikFlows performance metrics. It helps internal stakeholders understand merchant-level risk gradients and delivery outcomes using LLM-powered insights.

## Features

- **Metric Analysis Tool**: `analyze_monthly_risk_flag_metrics` - Provides deep analysis of RTO%, COD share, and CR% grouped by risk flags.
- **Data Retrieval Tool**: `get_metric_analysis_data` - Fetches raw structured data for manual inspection.
- **Guidance Resource**: `guidance://main` - Built-in domain knowledge and troubleshooting guide for agents.
- **Smart Prompting**: Includes a pre-configured analysis flow that ensures `merchant_id` and `date_range` are collected before processing.

## Current Architecture

Currently, the server operates on a **static file approach**:
- Data is read from a CSV/JSON file defined in the `METRIC_ANALYSIS_INPUT_PATH`.
- The [data_transforms.py](src/utils/data_transforms.py) utility handles filtering and normalization.

### Roadmap: Future API Integration
The architecture is designed to be modular. In the future:
1.  The `GetMetricAnalysisDataTool` will be updated to make authenticated API calls to GoKwik's backend services.
2.  The static CSV mock will be replaced with real-time data fetching.
3.  Support for more granular timeframes (weekly/daily) will be added.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/apo1397/gokwik-mcp-test.git
    cd gokwik-mcp-test
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    GEMINI_API_KEY=your_api_key_here
    GEMINI_MODEL=gemini-2.0-flash
    ANALYSIS_TODAY=2026-03-24
    METRIC_ANALYSIS_INPUT_PATH=sample_data/risk_flag_summary.csv
    MCP_SERVER_NAME=rto-kwikflows-mcp
    ```

## Running the Server

### Local Development
To run the server in stdio mode:
```bash
python -m src.app
```

### Integration with MCP Clients (e.g., Claude Desktop / Google Antigravity)
Add the following to your configuration:

```json
{
  "mcpServers": {
    "rto-kwikflows-mcp": {
      "command": "path/to/your/.venv/bin/python3",
      "args": ["-m", "src.app"],
      "env": {
        "GEMINI_API_KEY": "...",
        "PYTHONPATH": "path/to/project/root"
      }
    }
  }
}
```

## Project Structure

- [src/server.py](src/server.py): MCP tool and resource registration.
- [src/prompts/metric_analysis.py](src/prompts/metric_analysis.py): LLM analysis logic and prompt templates.
- [src/services/metric_analysis_service.py](src/services/metric_analysis_service.py): Orchestration layer.
- [resources/guidance.md](resources/guidance.md): Built-in domain guide.

## License
Proprietary - GoKwik Internal Use.
