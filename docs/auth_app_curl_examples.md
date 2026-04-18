# Auth App Curl Examples

This example (`examples/auth_app.py`) uses **prompt-based HTTP middleware** plus:

- **`POST /auth/sign-in`** — the LLM generates an `access_token`, appends it to `data/issued_tokens.json`, and returns JSON modeled on OAuth2-style responses.
- **Protected routes** (e.g. `POST /private/echo`) — the middleware agent **Read**s `data/issued_tokens.json` and allows the request only if the `Authorization: Bearer` value matches an issued token.

Public routes (no Bearer required): `GET /health`, `POST /auth/sign-in`.

Run **uvicorn from the repository root** so paths like `data/issued_tokens.json` resolve correctly.

## Prerequisites

**Anthropic API key** (agents power routes and middleware):

```bash
export ANTHROPIC_API_KEY=your-api-key
```

## Start the server

```bash
uvicorn examples.auth_app:app --reload
```

Examples below use `http://127.0.0.1:8000`.

## 1) Health (no auth)

```bash
curl -sS "http://127.0.0.1:8000/health"
```

## 2) Sign in (mint a token)

```bash
curl -sS -X POST "http://127.0.0.1:8000/auth/sign-in" \
  -H "Content-Type: application/json" \
  -d '{}'
```

The response should be a JSON object with `access_token` and `token_type`. Copy `access_token` for the next steps (the exact format depends on the model following the route prompt).

## 3) Private echo with issued Bearer token

Replace `PASTE_ACCESS_TOKEN` with the value from sign-in:

```bash
curl -sS -X POST "http://127.0.0.1:8000/private/echo" \
  -H "Authorization: Bearer PASTE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msg":"hi"}'
```

## 4) Private echo without token (expect block)

```bash
curl -sS -X POST "http://127.0.0.1:8000/private/echo" \
  -H "Content-Type: application/json" \
  -d '{"msg":"hi"}'
```

Expect a **403** from middleware if the agent denies the request.

## 5) Wrong Bearer token (expect block)

```bash
curl -sS -X POST "http://127.0.0.1:8000/private/echo" \
  -H "Authorization: Bearer not-a-issued-token" \
  -H "Content-Type: application/json" \
  -d '{"msg":"hi"}'
```

## Optional: shell variables

```bash
BASE_URL="http://127.0.0.1:8000"

curl -sS "$BASE_URL/health"

# Sign in and capture token (requires jq; response must be strict JSON)
TOKEN="$(curl -sS -X POST "$BASE_URL/auth/sign-in" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.access_token')"

curl -sS -X POST "$BASE_URL/private/echo" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msg":"hello from curl"}'
```

## Notes

- **Issued tokens** accumulate in `data/issued_tokens.json`. Delete or reset that file to clear sessions for local testing.
- **Middleware and routes are LLM-driven** (including file Read/Write). Behavior depends on the model following prompts and returning valid JSON for middleware decisions.
- **Cost**: each HTTP request runs the middleware agent; each route runs again for the handler.
