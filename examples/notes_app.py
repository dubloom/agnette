"""
Agnette example: CRUD notes backed by `data/notes.json` (LLM-driven file I/O).

Run (from repo root):
  uvicorn examples.notes_app:app --reload

Try:
  curl -sS http://127.0.0.1:8000/notes
  curl -sS http://127.0.0.1:8000/notes/note-1

  curl -sS -X POST http://127.0.0.1:8000/notes \
    -H 'Content-Type: application/json' \
    -d '{"new_note":{"title":"Hello","content":"World"}}'

  curl -sS -X PATCH http://127.0.0.1:8000/notes/note-1 \
    -H 'Content-Type: application/json' \
    -d '{"updates":{"title":"Hi"}}'

  curl -sS -X DELETE http://127.0.0.1:8000/notes/note-1
"""
from agnette import Agnette, AgentOptions

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    )
)


@app.get(
    "/notes",
    prompt=(
        "Read notes from a file and return either one note or all notes.\n"
        "Use `data/notes.json` as storage. If it does not exist, treat notes as an empty list.\n"
        "Rules:\n"
        "1. Return all notes.\n"
        "2. Return only valid JSON with keys:\n"
        '   - `notes`: list of notes\n'
        '   - `message`: short success message\n'
        "Do not include markdown fences."
    ),
)
def list_notes_route() -> None:
    """Decorator anchor; route behavior is prompt-driven."""


@app.get(
    "/notes/{id}",
    prompt=(
        "Read notes from a file and return one note by id.\n"
        "Use `data/notes.json` as storage. If it does not exist, treat notes as an empty list.\n"
        "Use path param `id` from the request context as the target note id.\n"
        "Rules:\n"
        "1. If note is found, return it.\n"
        "2. If note is not found, return null and a clear message.\n"
        "3. Return only valid JSON with keys:\n"
        '   - `note`: note object or null\n'
        '   - `message`: short success or not-found message\n'
        "Do not include markdown fences."
    ),
)
def get_note_by_id_route() -> None:
    """Decorator anchor; route behavior is prompt-driven."""


@app.post(
    "/notes",
    prompt=(
        "Add a new note to file-backed storage.\n"
        "Use `data/notes.json` as storage. If it does not exist, start from an empty list.\n"
        "Input JSON body format:\n"
        "- `new_note`: object with `title` and `content` (optional `id`)\n\n"
        "Rules:\n"
        "1. If `new_note.id` is missing, create one as `note-<n>` where n is next available integer.\n"
        "2. Append the note to stored notes and write back to `data/notes.json`.\n"
        "3. Return only valid JSON with keys:\n"
        '   - `note`: the inserted note\n'
        '   - `message`: short success string\n'
        "Do not include markdown fences."
    ),
)
def add_note_route() -> None:
    """Decorator anchor; route behavior is prompt-driven."""


@app.patch(
    "/notes/{id}",
    prompt=(
        "Modify one stored note in file-backed storage.\n"
        "Use `data/notes.json` as storage. If it does not exist, treat notes as an empty list.\n"
        "Input JSON body format:\n"
        "- `updates`: object that may contain `title` and/or `content`\n\n"
        "Use path param `id` from the request context as the target note id.\n"
        "Rules:\n"
        "1. Find note by exact `id`.\n"
        "2. Apply only fields present in `updates`.\n"
        "3. Persist updates to `data/notes.json`.\n"
        "4. If no note is found, return a clear error message.\n"
        "5. Return only valid JSON with keys:\n"
        '   - `note`: updated note or null\n'
        '   - `message`: success or not-found message\n'
        "Do not include markdown fences."
    ),
)
def modify_note_route() -> None:
    """Decorator anchor; route behavior is prompt-driven."""


@app.delete(
    "/notes/{id}",
    prompt=(
        "Erase one stored note from file-backed storage.\n"
        "Use `data/notes.json` as storage. If it does not exist, treat notes as an empty list.\n"
        "Use path param `id` from the request context as the target note id.\n"
        "Rules:\n"
        "1. Remove the note with matching `id`.\n"
        "2. Persist updates to `data/notes.json`.\n"
        "3. If no note is found, return a clear error message.\n"
        "4. Return only valid JSON with keys:\n"
        '   - `deleted_id`: deleted id or null\n'
        '   - `message`: success or not-found message\n'
        "Do not include markdown fences."
    ),
)
def erase_note_route() -> None:
    """Decorator anchor; route behavior is prompt-driven."""
