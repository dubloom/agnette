# LLM Backend Framework

A lightweight Python framework inspired by FastAPI route decorators, but designed for **LLM-as-a-backend**.

When a route is hit, the framework:
1. Builds a prompt that includes route metadata and request context.
2. Runs a Claude agent through `claude-agent-sdk`.
3. Returns plain text as the HTTP response.
4. Appends an invocation record to a local JSONL file (no database required).

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Set your Anthropic credentials:

```bash
export ANTHROPIC_API_KEY=your-api-key
```

## Quick Start

```python
from llm_backend_framework import LLMApp

framework = LLMApp()

@framework.route("/hello", methods=["POST"], prompt="Reply with a short greeting.")
def hello() -> None:
    pass

app = framework.to_starlette()
```

Run:

```bash
uvicorn examples.basic_app:app --reload
```

## Request Handling Behavior

- Route prompt is defined at declaration time via `@framework.route(..., prompt="...")`.
- Each incoming request contributes context:
  - path, method
  - path/query params
  - JSON body or raw body text
- Final prompt is sent to Claude through `ClaudeAgentRunner`.
- Response body is plain text (`text/plain`).

## File-Based Persistence

All invocations are recorded in:

- `data/invocations.jsonl`

Each line contains:

- timestamp
- route path
- HTTP method
- composed prompt
- request context
- response text or error

This keeps the initial framework simple and satisfies the requirement to use files rather than a database.

## Testing

```bash
pytest
```
