"""Render GitHub's public contribution calendar; requires only Python 3.

Fetches the same public contribution counts shown on the user's GitHub profile.
No token or third-party statistics service is required.
"""
from argparse import ArgumentParser
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import html
import json
import re
import time

ROOT = Path(__file__).resolve().parents[1]
USER = 'bluedinosaur233'
URL = f'https://github.com/users/{USER}/contributions'
OUT = ROOT / 'assets/profile-v2'
COLORS = ['#E8EDF5', '#BBE1EC', '#79BDD9', '#758DCE', '#BD78A9']


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tooltips = {}
        self.current = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('data-date') and attrs.get('data-level'):
            self.cells[attrs['id']] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        if tag == 'tool-tip' and attrs.get('for'):
            self.current = attrs['for']
            self.tooltips[self.current] = ''

    def handle_data(self, data):
        if self.current:
            self.tooltips[self.current] += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.current = None

    def records(self):
        days = []
        for key, cell in self.cells.items():
            match = re.match(r'\s*(No|[\d,]+) contributions?\b', self.tooltips.get(key, ''))
            if not match:
                raise ValueError(f'Missing contribution count for {cell["date"]}; refusing to publish partial data.')
            count = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            days.append({**cell, 'count': count})
        return sorted(days, key=lambda item: item['date'])


def validate(days):
    if not 350 <= len(days) <= 380:
        raise ValueError(f'Unexpected calendar size: {len(days)}')
    parsed = [date.fromisoformat(day['date']) for day in days]
    if any(b-a != timedelta(days=1) for a, b in zip(parsed, parsed[1:])):
        raise ValueError('Contribution dates contain gaps or duplicates.')
    if any(day['level'] not in range(5) or day['count'] < 0 for day in days):
        raise ValueError('Invalid contribution data.')


def text(x, y, content, size=14, fill='#78859A', weight='400', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra}>{html.escape(str(content))}</text>'


def render(days, narrow=False, animated=True):
    end = date.fromisoformat(days[-1]['date'])
    cutoff = end - timedelta(days=364)
    year = [day for day in days if date.fromisoformat(day['date']) >= cutoff]
    recent = [day for day in days if date.fromisoformat(day['date']) >= end-timedelta(days=29)]
    width, height = (600, 344) if narrow else (1200, 384)
    parts = [f'<rect width="{width}" height="{height}" rx="4" fill="#F7F9FC"/>']
    values = [sum(day['count'] for day in year), sum(day['count'] for day in recent), sum(day['count'] > 0 for day in year)]
    labels = ['PAST YEAR', 'LAST 30 DAYS', 'ACTIVE DAYS / YEAR']
    for i, (value, label) in enumerate(zip(values, labels)):
        x = (32+i*190) if narrow else (52+i*382)
        if animated:
            parts.append(f'<g><animate attributeName="opacity" values="0;1" dur="{.65+i*.15:.2f}s" fill="freeze"/>')
        parts.append(text(x, 56 if narrow else 69, value, 39 if narrow else 54, '#343D52', '700'))
        parts.append(text(x, 80 if narrow else 99, label, 11 if narrow else 14, extra='letter-spacing="1"'))
        if animated:
            parts.append('</g>')
    parts.append(f'<path d="M{32 if narrow else 52} {103 if narrow else 126}H{width-(32 if narrow else 52)}" stroke="#DBE3EF"/>')
    if animated:
        rule_x, rule_y = (32, 103) if narrow else (52, 126)
        travel = width-rule_x*2-64
        parts.append(f'<rect x="{rule_x}" y="{rule_y-1}" width="64" height="2" rx="1" fill="#25ADD4" opacity=".8"><animate attributeName="x" values="{rule_x};{rule_x+travel};{rule_x}" keyTimes="0;.5;1" dur="9s" calcMode="spline" keySplines=".42 0 .58 1;.42 0 .58 1" repeatCount="indefinite"/></rect>')
    # Week columns start on Sunday, matching GitHub's own calendar.
    first = date.fromisoformat(days[0]['date'])
    start = first-timedelta(days=(first.weekday()+1)%7)
    if narrow:
        start = end-timedelta(days=(end.weekday()+1)%7)-timedelta(weeks=25)
    step, box, left, top = (20, 15, 48, 152) if narrow else (20, 15, 80, 184)
    shown = [day for day in days if date.fromisoformat(day['date']) >= start]
    seen_month = None
    last_label_x = -100
    active_positions = []
    for day in shown:
        when = date.fromisoformat(day['date'])
        offset = (when-start).days
        x, y = left+(offset//7)*step, top+(offset%7)*step
        if (when.year, when.month) != seen_month:
            seen_month = (when.year, when.month)
            if x-last_label_x >= 55:
                parts.append(text(x, top-16, when.strftime('%b'), 12 if narrow else 14))
                last_label_x = x
        reveal = ''
        if animated:
            delay = (offset//7)*.028
            reveal = f'<animate attributeName="opacity" values=".28;.28;1" keyTimes="0;{max(.001,delay/(delay+.65)):.4f};1" dur="{delay+.65:.3f}s" fill="freeze"/>'
        parts.append(f'<rect data-date="{day["date"]}" data-count="{day["count"]}" x="{x}" y="{y}" width="{box}" height="{box}" rx="3" fill="{COLORS[day["level"]]}"><title>{day["date"]}: {day["count"]} contributions</title>{reveal}</rect>')
        if day['count'] > 0 and when >= end-timedelta(days=29):
            active_positions.append((x, y, day['date']))
    if animated:
        columns = (end-start).days//7+1
        grid_width = (columns-1)*step+box
        grid_height = 6*step+box
        parts.append(f'<defs><clipPath id="calendar-area"><rect x="{left-3}" y="{top-3}" width="{grid_width+6}" height="{grid_height+6}" rx="4"/></clipPath><linearGradient id="scan"><stop stop-color="#6ECBE4" stop-opacity="0"/><stop offset=".7" stop-color="#6ECBE4" stop-opacity=".24"/><stop offset="1" stop-color="#D88EB8" stop-opacity="0"/></linearGradient></defs>')
        parts.append(f'<g clip-path="url(#calendar-area)"><rect x="{left-100}" y="{top-3}" width="100" height="{grid_height+6}" fill="url(#scan)"><animate attributeName="x" values="{left-100};{left+grid_width+20};{left+grid_width+20}" keyTimes="0;.7;1" dur="8s" repeatCount="indefinite"/></rect></g>')
        for i, (x, y, day_date) in enumerate(active_positions[-3:]):
            parts.append(f'<rect data-pulse-date="{day_date}" x="{x-2}" y="{y-2}" width="{box+4}" height="{box+4}" rx="5" fill="none" stroke="#BA79AB" stroke-width="1.4" opacity=".2"><animate attributeName="opacity" values=".15;.85;.15" keyTimes="0;.5;1" dur="{2.8+i*.35:.2f}s" repeatCount="indefinite"/></rect>')
    if not narrow:
        for row, label in [(1,'Mon'), (3,'Wed'), (5,'Fri')]:
            parts.append(text(34, top+row*step+12, label, 12))
    label = '26 WEEKS' if narrow else 'PUBLIC CONTRIBUTION CALENDAR'
    parts.append(text(32 if narrow else 52, height-28, label, 10 if narrow else 12, extra='letter-spacing="1"'))
    parts.append(text(width-(32 if narrow else 52), height-28, f'AS OF {end.isoformat()}', 10 if narrow else 12, extra='text-anchor="end"'))
    description = f'{USER}: {values[0]} contributions in the past year, {values[1]} in the last 30 days, {values[2]} active days. Data through {end.isoformat()}.'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{description}</title><g font-family="Arial,sans-serif">{"".join(parts)}</g></svg>'


def fetch():
    request = Request(URL, headers={'User-Agent':'GitHub-Profile-Calendar/1.0', 'Accept-Language':'en-US,en;q=0.9'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode('utf-8')
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2**attempt)


def main():
    parser = ArgumentParser()
    parser.add_argument('--html', type=Path, help='Use an already downloaded calendar for offline verification.')
    args = parser.parse_args()
    calendar = CalendarParser()
    calendar.feed(args.html.read_text() if args.html else fetch())
    days = calendar.records()
    validate(days)
    # Generate everything before replacing the last successful snapshot.
    outputs = {
        'activity.svg':render(days),
        'activity-mobile.svg':render(days, True),
        'activity-static.svg':render(days, animated=False),
        'activity-mobile-static.svg':render(days, True, animated=False),
    }
    outputs['activity-data.json'] = json.dumps({'user':USER,'source':URL,'through':days[-1]['date'],'days':days}, indent=2)+'\n'
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        destination = OUT/name
        temp = destination.with_suffix(destination.suffix+'.tmp')
        temp.write_text(content)
        temp.replace(destination)
    print(f'Updated {USER}: {len(days)} contribution days through {days[-1]["date"]}.')


if __name__ == '__main__':
    main()
