# Notes App Curl Examples

Start the app first:

```bash
uvicorn examples.notes_app:app --reload
```

The examples below assume the app is running at `http://127.0.0.1:8000`.

## 1) List notes (GET)

```bash
# Get all notes
curl "http://127.0.0.1:8000/notes"

# Get one note by id
curl "http://127.0.0.1:8000/notes/note-1"
```

## 2) Add a note

```bash
curl -X POST "http://127.0.0.1:8000/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "new_note": {
      "title": "Reading list",
      "content": "Clean Architecture"
    }
  }'
```

## 3) Modify a note

```bash
curl -X PATCH "http://127.0.0.1:8000/notes/note-2" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "content": "Clean Architecture, Designing Data-Intensive Applications"
    }
  }'
```

## 4) Erase a note

```bash
curl -X DELETE "http://127.0.0.1:8000/notes/note-1"
```

## Optional: chaining with shell variables

```bash
BASE_URL="http://127.0.0.1:8000"

curl -X POST "$BASE_URL/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "new_note": {
      "id": "note-10",
      "title": "Workout",
      "content": "Leg day at 6pm"
    }
  }'
```
