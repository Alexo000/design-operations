"""wordmark.py — 2026-10-15 (work lane). The Actionary name as drawn on the identity canvas, board G:
ACTIONARY in small capitals, each letter in an equal cell under one operation symbol. The symbols are
drawn at random on every visit, nine different ones, from the symbols that are close to square
(width over height between 0.7 and 1.4), each kept at its own proportions and drawn with heavier lines
so it reads at header size. No rule ties a symbol to its letter.

Third cut, 2026-10-17: the symbols are the small set (set E, one glyph per operation drawn to read at
12 px, the one the explorer's lists use) in place of the full set A, drawn at their own weight and
slightly smaller than the cell (20 px in a 26 px box in the header), as chosen on the identity
canvas, board H. Still the near-square ones only (width over height 0.7 to 1.4).

How it is drawn (second cut, same day): every symbol is inline SVG. The page ships with nine symbols
already in place, so the name shows before any script runs and without one. A short script then
fetches wordmark-symbols.svg (one <symbol> per operation), adds it to the page out of sight and swaps
in nine new ones through <use>. The first cut cut symbols out of the sheet with image fragment
links, which Safari does not show; this way works in every current browser.

Writes into site/: wordmark-symbols.svg, favicon.svg and favicon-32.png (the A built from squares).
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
    .wm-cell svg { width:20px; height:20px; margin:3px; display:block; overflow:visible; }
    .wm-cell span { font-size:13px; font-weight:500; line-height:1; letter-spacing:0; }
    .wm-tag { font-size:15px; font-weight:400; color:var(--muted); letter-spacing:0; }
    .wm-sr { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
    @media (max-width:420px) {
      .wm-row { grid-template-columns:repeat(9, 35px); margin-left:-6px; }
      .wm-cell { grid-template-rows:22px auto; }
      .wm-cell svg { width:17px; height:17px; margin:2.5px; }
    }
"""


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r"['’]", '', str(name).lower())).strip('-')


def _bold(svg):
    svg = re.sub(r'stroke-width="([\d.]+)"',
                 lambda m: 'stroke-width="%.2f"' % (float(m.group(1)) * 2.4) if float(m.group(1)) > 0 else m.group(0), svg)
    return re.sub(r'(<circle[^>]*?) r="([\d.]+)"', lambda m: '%s r="%.2f"' % (m.group(1), max(float(m.group(2)), 1.6)), svg)


ITEMS = {}   # the wordmark's symbols, once write_assets has run


def symbols(records, small=None):
    """{slug: (viewBox, inner markup)} for the near-square symbols, in register order.
    small: {DO id: small-set svg}; without it, the records' full symbols, drawn heavier (the first cut)."""
    if small is None and ITEMS:
        return ITEMS
    out = {}
    for r in sorted(records, key=lambda r: r['index']):
        svg = (small or {}).get(r['id']) if small is not None else _bold(r['locked'].get('symbol') or '')
        m = re.search(r'viewBox="([^"]+)"', svg or '')
        if not m:
            continue
        x0, y0, w, h = [float(v) for v in m.group(1).split()]
        if LO <= w / h <= HI:
            inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip()).replace('currentColor', '#161616')
            out[slug(r['locked']['name'])] = (m.group(1), inner)
    return out


def sheet(items):
    return ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">'
            + ''.join(f'<symbol id="wm-{s}" viewBox="{vb}">{inner}</symbol>' for s, (vb, inner) in items.items())
            + '</svg>')


def html(items, link=None):
    """The wordmark, with nine symbols already in place. With link, a link home; without, a plain block."""
    picks = random.Random(15).sample(list(items), len(LETTERS))
    cells = ''.join(f'<span class="wm-cell"><svg viewBox="{items[p][0]}" aria-hidden="true" focusable="false">{items[p][1]}</svg>'
                    f'<span>{ch}</span></span>' for ch, p in zip(LETTERS, picks))
    inner = (f'<span class="wm-sr">{NAME}</span><span class="wm-row" aria-hidden="true">{cells}</span>'
             f'<span class="wm-tag">{TAGLINE}</span>')
    if link:
        return f'<a class="wordmark" href="{link}">{inner}</a>'
    return f'<div class="wordmark">{inner}</div>'


def js(items):
    """Nine different symbols, drawn again on every visit."""
    return ("<script>\n(function(){\n"
            "  var cells = document.querySelectorAll('.wm-cell'); if (!cells.length || !window.fetch) return;\n"
            "  fetch('" + SHEET + "').then(function(r){ return r.ok ? r.text() : ''; }).then(function(t){\n"
            "    if (!t) return;\n"
            "    var box = document.createElement('div'); box.setAttribute('aria-hidden', 'true');\n"
            "    box.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';\n"
            "    box.innerHTML = t; document.body.insertBefore(box, document.body.firstChild);\n"
            "    var pool = Array.prototype.slice.call(box.querySelectorAll('symbol'));\n"
            "    var NS = 'http://www.w3.org/2000/svg';\n"
            "    Array.prototype.forEach.call(cells, function(cell){\n"
            "      if (!pool.length) return;\n"
            "      var sym = pool.splice(Math.floor(Math.random() * pool.length), 1)[0];\n"
            "      var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', sym.getAttribute('viewBox'));\n"
            "      svg.setAttribute('aria-hidden', 'true'); svg.setAttribute('focusable', 'false');\n"
            "      var use = document.createElementNS(NS, 'use'); use.setAttribute('href', '#' + sym.id); svg.appendChild(use);\n"
            "      var old = cell.querySelector('svg'); if (old) cell.replaceChild(svg, old);\n"
            "    });\n"
            "  }).catch(function(){});\n"
            "})();\n</script>\n")


def write_assets(out, records, small=None):
    global ITEMS
    items = symbols(records, small)
    ITEMS = items
    open(os.path.join(out, 'wordmark-symbols.svg'), 'w', encoding='utf-8').write(sheet(items))
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
    return items
