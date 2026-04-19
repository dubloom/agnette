# Agnette

The FIRST LLM-as-a-backend framework.

Agnette is a lightweight ASGI framework built on Starlette where route and middleware logic is driven by LLM prompts.

## Runtime Support

This project is intended to run with `uvicorn` only for now.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

```python
from agnos import AgentOptions
from agnette import Agnette

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    )
)

@app.post("/hello", prompt="Reply with a short greeting.")
def hello() -> None:
    pass
```

Run:

```bash
uvicorn examples.notes_app:app --reload
```

## How It Works

For each route request, Agnette:

1. Collects request context (`path`, `method`, `path_params`, `query_params`, `headers`, and body as `json_body` or `raw_body`).
2. Composes a final prompt with route metadata and your route prompt.
3. Executes the agent via `agnos.query(...)`.
4. Returns the model output as `text/plain`.

If execution fails, the route returns `500` with `Agent execution failed: ...`.

## Routing API

Use decorators on an `Agnette` app instance:

- `@app.route(path, prompt=..., methods=[...])`
- `@app.get(...)`
- `@app.post(...)`
- `@app.put(...)`
- `@app.patch(...)`
- `@app.delete(...)`
- `@app.options(...)`
- `@app.head(...)`

Each route can override `agent_options`; otherwise it uses `default_agent_options`.

## Prompt Middleware

Agnette supports HTTP middleware through:

```python
@app.middleware("http", prompt="...")
def my_middleware() -> None:
    pass
```

Middleware prompt output must be JSON with:

- `allow` (required boolean)
- `status_code` (optional integer, default `403`)
- `response_text` (optional string)

If `allow` is `false`, the request is blocked with a plain-text response.

## Included Examples

### Notes CRUD (file-backed)

`examples/notes_app.py` demonstrates prompt-driven CRUD using `data/notes.json`.

Run:

```bash
uvicorn examples.notes_app:app --reload
```

### Auth + Protected Route (file-backed tokens)

`examples/auth_app.py` demonstrates:

- public `/health`
- public `/auth/sign-in` that mints/stores bearer tokens in `data/issued_tokens.json`
- protected `/private/echo` enforced by prompt-driven HTTP middleware

Run:

```bash
uvicorn examples.auth_app:app --reload
```

## Cost Logging

- Each completed agent run logs its cost.
- Agnette also logs total accumulated cost on app shutdown.
