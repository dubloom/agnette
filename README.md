# Agnette

The **FIRST** LLM-as-a-backend framework.

<p align="center">
  <img src="images/agnette.png" alt="Agnette logo" width="400"/>
</p>

Who needs fast, deterministic and cheap backend when you can have agents?

Why write boring, predictable code when you can replace your entire API with **vibes**? 🚀

Tired of your endpoints responding in *microseconds*? 😴
Sick of knowing **exactly** what your backend will do? 🥱
Fed up with paying *pennies* for compute? 😤

Agnette liberates you from the tyranny of determinism.

✅ Your `/users` endpoint can now **hallucinate** creative new users

✅ Your auth middleware can *philosophize* about whether someone deserves access

✅ Your database queries become polite requests to an AI that may or may not feel like helping today

Each request is a surprise(🎁), each response is an adventure (🌈), your API now costs more than your CEO's salary (💸)

**This is the future.** 🔥

(The package is powered by [`glyph-agents`] https://github.com/dubloom/glyph-agents, another lib I'm building).


## Runtime Support

This project is intended to run with `uvicorn` only for now.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install agnette
```

## Quick Start

```python
from glyph import AgentOptions
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

## Vibe Mode (No Routes)

You can run Agnette in full "LLM-as-a-backend" mode with a single app-level prompt and no route decorators.

Why define routes when you can just *describe your entire app in one sentence* and let the model figure out the rest? 🧘

No paths. No methods. No schemas. The LLM is the router, the controller, the business logic, *and* the database layer. Your API is now a philosophy. ✨

```python
from agnette import Agnette, AgentOptions

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    ),
    prompt="You are the backend for a playful habit tracker app...",
)
```

Run:

```bash
uvicorn examples.pure_vibe_app:app --reload
```

Try:

```bash
curl -sS -X POST http://127.0.0.1:8000/habits \
  -H 'Content-Type: application/json' \
  -d '{"name":"drink water","target_per_day":8,"unit":"glasses"}'

curl -sS http://127.0.0.1:8000/habits
curl -sS http://127.0.0.1:8000/habits/habit-1
```

## How It Works

For each route request, Agnette:

1. Collects request context (`path`, `method`, `path_params`, `query_params`, `headers`, and body as `json_body` or `raw_body`).
2. Composes a final prompt with route metadata and your route prompt.
3. Executes the agent via `glyph.query(...)`.
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

### Pure Vibe Habit Tracker (single prompt)

`examples/pure_vibe_app.py` demonstrates full vibe mode:

- no route definitions
- one app-level prompt that handles all paths/methods
- playful habit-tracker behavior with optional file-backed memory via tools

Run:

```bash
uvicorn examples.pure_vibe_app:app --reload
```

## Cost Logging

- Each completed agent run logs its cost.
- Agnette also logs total accumulated cost on app shutdown.
