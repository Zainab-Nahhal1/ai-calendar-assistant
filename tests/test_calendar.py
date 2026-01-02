import os
import tempfile
import json
import unittest
from google_calendar_assistant import CalendarFunctions, _save_events


class CalendarFunctionsTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.events_path = os.path.join(self.tmpdir.name, 'events.json')
        # create empty events file
        with open(self.events_path, 'w', encoding='utf-8') as f:
            json.dump({'events': []}, f)
        self.funcs = CalendarFunctions(events_path=self.events_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_book_and_check(self):
        r = self.funcs.book_event('Test', '2026-01-02T10:00:00', '2026-01-02T11:00:00')
        self.assertIn('✅', r)

        available = self.funcs.check_availability('2026-01-02')
        self.assertIn('meeting', available) or self.assertIn('You have', available)

    def test_cancel(self):
        r = self.funcs.book_event('CancelMe', '2026-01-03T10:00:00', '2026-01-03T11:00:00')
        # load id
        with open(self.events_path, 'r', encoding='utf-8') as f:
            events = json.load(f)['events']
        ev_id = events[0]['id']

        canceled = self.funcs.cancel_event(event_id=ev_id)
        self.assertIn('✅', canceled)


if __name__ == '__main__':
    unittest.main()
