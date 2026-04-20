"""
Agnette example: sign-in mints a Bearer token (LLM-generated); middleware allows any
request whose Bearer token appears in the issued-token store.

Tokens are persisted by the **sign-in** agent using Read/Write on `data/issued_tokens.json`.
The **middleware** agent uses Read on that file to decide allow/deny — no Python token checks.

Run (from repo root):
  uvicorn examples.auth_app:app --reload

Try:
  curl -sS http://127.0.0.1:8000/health
  curl -sS -X POST http://127.0.0.1:8000/auth/sign-in -H 'Content-Type: application/json' -d '{}'

  # Copy access_token from the JSON response, then:
  curl -sS -X POST http://127.0.0.1:8000/private/echo \\
    -H "Authorization: Bearer <paste-token>" \\
    -H 'Content-Type: application/json' -d '{"msg":"hi"}'

This is what a LLM has to say on this app:
  +----------------------------------------------------------------------------------------------------------------------+
  | + [N1] Document LLM-based auth limitations in auth_app example                                                       |
  | file: examples/auth_app.py                                                                                           |
  |                                                                                                                      |
  | Why: The auth example relies entirely on LLM prompt-following for security (token validation, file I/O). While       |
  | novel, this is inherently less reliable than deterministic code. The example would benefit from an explicit warning  |
  | comment that this is a demonstration and should not be used for production authentication without additional         |
  | safeguards.                                                                                                          |
  |                                                                                                                      |
  | Fix: Add a comment block near the top of auth_app.py warning that LLM-based auth is for demonstration only and       |
  | explaining why (non-deterministic, dependent on prompt-following, cost per request, etc.).                           |
  +----------------------------------------------------------------------------------------------------------------------+
"""

from glyph import AgentOptions

from agnette import Agnette

# Relative to process working directory (run uvicorn from repo root).
_ISSUED_TOKENS_FILE = "data/issued_tokens.json"

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    )
)


@app.middleware(
    "http",
    prompt=f"""You enforce Bearer authentication for this API using tools.

            Issued tokens live in a JSON file (array of strings, one entry per successful sign-in):
            Path: {_ISSUED_TOKENS_FILE}

            You MUST use the Read tool to load that file when you need to validate a token.

            Decision procedure (return JSON allow/403 per system instructions):

            1) Normalize path: strip a single trailing "/" from request_context.path unless it is exactly "/".
            2) If method is GET and normalized path is "/health" → allow=true.
            3) If method is POST and normalized path is "/auth/sign-in" → allow=true (sign-in is public; no Bearer required).
            4) Otherwise:
            a) Read {_ISSUED_TOKENS_FILE}. Parse as JSON. It must be a JSON array of strings. If file is missing or unreadable, treat issued list as empty [].
            b) From request_context.headers (keys may be lower-case), get the Authorization header.
            c) If there is no "Bearer " prefix (single space after Bearer), or no token after it → allow=false, status_code=403.
            d) Strip leading/trailing ASCII whitespace from the token only (do not alter inner characters).
            e) If the token is exactly equal to one of the strings in the issued array → allow=true.
            f) Otherwise allow=false, status_code=403, response_text short message like "Forbidden: unknown or revoked token".

            Important:
            - Do not allow protected routes just because some Bearer string was sent; only allow if it is in the file you read.
            - You must actually Read the file before deciding for step 4; do not guess the list.
    """
)
def bearer_auth_middleware() -> None:
    """Prompt-driven middleware declaration anchor."""


@app.get(
    "/health",
    prompt="Return a short one-line health check response for this API route.",
)
def health_route() -> None:
    """Public route."""


@app.post(
    "/auth/sign-in",
    prompt=f"""You run the sign-in endpoint: mint a new Bearer token and register it.

        Token store (JSON array of strings):
        {_ISSUED_TOKENS_FILE}

        Steps:
        1) Generate one new random `access_token` string: at least 32 characters from [A-Za-z0-9_-] only.
        2) Read {_ISSUED_TOKENS_FILE}. If missing or not valid JSON array, use [].
        3) Append the new token string to the array (no duplicates). Write the file back as valid JSON only (a single JSON array).
        4) Reply to the client with **only** a JSON object (no markdown fences, no extra prose), exactly in this shape:
        {{"access_token":"<token>","token_type":"Bearer","expires_in":3600}}

        Use the same token value in `access_token` as the string you appended to the array.
        """
)
def sign_in_route() -> None:
    """Public: LLM mints a token and appends it to the token file."""


@app.post(
    "/private/echo",
    prompt=(
        "Echo back the user's message in a friendly one-liner. "
        "Read `msg` from `json_body` in the request context if present."
    ),
)
def private_echo_route() -> None:
    """Requires Authorization: Bearer <issued access_token>."""
