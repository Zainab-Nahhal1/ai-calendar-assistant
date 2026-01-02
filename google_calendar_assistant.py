"""
Lightweight local Calendar Assistant
===================================

This repository contains a safe, local-only implementation of the calendar
assistant used for demos and tests. All calls to external APIs (Google
Calendar, OpenAI, LangChain, etc.) have been removed to make the project
safe to publish. The assistant uses a local JSON file in `samples/` to
store and query events.

Files created/modified:
- `google_calendar_assistant.py` (sanitized local-only logic)
- `main.py` (entry point)
- `samples/events.json` (local event storage)
- `tests/test_calendar.py` (basic unit tests)

If you want to re-enable real API integrations, keep credentials out of the
repository and follow provider best practices. See README.md for details.
"""

import os
import json
import uuid
import datetime
from typing import Optional, List, Dict, Any
from dateutil import parser


EVENTS_PATH = os.path.join(os.path.dirname(__file__), 'samples', 'events.json')


def _ensure_events_file(path: str = EVENTS_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'events': []}, f, indent=2)


def _load_events(path: str = EVENTS_PATH) -> List[Dict[str, Any]]:
    _ensure_events_file(path)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f).get('events', [])


def _save_events(events: List[Dict[str, Any]], path: str = EVENTS_PATH):
    _ensure_events_file(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'events': events}, f, indent=2, default=str)


class CalendarFunctions:
    """Local, file-backed calendar functions for demos and tests.

    This implementation stores events in `samples/events.json` and provides
    the same method signatures as a Google-backed implementation so it's
    easy to swap implementations later.
    """

    def __init__(self, events_path: str = EVENTS_PATH):
        self.events_path = events_path

    def book_event(self, summary: str, start_time: str, end_time: str,
                   description: str = "", location: str = "",
                   attendees: Optional[List[str]] = None) -> str:
        try:
            start_dt = parser.parse(start_time)
            end_dt = parser.parse(end_time)

            event = {
                'id': str(uuid.uuid4()),
                'summary': summary,
                'location': location,
                'description': description,
                'start': start_dt.isoformat(),
                'end': end_dt.isoformat(),
                'attendees': attendees or [],
            }

            events = _load_events(self.events_path)
            events.append(event)
            _save_events(events, self.events_path)

            return f"✅ Event booked locally. ID: {event['id']}"
        except Exception as e:
            return f"❌ Error booking event: {e}"

    def check_availability(self, date: str, start_time: Optional[str] = None,
                          end_time: Optional[str] = None) -> str:
        try:
            target_date = datetime.datetime.strptime(date, '%Y-%m-%d')

            if start_time and end_time:
                time_min = parser.parse(f"{date} {start_time}")
                time_max = parser.parse(f"{date} {end_time}")
            else:
                time_min = target_date.replace(hour=0, minute=0, second=0)
                time_max = target_date.replace(hour=23, minute=59, second=59)

            events = _load_events(self.events_path)
            busy = []
            for ev in events:
                start = parser.parse(ev['start'])
                end = parser.parse(ev['end'])
                if (start <= time_max) and (end >= time_min):
                    busy.append(ev)

            if not busy:
                return f"✅ You're free on {date}" + (f" from {start_time} to {end_time}" if start_time else "")

            result = f"📅 You have {len(busy)} meeting(s) on {date}:\n"
            for ev in busy:
                start_dt = parser.parse(ev['start'])
                result += f"• {ev.get('summary', 'Untitled')} at {start_dt.strftime('%H:%M')} (ID: {ev['id']})\n"

            return result
        except Exception as e:
            return f"❌ Error checking availability: {e}"

    def cancel_event(self, event_id: Optional[str] = None,
                    event_summary: Optional[str] = None,
                    date: Optional[str] = None) -> str:
        try:
            events = _load_events(self.events_path)

            if event_id:
                new_events = [e for e in events if e.get('id') != event_id]
                if len(new_events) == len(events):
                    return f"❌ No event with ID {event_id} found"
                _save_events(new_events, self.events_path)
                return f"✅ Event {event_id} canceled locally"

            if not event_summary:
                return "❌ Please provide either event_id or event_summary"

            matches = [e for e in events if event_summary.lower() in e.get('summary', '').lower()]

            if not matches:
                return f"❌ No event found with summary '{event_summary}'"

            if len(matches) > 1:
                result = f"Found {len(matches)} events matching '{event_summary}':\n"
                for i, ev in enumerate(matches, 1):
                    result += f"{i}. {ev.get('summary')} (ID: {ev['id']})\n"
                result += "Please specify the event_id to cancel a specific event."
                return result

            ev = matches[0]
            new_events = [e for e in events if e.get('id') != ev.get('id')]
            _save_events(new_events, self.events_path)
            return f"✅ Event '{ev.get('summary')}' canceled locally"
        except Exception as e:
            return f"❌ Error canceling event: {e}"

    def generate_daily_report(self, date: str) -> str:
        try:
            target_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            time_min = target_date.replace(hour=0, minute=0, second=0)
            time_max = target_date.replace(hour=23, minute=59, second=59)

            events = _load_events(self.events_path)
            day_events = [e for e in events if (parser.parse(e['start']) <= time_max) and (parser.parse(e['end']) >= time_min)]

            report = f"📊 DAILY CALENDAR REPORT - {target_date.strftime('%A, %B %d, %Y')}\n"
            report += "=" * 60 + "\n\n"

            if not day_events:
                report += "No events scheduled for this day.\n"
                return report

            report += f"Total Events: {len(day_events)}\n\n"
            total_minutes = 0

            for i, ev in enumerate(day_events, 1):
                start_dt = parser.parse(ev['start'])
                end_dt = parser.parse(ev['end'])
                duration = (end_dt - start_dt).total_seconds() / 60
                total_minutes += duration

                report += f"{i}. {ev.get('summary', 'Untitled Event')}\n"
                report += f"   Time: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}\n"
                report += f"   Duration: {int(duration)} minutes\n\n"

            report += "=" * 60 + "\n"
            report += f"Total Meeting Time: {int(total_minutes / 60)}h {int(total_minutes % 60)}m\n"
            return report
        except Exception as e:
            return f"❌ Error generating report: {e}"


class CalendarAgent:
    """Minimal local agent.

    This agent does not call external LLMs. It only accepts explicit
    function-call strings in the format `CALL_FUNCTION: func_name(arg=... )`.
    This makes the repository safe to publish. If you want natural-language
    parsing, re-enable an LLM in a private branch and keep credentials out of
    the repo.
    """

    def __init__(self, events_path: str = EVENTS_PATH):
        self.functions = CalendarFunctions(events_path)

    def _parse_function_call(self, text: str) -> Optional[Dict[str, Any]]:
        if "CALL_FUNCTION:" not in text:
            return None
        try:
            func_part = text.split("CALL_FUNCTION:", 1)[1].strip()
            name = func_part.split("(", 1)[0].strip()
            params_str = func_part.split("(", 1)[1].rsplit(")", 1)[0]
            params: Dict[str, Any] = {}
            if params_str.strip():
                # naive split by comma
                for p in params_str.split(','):
                    if '=' in p:
                        k, v = p.split('=', 1)
                        v = v.strip().strip('"').strip("'")
                        params[k.strip()] = v if v.lower() != 'none' else None
            return {'function': name, 'params': params}
        except Exception:
            return None

    def _execute_function(self, func_name: str, params: Dict[str, Any]) -> str:
        if func_name == 'book_event':
            return self.functions.book_event(**params)
        if func_name == 'check_availability':
            return self.functions.check_availability(**params)
        if func_name == 'cancel_event':
            return self.functions.cancel_event(**params)
        if func_name == 'generate_daily_report':
            return self.functions.generate_daily_report(**params)
        return f"❌ Unknown function: {func_name}"

    def run(self, user_input: str) -> str:
        """Run the agent on a piece of input.

        The agent expects the user to include an explicit `CALL_FUNCTION:`
        directive. This avoids any external API usage.
        """
        function_call = self._parse_function_call(user_input)
        if not function_call:
            return (
                "Please call functions using the format:\n"
                "CALL_FUNCTION: book_event(summary=\"Meeting\", start_time=\"2026-01-02T14:00:00\", end_time=\"2026-01-02T15:00:00\")\n\n"
                "Available functions: book_event, check_availability, cancel_event, generate_daily_report"
            )

        return self._execute_function(function_call['function'], function_call['params'])


def main():
    print("Local Calendar Assistant (safe for publishing).\n")
    print("Instructions: Use CALL_FUNCTION: ... to run functions. Example:")
    print("CALL_FUNCTION: book_event(summary=\"Standup\", start_time=\"2026-01-02T09:00:00\", end_time=\"2026-01-02T09:15:00\")\n")

    agent = CalendarAgent()

    while True:
        try:
            user_input = input('\nYou: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye')
            break

        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', 'bye'):
            print('Goodbye')
            break

        print('\nAgent:')
        print(agent.run(user_input))


if __name__ == '__main__':
    main()
    print("- 'Book a meeting with John tomorrow at 2pm for 1 hour about project review'")
    print("- 'Check if I'm free on January 15th'")
    print("- 'Cancel my meeting with Sarah'")
    print("- 'Generate a report for tomorrow'")
    print("\nType 'quit' to exit\n")
    
    while True:
        user_input = input("\n🗓️  You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\n🤖 Agent: ", end="")
        response = agent.run(user_input)
        print(response)


if __name__ == "__main__":
    main()