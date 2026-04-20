"""
Agnette example: habit tracker in full vibe mode (single prompt, no route definitions).

Run (from repo root):
  uvicorn examples.pure_vibe_app:app --reload

Try:
  curl -sS http://127.0.0.1:8000/
  curl -sS -X POST http://127.0.0.1:8000/habits \
    -H 'Content-Type: application/json' \
    -d '{"name":"drink water","target_per_day":8,"unit":"glasses"}'

  curl -sS http://127.0.0.1:8000/habits
  curl -sS http://127.0.0.1:8000/habits/habit-1

  curl -sS -X POST http://127.0.0.1:8000/habits/habit-1/check-in \
    -H 'Content-Type: application/json' \
    -d '{"status":"done","value":1}'
"""

from agnette import Agnette, AgentOptions

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    ),
    prompt=(
        "You are the backend for a playful habit tracker app. "
        "Handle any HTTP path and method as a habit-tracking action, using request context "
        "(path, method, query params, headers, and body). "
        "Support use cases like creating habits, checking in, streak updates, daily summaries, "
        "motivational nudges, and reminders. "
        "Be encouraging but practical. "
        "Keep responses concise. "
        "You have the authorization to store data in files for memory "
        "If the request suggests structured output or includes JSON, return valid JSON only."
    ),
)
