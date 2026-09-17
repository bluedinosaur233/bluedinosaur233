"""Regression checks for parsing public counts and preserving truthful output."""
from datetime import date, timedelta
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('activity', Path(__file__).with_name('update-activity.py'))
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)


class ActivityTests(unittest.TestCase):
    def test_zero_plural_and_comma_separated_counts(self):
        parser = activity.CalendarParser()
        for i, label in enumerate(['No contributions', '1 contribution', '1,234 contributions']):
            parser.feed(f'<td id="d{i}" data-date="2026-09-{15+i}" data-level="{min(i,4)}"></td><tool-tip for="d{i}">{label} on September.</tool-tip>')
        self.assertEqual([d['count'] for d in parser.records()], [0, 1, 1234])

    def test_missing_tooltip_is_not_treated_as_zero(self):
        parser = activity.CalendarParser()
        parser.feed('<td id="d0" data-date="2026-09-17" data-level="0"></td>')
        with self.assertRaises(ValueError):
            parser.records()

    def test_calendar_gap_is_rejected(self):
        days = [{'date':(date(2025,9,18)+timedelta(days=i)).isoformat(), 'count':0, 'level':0} for i in range(365)]
        activity.validate(days)
        del days[50]
        with self.assertRaises(ValueError):
            activity.validate(days)

    def test_recent_window_and_active_days_have_distinct_meanings(self):
        days = [{'date':(date(2025,9,18)+timedelta(days=i)).isoformat(), 'count':0, 'level':0} for i in range(365)]
        days[0]['count'] = 3
        days[-30]['count'] = 5
        days[-31]['count'] = 7
        svg = activity.render(days)
        self.assertIn('15 contributions in the past year, 5 in the last 30 days, 3 active days', svg)

    def test_motion_preserves_counts_and_only_highlights_real_recent_activity(self):
        days = [{'date':(date(2025,9,18)+timedelta(days=i)).isoformat(), 'count':0, 'level':0} for i in range(365)]
        for i in [0, -20, -3, -1]:
            days[i].update(count=2, level=2)
        for narrow in (False, True):
            animated = ET.fromstring(activity.render(days, narrow))
            still = ET.fromstring(activity.render(days, narrow, animated=False))
            cells = lambda root: [(node.attrib['data-date'], node.attrib['data-count'], node.attrib['fill']) for node in root.iter() if 'data-date' in node.attrib]
            self.assertEqual(cells(animated), cells(still))
            self.assertTrue(any(node.tag.endswith('animate') for node in animated.iter()))
            self.assertFalse(any(node.tag.endswith('animate') for node in still.iter()))
            pulses = {node.attrib['data-pulse-date'] for node in animated.iter() if 'data-pulse-date' in node.attrib}
            self.assertEqual(pulses, {days[i]['date'] for i in [-20,-3,-1]})


if __name__ == '__main__':
    unittest.main()
