# Calendar Assistant (Local-safe)

This repository contains a local-only version of a calendar assistant intended
for demos, tests, and safe publishing. All external API calls (Google
Calendar, OpenAI, LangChain, etc.) have been removed from the main branch to
avoid leaking credentials. The assistant stores events in `samples/events.json`
and provides the same high-level operations you would expect from an online
calendar: booking events, checking availability, canceling events, and
generating daily reports.

Key goals
---------

- Provide a minimal, runnable calendar assistant without external credentials.
- Keep function signatures compatible with a future Google-backed implementation.
- Offer simple unit tests and sample data so CI can validate basic behavior.

Quick start
-----------

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Run the assistant locally:

```bash
python main.py
```

Usage
-----

Interact using explicit, safe function calls. Example:

```text
CALL_FUNCTION: book_event(summary="Standup", start_time="2026-01-02T09:00:00", end_time="2026-01-02T09:15:00")
```

This avoids any automatic LLM or API calls on the main branch. If you want
natural-language parsing with an LLM, add it in a private branch and keep any
API keys out of the repository.

Features
--------

- Book events with a summary, start/end times, description, location, and
	attendees.
- Check availability for a date or a specific time range.
- Cancel events by ID or by searching for a summary.
- Generate a human-friendly daily report summarizing events and total time.

Project layout
--------------

- `google_calendar_assistant.py`: core local implementation (file-backed).
- `main.py`: simple CLI entry point to interact with the assistant.
- `samples/events.json`: local JSON event store (committed empty by default).
- `tests/test_calendar.py`: basic unit tests using a temporary events file.
- `requirements.txt`: minimal runtime dependencies.
- `Makefile`: convenience targets for `install`, `test`, and `run`.

Extending to real APIs
----------------------

If you later re-enable Google Calendar or an LLM, do the following:

- Keep credentials out of version control. Use environment variables or a
	secrets manager.
- Add real API code on a protected branch and document setup steps in a
	private README or deployment playbook.

Security
--------

Never commit credentials, tokens, or `.env` files. The repository includes a
`.gitignore` that excludes common secret files; double-check it before
publishing.

License
-------

Use as you wish.
