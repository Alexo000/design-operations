"""noticed.py: pictures from the Aesthetic Catalogue on Actionary (2026-11-06).

Runs last in the build, and on its own: python3 build/noticed.py
It works on the finished pages in site/, so it needs none of the private sources.

  - a Noticed strip on each operation that has a catalogue plate, under Seen in;
  - /by-eye/, a way in by picture, with one plate for each of those operations, plus move plates
    for operations with no entry (build/moves.json), which show the move and appear only there;
  - links to /by-eye/ from the explorer, /all/ and each operation page;
  - /by-eye/ in the sitemap.

Catalogue entries are observations, so they stay apart from Seen in, which holds
canonic examples only. The symbols are untouched. Nothing here reads or changes the Compendium.

The plates stay on the catalogue's own site. build/noticed.json is a snapshot of which
plate goes with which operation. To refresh it after changing the catalogue:
  python3 build/noticed.py --from ../aesthetic-catalogue
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'noticed.json')
MOVES = os.path.join(HERE, 'moves.json')   # operations with no catalogue entry, drawn as the move: /by-eye/ only
SITE = 'https://operations.ramos-saavedra.com'
CAT = 'https://catalogue.ramos-saavedra.com'
BY_EYE = f'{SITE}/by-eye/'

# Linked on the catalogue, but too loose a fit to send people here from the picture.
LEAVE_OUT = {'compress'}

# The plate that stands for each operation on /by-eye/. Any operation not named takes its first.
CHOSEN = {
    'contain': 'prisms', 'cut-through': 'sliced', 'find-the-threshold': 'dark_substance', 'graft': 'marquetry',
    'isolate': 'niches', 'iterate': 'mirrors', 'juxtapose': 'wood_bronze', 'lay-over': 'paint_glass',
    'let-drift': 'drift', 'locate': 'gallery_angle', 'mirror': 'double_sym', 'partition': 'rot_wall', 'reframe': 'doorway',
    'reveal': 'candle', 'run-it-long': 'timelapse', 'translate': 'stacked_prisms', 'weather': 'drips',
    'work-the-gap': 'heavy',
}

CSS = """
    .noticed { margin:44px 0 0; }
    .noticed .head { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:baseline; gap:4px 24px; margin-bottom:14px; }
    .noticed h2 { margin:0; }
    .noticed .head a { font-size:14px; }
    .noticed .plates { display:grid; grid-template-columns:repeat(auto-fill, minmax(128px, 1fr)); gap:16px 12px; }
    .noticed figure { margin:0; }
    .noticed figcaption { margin-top:8px; font-size:14px; line-height:1.35; }
    .noticed.one figure { display:flex; flex-wrap:wrap; align-items:flex-end; gap:12px 16px; }
    .noticed.one figcaption { flex:1 1 200px; margin:0; max-width:34ch; }
    .noticed.one .plates { display:block; }
    .plate { display:block; width:128px; height:128px; image-rendering:pixelated; }
"""

EYE_CSS = """
    main { width:min(1120px, calc(100% - 32px)); }
    .eye { list-style:none; margin:40px 0 0; padding:0; display:grid; grid-template-columns:repeat(auto-fill, 128px); justify-content:space-between; gap:24px 16px; }
    .eye a { display:block; font-size:14px; line-height:1.3; text-decoration:none; }
    .eye a:hover { text-decoration:underline; }
    .eye .plate { margin-bottom:8px; }
    @media (max-width:320px) { .eye { justify-content:center; } }
"""

SHUFFLE = """<script>
(function(){var u=document.querySelector('.eye');for(var i=u.children.length;i>1;i--)u.appendChild(u.children[Math.floor(Math.random()*i)])})();
</script>
"""


def e(s):
    return html.escape(str(s), quote=True)


def refresh(repo):
    """Rewrite the snapshot from a checkout of the catalogue."""
    entries = json.load(open(os.path.join(repo, 'src', 'entries.json'), encoding='utf-8'))
    out = {}
    for x in entries:
        if not (x.get('slug') and x.get('plate')) or x['slug'] in LEAVE_OUT:
            continue
        gif = os.path.exists(os.path.join(repo, 'site', 'plates', x['plate'] + '.gif'))
        out.setdefault(x['slug'], {'name': x['op'], 'plates': []})['plates'].append(
            {'plate': x['plate'], 'file': x['plate'] + ('.gif' if gif else '.png'), 'moves': gif,
             'text': x['text'], 'alt': x['alt']})
    json.dump(out, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    moves = json.load(open(os.path.join(repo, 'src', 'moves.json'), encoding='utf-8'))
    json.dump(moves, open(MOVES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(out)


def picture(p):
    folder = p.get('dir', 'plates')
    src = f'{CAT}/{folder}/{p["file"]}'
    img = f'<img class="plate" src="{src}" alt="{e(p["alt"])}" width="128" height="128" loading="lazy" decoding="async">'
    if p['moves']:
        return (f'<picture><source media="(prefers-reduced-motion: reduce)" srcset="{CAT}/{folder}/{p["plate"]}-still.png">'
                f'{img}</picture>')
    return img


def strip(plates):
    figs = ''.join(f'<figure>{picture(p)}<figcaption>{e(p["text"])}</figcaption></figure>' for p in plates)
    cls = 'noticed one' if len(plates) == 1 else 'noticed'
    return (f'<!--noticed--><section class="{cls}"><div class="head"><h2>Noticed</h2>'
            f'<a href="{CAT}/">From the Aesthetic Catalogue</a></div><div class="plates">{figs}</div></section><!--/noticed-->\n')


def clean(page):
    """Take out anything an earlier run added, so that a second run changes nothing."""
    page = re.sub(r'<!--noticed-->.*?<!--/noticed-->\n?', '', page, flags=re.S)
    page = re.sub(r'/\*noticed\*/.*?/\*/noticed\*/\n?', '', page, flags=re.S)
    return re.sub(r'<!--eye-->.*?<!--/eye-->', '', page, flags=re.S)


def add_css(page, css):
    return page.replace('</style>', f'/*noticed*/{css}/*/noticed*/\n</style>', 1)


def op_page(page, plates):
    page = clean(page)
    if plates:
        page = add_css(page, CSS)
        block = strip(plates)
        for pat in (r'(<p class="seen">.*?</p>\n)', r'(<p class="ex">.*?</p>\n)', r'(<div class="hero">.*?</div></div>\n)'):
            page, n = re.subn(pat, lambda m: m.group(1) + block, page, count=1, flags=re.S)
            if n:
                break
        else:
            raise SystemExit('no place for the strip')
    anchor = f'<a href="{SITE}/">Find one for your situation</a>'
    assert anchor in page, 'operation page has changed'
    return page.replace(anchor, anchor + f'<!--eye--><a href="{BY_EYE}">Find one by eye</a><!--/eye-->', 1)


def eye_page(allpage, data):
    allpage = clean(allpage)
    moves = json.load(open(MOVES, encoding='utf-8'))
    n = len(data) + len(moves)
    title = 'Find one by eye · Actionary'
    desc = f'Pick the picture that pulls at you. {n} operations, each shown by a small animated plate.'
    a = allpage.index('</header>') + len('</header>\n')
    b = allpage.index('  <footer>')
    head, tail = allpage[:a], allpage[b:]
    head = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + e(desc), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + e(title), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + e(desc), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + BY_EYE, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + BY_EYE, head)
    head = add_css(add_css(head, CSS), EYE_CSS)
    items = ''
    for slug, op in data.items():
        want = CHOSEN.get(slug)
        p = next((x for x in op['plates'] if x['plate'] == want), op['plates'][0])
        items += f'<li><a href="{SITE}/{slug}/">{picture(p)}{e(op["name"])}</a></li>\n'
    for m in moves:
        p = {'plate': m['file'], 'file': m['file'] + '.gif', 'moves': True, 'alt': m['alt'], 'dir': 'moves'}
        items += f'<li><a href="{SITE}/{m["slug"]}/">{picture(p)}{e(m["name"])}</a></li>\n'
    body = ('  <h1 style="margin-top:56px">Find one by eye</h1>\n'
            '  <p class="lede">Pick the picture that pulls at you. It leads to something to do to your work. '
            f'Or <a href="{SITE}/">find one for your situation</a>.</p>\n'
            f'  <ul class="eye">\n{items}</ul>\n{SHUFFLE}')
    return head + body + tail


def apply(out='site'):
    data = json.load(open(DATA, encoding='utf-8'))
    done = 0
    for slug in sorted(os.listdir(out)):
        path = os.path.join(out, slug, 'index.html')
        if slug in ('all', 'by-eye') or not os.path.exists(path):
            continue
        page = op_page(open(path, encoding='utf-8').read(), (data.get(slug) or {}).get('plates') or [])
        open(path, 'w', encoding='utf-8').write(page)
        done += slug in data
    assert done == len(data), 'an operation in the snapshot has no page'

    path = os.path.join(out, 'all', 'index.html')
    allpage = clean(open(path, encoding='utf-8').read())
    os.makedirs(os.path.join(out, 'by-eye'), exist_ok=True)
    open(os.path.join(out, 'by-eye', 'index.html'), 'w', encoding='utf-8').write(eye_page(allpage, data))
    was = 'to find one for your situation.</p>'
    assert was in allpage, '/all/ has changed'
    allpage = allpage.replace(was, 'to find one for your situation.' f'<!--eye--> Or <a href="{BY_EYE}">find one by eye</a>.<!--/eye--></p>', 1)
    open(path, 'w', encoding='utf-8').write(allpage)

    path = os.path.join(out, 'index.html')
    page = clean(open(path, encoding='utf-8').read())
    was = '<button type="button" class="onb-next" id="onb-map">Browse all 144</button>'
    assert was in page, 'the explorer has changed'
    page = page.replace(was, was + f'<!--eye-->\n        <a class="onb-next" href="{BY_EYE}">Find one by eye</a><!--/eye-->', 1)
    page = add_css(page, '\n    .onb-actions a.onb-next { display:inline-flex; align-items:center; padding:14px 20px; font-size:16px; border:1px solid var(--line-strong); color:var(--ink); text-decoration:none; }\n    .onb-actions a.onb-next:hover { background:var(--selected); }\n    @media (max-width:640px) { .onb-actions a.onb-next { flex:1 1 100%; } }\n')
    open(path, 'w', encoding='utf-8').write(page)

    path = os.path.join(out, 'sitemap.xml')
    sm = open(path, encoding='utf-8').read()
    if BY_EYE not in sm:
        sm = sm.replace('</urlset>', f'  <url><loc>{BY_EYE}</loc></url>\n</urlset>')
        open(path, 'w', encoding='utf-8').write(sm)
    return done


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--from':
        print('operations in snapshot', refresh(sys.argv[2]))
    print('operations with plates', apply(os.path.join(os.path.dirname(HERE), 'site')))
