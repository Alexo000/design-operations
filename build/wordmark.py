"""wordmark.py — 2026-10-15 (work lane). The Actionary name as drawn on the identity canvas, board G:
ACTIONARY in small capitals, each letter in an equal cell under one operation symbol. The symbols are
drawn at random on every visit, nine different ones, from the symbols that are close to square
(width over height between 0.7 and 1.4), each kept at its own proportions and drawn with heavier lines
so it reads at header size. No rule ties a symbol to its letter.

Writes into site/: wordmark-symbols.svg (one sheet holding those symbols, each reachable as
wordmark-symbols.svg#<slug>), favicon.svg and favicon-32.png (the A built from squares).
Gives the explorer and the operation pages the same markup, styles and script."""
import os, re, random

LO, HI = 0.7, 1.4
SHEET = '/wordmark-symbols.svg'
LETTERS = 'ACTIONARY'
NAME = 'Actionary'
TAGLINE = 'Things to do to your work'

# the A built from squares, 5 by 7, white on black (identity canvas, board D)
A_ROWS = ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#']
FAVICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#161616"/>'
               + ''.join(f'<rect x="{7 + c * 3.6:.1f}" y="{3.4 + r * 3.6:.1f}" width="2.9" height="2.9" fill="#fff"/>'
                         for r, row in enumerate(A_ROWS) for c, v in enumerate(row) if v == '#')
               + '</svg>')

CSS = """
    /* wordmark 2026-10-15 */
    .wordmark { display:inline-flex; flex-direction:column; gap:10px; color:var(--ink); text-decoration:none; }
    .wm-row { display:grid; grid-template-columns:repeat(9, 42px); margin-left:-8px; }
    .wm-cell { display:grid; grid-template-rows:26px auto; row-gap:8px; justify-items:center; align-items:end; }
    .wm-cell img { width:26px; height:26px; object-fit:contain; display:block; }
    .wm-cell span { font-size:13px; font-weight:500; line-height:1; letter-spacing:0; }
    .wm-tag { font-size:15px; font-weight:400; color:var(--muted); letter-spacing:0; }
    .wm-sr { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
    @media (max-width:420px) {
      .wm-row { grid-template-columns:repeat(9, 35px); margin-left:-6px; }
      .wm-cell { grid-template-rows:22px auto; }
      .wm-cell img { width:22px; height:22px; }
    }
"""


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r"['’]", '', str(name).lower())).strip('-')


def _bold(svg):
    svg = re.sub(r'stroke-width="([\d.]+)"',
                 lambda m: 'stroke-width="%.2f"' % (float(m.group(1)) * 2.4) if float(m.group(1)) > 0 else m.group(0), svg)
    return re.sub(r'(<circle[^>]*?) r="([\d.]+)"', lambda m: '%s r="%.2f"' % (m.group(1), max(float(m.group(2)), 1.6)), svg)


def sheet(records):
    """The symbol sheet and the slugs it holds, in register order."""
    views, groups, slugs, y = [], [], [], 0.0
    for r in sorted(records, key=lambda r: r['index']):
        svg = r['locked'].get('symbol') or ''
        m = re.search(r'viewBox="([^"]+)"', svg)
        if not m:
            continue
        x0, y0, w, h = [float(v) for v in m.group(1).split()]
        if not (LO <= w / h <= HI):
            continue
        s = slug(r['locked']['name'])
        inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', _bold(svg).strip()).replace('currentColor', '#161616')
        groups.append(f'<g transform="translate(0,{y - y0:.1f})">{inner}</g>')
        views.append(f'<view id="{s}" viewBox="{x0:.1f} {y:.1f} {w:.1f} {h:.1f}"/>')
        slugs.append(s)
        y += h + 20
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 0 200 {y:.0f}">' + ''.join(views) + ''.join(groups) + '</svg>'
    return svg, slugs


def html(slugs, link=None):
    """The wordmark. With link, it is a link home; without, a plain block (the explorer's own header)."""
    picks = random.Random(15).sample(slugs, len(LETTERS))   # what shows before the script runs, and without it
    cells = ''.join(f'<span class="wm-cell"><img src="{SHEET}#{p}" alt="" width="26" height="26"><span>{ch}</span></span>'
                    for ch, p in zip(LETTERS, picks))
    inner = (f'<span class="wm-sr">{NAME}</span><span class="wm-row" aria-hidden="true">{cells}</span>'
             f'<span class="wm-tag">{TAGLINE}</span>')
    if link:
        return f'<a class="wordmark" href="{link}">{inner}</a>'
    return f'<div class="wordmark">{inner}</div>'


def js(slugs):
    """Nine different symbols, drawn again on every visit."""
    return ('<script>\n(function(){\n  var S = ' + '[' + ','.join('"%s"' % s for s in slugs) + '];\n'
            "  var imgs = document.querySelectorAll('.wm-cell img'); if (!imgs.length) return;\n"
            '  var pool = S.slice();\n'
            '  imgs.forEach(function(img){ var i = Math.floor(Math.random() * pool.length);'
            " img.src = img.src.split('#')[0] + '#' + pool.splice(i, 1)[0]; });\n"
            '})();\n</script>\n')


def write_assets(out, records):
    svg, slugs = sheet(records)
    open(os.path.join(out, 'wordmark-symbols.svg'), 'w', encoding='utf-8').write(svg)
    open(os.path.join(out, 'favicon.svg'), 'w', encoding='utf-8').write(FAVICON_SVG)
    try:   # a PNG beside the SVG for browsers that want one; drawn with Pillow when it is installed
        from PIL import Image, ImageDraw
        im = Image.new('RGBA', (128, 128), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, 127, 127], radius=24, fill=(22, 22, 22, 255))
        for r, row in enumerate(A_ROWS):
            for c, v in enumerate(row):
                if v == '#':
                    x, y = 28 + c * 14.4, 13.6 + r * 14.4
                    d.rectangle([x, y, x + 11.6, y + 11.6], fill=(255, 255, 255, 255))
        im.resize((32, 32), Image.LANCZOS).save(os.path.join(out, 'favicon-32.png'))
    except ImportError:
        pass
    return slugs
