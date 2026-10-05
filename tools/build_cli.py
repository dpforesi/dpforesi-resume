"""Build the text-mode site for CLI browsers (lynx, w3m, links) from RESUME_DATA in index.html.

Writes:
  - the #cli main-menu screen inside index.html (between the TEXT-MODE markers)
  - one page per menu screen in cli/*.html
  - cli/cli.css, copied from the TEXT MODE styles in index.html

Run after editing RESUME_DATA or the text-mode styles:  python3 tools/build_cli.py
"""
import html
import json
import os
import random
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
CLI_DIR = os.path.join(ROOT, 'cli')

src = open(INDEX, encoding='utf-8').read()
d = json.loads(re.search(r'const RESUME_DATA = (\{.*?\});\n', src).group(1))
e = html.escape

BOOK_BLURB = ('A dreamer, freelance shuttle pilot, and staunch advocate of minding his own damn business — '
  'Jeron Hayden finds himself drawn to Rieva, a tropical paradise inhabited by anarchists, sentient AI entities, '
  'ingenious inventors, and a race of time-agnostic aliens. When a technological singularity threatens total '
  'annihilation, Jeron must navigate a quantum-entangled dimension called the echoverse and embrace an esoteric '
  'alien philosophy known as eom.')
BLUEPRINT = [
  'Blueprint Synth enables developers to create reproducible synthetic data by defining features, population '
  'segments, and causal relationships between columns — then generating a pandas DataFrame in a single operation. '
  'It supports multiple data types (numeric, boolean, categorical, datetime, text, computed, derived), named '
  'population segments with conditional parameter overrides, and causal influences with customizable effect types.',
  'Key capabilities include topological dependency sorting for multi-hop relationships, deterministic '
  'reproducibility via seed control, rich effect specifications (per-unit additive, percentage-based, flat values, '
  'custom functions), and row-level noise injection. Output options include direct pandas DataFrame emission, CSV '
  'and JSON export, and JSON manifest generation for metadata documentation.',
]
GLYPHS = '░▒▓█▌▐▄▀αβγδεζηθλξπσφψω∑∏∆∇∂∫∞≠≈±×√⊕⊗⊥∴≡'

# (key, page, label) — mirrors the GUI main menu, minus GUI-only items (JSON views, sound, clear)
MENU = [
  ('A', 'resume', 'View Resume'),
  ('B', 'history', 'Work History'),
  ('C', 'skills', 'List Skills'),
  ('D', 'experience', 'Experience'),
  ('E', 'education', 'Education'),
  ('F', 'about', 'About'),
  ('G', 'books', 'Sci-Fi Works'),
  ('H', 'projects', 'GitHub Projects'),
  ('I', 'contact', 'Contact'),
]
BOOK = next(x['book'] for x in d['experience'] if 'book' in x)


def opts(items):
    """Lettered options; data-key lets cli.js route a typed letter to the link."""
    lines = '<br>\n'.join(f'&nbsp;&nbsp;<a data-key="{k}" href="{e(href)}">[{k}]&nbsp;&nbsp;{e(label)}</a>'
                           for k, href, label in items)
    return f'<p class="cli-opts">\n{lines}\n</p>'


def screen(cmd, title, body, options, root):
    menu_href = root + 'index.html?cli'
    if options is None:
        options = [('M', menu_href, 'Main menu')]
    return '\n'.join([
        f'<p class="cli-echo">guest@dpforesi:~$ {e(cmd)}</p>',
        '<hr>',
        f'<h2>{e(title)}</h2>',
        '<hr>',
        *([body, '<hr>'] if body else []),
        opts(options),
        '<div id="cli-prompt"><p>guest@dpforesi:~$ '
        '<span class="cli-hint">select an option above (arrow keys or Tab, then Enter)</span></p></div>',
    ])


def about_html():
    roles = ''.join(f'<li>{e(r)}</li>' for r in d['current_roles'])
    return (f'<p>{e(d["contact"]["name"])}<br>Las Vegas, NV / Cabo San Lucas, MX</p>'
            f'<p>{e(d["summary"])}</p><h3>Current Roles</h3><ul>{roles}</ul>')


def experience_html():
    out = []
    for x in d['experience']:
        out.append(f'<h3>{e(x["title"])}</h3>')
        out.append(f'<p>{e(x["organization"])}<br><i>{e(x["dates_display"])} | {e(x["location"])}</i></p>')
        out.append(f'<p>{e(x["narrative"])}</p>')
    return '\n'.join(out)


def skills_html(numbered=True):
    out = []
    for i, s in enumerate(d['skills'], 1):
        out.append(f'<h3>{f"[{i}] " if numbered else ""}{e(s["heading"])}</h3>')
        out.append(f'<p>{e(s["narrative"])}</p>')
        out.append(f'<p><i>tags: {e(", ".join(s["tags"]))}</i></p>')
    return '\n'.join(out)


def education_html():
    out = []
    for x in d['education']:
        out.append(f'<h3>{e(x["degree"])}' + (f' — {e(x["field"])}' if x.get('field') else '') + '</h3>')
        parts = [x['institution'], x.get('location'), x['dates_display']]
        out.append('<p><i>' + ' | '.join(e(p) for p in parts if p) + '</i></p>')
        if x.get('narrative'):
            out.append(f'<p>{e(x["narrative"])}</p>')
    return '\n'.join(out)


def history_html():
    rows = []
    for x in d['experience']:
        rows.append(e(x['dates_display']).ljust(22) + e(x['title']))
        rows.append(' ' * 22 + e(x['organization']))
        rows.append('')
    return '<pre>' + '\n'.join(rows).rstrip() + '</pre>'


def resume_html():
    loc = ''.join(f'<li>{e(l["city"])}, {e(l["state"])}, {e(l["country"])}</li>' for l in d['contact']['locations'])
    roles = ''.join(f'<li>{e(r)}</li>' for r in d['current_roles'])
    return '\n'.join([
        f'<h3>Locations</h3><ul>{loc}</ul>',
        f'<h3>Summary</h3><p>{e(d["summary"])}</p>',
        f'<h3>Current Roles</h3><ul>{roles}</ul>',
        '<hr><h2>Experience</h2><hr>', experience_html(),
        '<hr><h2>Skills</h2><hr>', skills_html(numbered=False),
        '<hr><h2>Education</h2><hr>', education_html(),
    ])


def books_html():
    return (f'<h3>{e(BOOK["title"])}</h3>'
            f'<p><i>{e(BOOK["subtitle"])}<br>{BOOK["pages"]:,} pages | Published July 2023 | Kindle Edition</i></p>'
            f'<p>{e(BOOK_BLURB)}</p>')


def projects_html():
    return ('<h3>Blueprint Synth</h3>'
            '<p><i>A Pure-Python Library for Generating Realistic Synthetic Datasets</i></p>'
            + ''.join(f'<p>{e(p)}</p>' for p in BLUEPRINT)
            + '<p><i>Python 3.10+ | Dependencies: numpy, pandas</i></p>')


def contact_html():
    rng = random.Random(7)  # stable output between builds
    scramble = lambda n: ''.join(rng.choice(GLYPHS) for _ in range(n))
    c = d['contact']
    return (f'<div id="cli-contact-body" data-email="{e(json.dumps(c["encoded_email"]))}" '
            f'data-phone="{e(json.dumps(c["encoded_phone"]))}">'
            f'<p>EMAIL: {scramble(len(c["encoded_email"]))}</p>'
            f'<p>PHONE: {scramble(len(c["encoded_phone"]))}</p></div>'
            '<p>This contact information is shared in good faith.<br>'
            'To reveal it, type the following pledge at the prompt:</p>'
            '<p>&gt; I will not spam</p>'
            '<p><i>(the prompt needs JavaScript — in lynx/w3m use the '
            '<a href="../index.html?gui">interactive terminal</a> in a graphical browser)</i></p>')


def page(cmd, title, body, options=None):
    root = '../'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>dpforesi — {e(title.lower())}</title>
  <link rel="stylesheet" href="cli.css" />
</head>
<body>
<!-- generated by tools/build_cli.py — edit RESUME_DATA in index.html and rebuild -->
<div id="cli" data-root="{root}">
<p class="cli-switch">DPFORESI :: text-mode terminal — [ <a href="{root}index.html?gui">launch interactive terminal</a> ]</p>
{screen(cmd, title, body, options, root)}
</div>
<script src="cli.js"></script>
</body>
</html>
'''


menu_href = '../index.html?cli'
PAGES = {
    'resume': page('resume', 'Resume — ' + d['contact']['name'], resume_html()),
    'history': page('history', 'Work History', history_html()),
    'skills': page('skills', 'Skills & Expertise', skills_html()),
    'experience': page('experience', 'Work Experience', experience_html()),
    'education': page('education', 'Education', education_html()),
    'about': page('about', 'About', about_html()),
    'books': page('books', 'Sci-Fi Works', books_html(), [
        ('A', BOOK['url'], 'View on Amazon'),
        ('B', BOOK['d2d_url'], 'View on Draft2Digital'),
        ('M', menu_href, 'Main menu'),
    ]),
    'projects': page('projects', 'GitHub Projects', projects_html(), [
        ('A', 'https://github.com/dpforesi/blueprint-synth', 'View on GitHub'),
        ('M', menu_href, 'Main menu'),
    ]),
    'contact': page('contact', 'Contact', contact_html()),
}

os.makedirs(CLI_DIR, exist_ok=True)
for name, content in PAGES.items():
    with open(os.path.join(CLI_DIR, name + '.html'), 'w', encoding='utf-8') as f:
        f.write(content)

# cli.css: the TEXT MODE styles from index.html, minus the rules that toggle GUI/text mode
tokens = re.search(r':root \{.*?\}', src, re.S).group(0)
text_css = src[src.index('/* ─── TEXT MODE (#cli)'):src.index('</style>')]
text_css = '\n'.join(l for l in text_css.splitlines() if 'data-mode' not in l)
with open(os.path.join(CLI_DIR, 'cli.css'), 'w', encoding='utf-8') as f:
    f.write('/* generated by tools/build_cli.py from index.html — do not edit by hand */\n'
            f'{tokens}\n'
            '*, *::before, *::after { box-sizing: border-box; }\n'
            'body { margin: 0; background: var(--bg); color: var(--fg); '
            "font-family: 'Courier New', Courier, monospace; font-size: 14px; line-height: 1.6; }\n"
            f'{text_css.strip()}\n')

# main menu screen inside index.html
END_MARKER = '<!-- /TEXT-MODE VERSION -->'
menu = '\n'.join([
    '<!-- TEXT-MODE VERSION: rendered as-is by lynx/w3m/links and other no-JS browsers.',
    '     Generated by tools/build_cli.py from RESUME_DATA — rebuild if the resume data changes. -->',
    '<div id="cli" data-root="">',
    '<pre class="cli-banner">+------------------------------------------------+\n'
    '|  DPFORESI  ::  text-mode terminal              |\n'
    '+------------------------------------------------+</pre>',
    f'<h1>{e(d["contact"]["name"])}</h1>',
    '<p>Las Vegas, NV / Cabo San Lucas, MX</p>',
    '<p class="cli-switch">[ <a href="?gui">Launch the interactive terminal</a> ] '
    '(needs JavaScript + a graphical browser)</p>',
    screen('menu', 'Main Menu', '', [(k, f'cli/{p}.html', label) for k, p, label in MENU], ''),
    '</div>',
])
start = src.index('<!-- TEXT-MODE VERSION')
end = src.index(END_MARKER) + len(END_MARKER)
src = src[:start] + menu + '\n' + END_MARKER + src[end:]
with open(INDEX, 'w', encoding='utf-8') as f:
    f.write(src)

print(f'wrote index.html menu, cli.css and {len(PAGES)} screens in cli/')
