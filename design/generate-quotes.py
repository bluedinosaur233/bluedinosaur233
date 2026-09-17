"""Generate portable, script-free SVG typing slides for a GitHub README."""
from pathlib import Path
import html
import json
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/profile-v2'
QUOTES = json.loads((ROOT / 'design/quotes.json').read_text())


def advance(char, size):
    return size * (1.12 if unicodedata.east_asian_width(char) in ('W', 'F') else .61)


def layout(quote, narrow):
    size = 34 if len(quote) < 20 else 30
    if narrow:
        breaks = {
            QUOTES[0]: ['醉后不知天在水，', '满船清梦压星河'],
            QUOTES[1]: ['黑客也是创作者，', '与画家、建筑师、', '作家一样'],
        }
        lines = breaks.get(quote, [quote])
        size = 34
    else:
        lines = [quote]
    width, height = (600, 176) if narrow else (960, 100)
    positions = []
    for row, line in enumerate(lines):
        x = (width - sum(advance(c, size) for c in line)) / 2
        y = (height - (len(lines)-1)*47)/2 + size*.32 + row*47
        for char in line:
            positions.append((char, round(x, 2), round(y, 2), size))
            x += advance(char, size)
    return positions


# Identical timing for desktop and mobile layouts.
timeline = []
time = .4
for quote in QUOTES:
    start = time
    arrivals = []
    for char in quote:
        time += .20 if unicodedata.east_asian_width(char) in ('W', 'F') else .13
        arrivals.append(time)
        if char in '，、,.':
            time += .32
    time += 2.5
    timeline.append((start, arrivals, time))
    time += .6
DURATION = round(time, 3)


def native_latin(quote, slide, width, positions, arrivals, end, animated):
    """Keep Latin glyphs in one text run so the font supplies actual advances."""
    spans = []
    for i, char in enumerate(quote):
        animation = ''
        if animated:
            animation = f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{arrivals[i]/DURATION:.6f};{end/DURATION:.6f};1" dur="{DURATION}s" calcMode="discrete" repeatCount="indefinite"/>'
        spans.append(f'<tspan opacity="{1 if slide==0 else 0}">{html.escape(char)}{animation}</tspan>')
    if animated:
        visibility = f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{arrivals[-1]/DURATION:.6f};{end/DURATION:.6f};1" dur="{DURATION}s" calcMode="discrete" repeatCount="indefinite"/>'
        spans.append(f'<tspan opacity="0">{visibility}<tspan dx="4" fill="#7E88B3">|<animate attributeName="opacity" values="1;0;1" keyTimes="0;.5;1" dur=".8s" calcMode="discrete" repeatCount="indefinite"/></tspan></tspan>')
    return f'<text x="{width/2}" y="{positions[0][2]}" font-size="{positions[0][3]}" text-anchor="middle" letter-spacing="1.2" xml:space="preserve">{"".join(spans)}</text>'


for narrow in (False, True):
    width, height = (600, 176) if narrow else (960, 100)
    for animated in (True, False):
        pieces = []
        for slide, quote in enumerate(QUOTES if animated else QUOTES[:1]):
            start, arrivals, end = timeline[slide]
            positions = layout(quote, narrow)
            if quote.isascii():
                pieces.append(native_latin(quote, slide, width, positions, arrivals, end, animated))
                continue
            for i, (char, x, y, size) in enumerate(positions):
                animation = ''
                if animated:
                    animation = f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{arrivals[i]/DURATION:.6f};{end/DURATION:.6f};1" dur="{DURATION}s" calcMode="discrete" repeatCount="indefinite"/>'
                pieces.append(f'<text x="{x}" y="{y}" font-size="{size}" opacity="{1 if slide==0 else 0}">{html.escape(char)}{animation}</text>')
            if animated:
                cursor = [(positions[0][1]-3, positions[0][2]-positions[0][3]+4)]
                for i, (char, x, y, size) in enumerate(positions):
                    if i+1 < len(positions) and positions[i+1][2] != y:
                        cursor.append((positions[i+1][1]-3, positions[i+1][2]-size+4))
                    else:
                        cursor.append((round(x+advance(char, size)-2, 2), y-size+4))
                cursor.append(cursor[-1])
                times = [0]+[v/DURATION for v in arrivals]+[1]
                keys = ';'.join(f'{v:.6f}' for v in times)
                movement = ''.join(f'<animate attributeName="{axis}" values="'+ ';'.join(str(p[j]) for p in cursor)+f'" keyTimes="{keys}" dur="{DURATION}s" calcMode="discrete" repeatCount="indefinite"/>' for j, axis in enumerate(('x','y')))
                visibility = f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{start/DURATION:.6f};{end/DURATION:.6f};1" dur="{DURATION}s" calcMode="discrete" repeatCount="indefinite"/>'
                pieces.append(f'<g opacity="0">{visibility}<rect x="{cursor[0][0]}" y="{cursor[0][1]}" width="2" height="32" fill="#7E88B3">{movement}<animate attributeName="opacity" values="1;0;1" keyTimes="0;.5;1" dur=".8s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
        decoration = '' if narrow else '<path d="M20 50h35m850 0h35" stroke="#BECDE0"/><path d="m72 50 4-4 4 4-4 4zm808 0 4-4 4 4-4 4z" fill="#B58FB5"/>'
        description = ' · '.join(QUOTES) if animated else QUOTES[0]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{html.escape(description)}</title><defs><linearGradient id="poem" gradientUnits="userSpaceOnUse" x1="80" x2="{width-80}"><stop stop-color="#4485AC"/><stop offset=".5" stop-color="#847EAE"/><stop offset="1" stop-color="#AE6D94"/></linearGradient></defs>{decoration}<g font-family="Songti SC,STSong,Noto Serif CJK SC,serif" fill="url(#poem)">{''.join(pieces)}</g></svg>'''
        suffix = ('-mobile' if narrow else '')+('' if animated else '-static')
        (OUT / f'poem{suffix}.svg').write_text(svg)

print(f'Generated {len(QUOTES)} typing slides; loop duration {DURATION}s.')
