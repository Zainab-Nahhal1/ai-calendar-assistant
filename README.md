# Calendar Assistant (Local-safe)

This repository contains a local-only version of a calendar assistant suitable
for publishing. External API usage (Google Calendar, OpenAI, LangChain, etc.)
has been removed; the assistant uses a local JSON file under `samples/`.

Quick start
-----------

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Run the assistant:

```bash
python main.py
```

Usage
-----

Use explicit function calls to interact with the assistant. Example:

```text
CALL_FUNCTION: book_event(summary="Standup", start_time="2026-01-02T09:00:00", end_time="2026-01-02T09:15:00")
```

Files
-----

- `google_calendar_assistant.py`: core local implementation
- `main.py`: entry point
- `samples/events.json`: local event store
- `tests/test_calendar.py`: basic unit tests

Security
--------

Do not add credentials or tokens to the repository. If you re-enable API
integrations, keep credentials in environment variables or external secrets
management and add them to `.gitignore`.

License
-------

Use as you wish.
