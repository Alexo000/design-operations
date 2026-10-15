"""pages.py — 2026-10-15 (work lane, ruling 3a of that day: rename and SEO work in one pass).
Writes what search engines need next to the explorer, all from the same register the explorer uses:
  - one plain page per operation at /<slug>/ (the same slug the explorer's #links use), with its own title,
    description, canonical address and the whole card in the HTML: name, line, symbol, example, Seen in,
    the tasks, How it has been used, Where it leads (linked), and a way into the explorer;
  - /all/, every operation on one page, grouped as in the collection map, so each page is one link from the home page;
  - sitemap.xml and robots.txt.
The explorer itself is untouched. Visitor wording on these pages is new and unratified."""
import html, json, os, re, datetime
from urllib.parse import quote

import standalone
import wordmark

WM_SLUGS = []   # set in write()

SITE = standalone.SITE_URL
NAME, TAGLINE, DOC_TITLE = standalone.TITLE, standalone.TAGLINE, standalone.DOC_TITLE
HOME_LABEL = 'Alejandro Ramos Saavedra'
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap">')
GOAT = '<script data-goatcounter="https://alexo000.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
TRIED = 'https://tally.so/r/QKgDo1'
EXAMPLE = 'https://tally.so/r/RGXJpK'
TASKS = [('hands', 'With your hands'), ('words', 'In words'), ('process', 'In the process'), ('general', 'Try this')]
RELATED = [('continueTo', 'If this lands, continue to'), ('alternative', 'If it doesn’t fit, try instead'),
           ('pairs', 'Works as a pair with'), ('escalation', 'To go further')]

CSS = """
    :root { color-scheme:light; --ink:#161616; --muted:#62625e; --line:#c8c8c1; --line-strong:#70706a; --paper:#f7f7f3; --focus:#2457d6; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--paper); color:var(--ink); font:400 17px/1.5 'IBM Plex Sans', Arial, sans-serif; }
    main { width:min(820px, calc(100% - 32px)); margin:0 auto; padding:30px 0 88px; }
    a { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }
    a:focus-visible { outline:3px solid var(--focus); outline-offset:2px; }
    .top { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:16px 24px; padding-bottom:20px; border-bottom:1px solid var(--ink); font-size:14px; }
    .hero { display:grid; grid-template-columns:1fr auto; gap:28px; align-items:start; margin:56px 0 0; }
    h1 { margin:0 0 14px; font-weight:400; font-size:clamp(32px,5.5vw,46px); line-height:1.05; letter-spacing:-.025em; }
    h2 { margin:0 0 14px; font-weight:400; font-size:15px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    p { max-width:62ch; }
    .line { margin:0; font-size:21px; line-height:1.4; }
    .formerly { margin:10px 0 0; color:var(--muted); font-size:14px; }
    .symbol { width:88px; color:var(--ink); }
    .symbol svg { width:100%; height:auto; max-height:150px; display:block; }
    .ex { margin:22px 0 0; color:var(--muted); }
    .seen { margin:8px 0 0; color:var(--muted); font-size:15px; }
    section { margin:48px 0 0; }
    .tasks { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; }
    .task { border:1px solid var(--line-strong); padding:18px; background:rgba(255,255,255,.4); }
    .task .label { display:flex; align-items:center; gap:8px; font-size:14px; color:var(--muted); }
    .task .label svg { width:18px; height:18px; flex:none; }
    .task .label svg path { fill:currentColor; }
    .task h3 { margin:10px 0 0; font-size:17px; font-weight:500; }
    .task p { margin:10px 0 0; }
    .related { list-style:none; margin:0; padding:0; display:grid; gap:8px; }
    .related li { display:flex; flex-wrap:wrap; gap:4px 12px; align-items:baseline; padding:12px 0; border-bottom:1px solid var(--line); }
    .related .rl { width:100%; font-size:14px; color:var(--muted); }
    .note { margin:40px 0 0; color:var(--muted); font-size:14px; }
    .go { display:flex; flex-wrap:wrap; gap:12px 28px; margin:44px 0 0; padding-top:22px; border-top:1px solid var(--ink); }
    .go .primary { display:inline-block; padding:12px 18px; border:1px solid var(--ink); text-decoration:none; }
    .go .primary:hover { background:#fff; }
    .pager { display:flex; justify-content:space-between; gap:16px; margin:36px 0 0; font-size:15px; }
    footer { margin-top:56px; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:14px; }
    footer p { max-width:none; margin:6px 0; }
    .group { margin:44px 0 0; }
    .group ul { list-style:none; margin:0; padding:0; }
    .group li { padding:12px 0; border-bottom:1px solid var(--line); }
    .group li a { font-size:19px; }
    .group li span { display:block; color:var(--muted); font-size:15px; }
    .lede { margin:18px 0 0; color:var(--muted); font-size:18px; }
    @media (max-width:560px) { .hero { grid-template-columns:1fr; } .symbol { width:64px; order:-1; } .pager { flex-direction:column; } }
"""


def slug(name):
    s = str(name).lower()
    s = re.sub(r"['’]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def display(name):
    return re.sub(r'(^|[\s/-])([a-z])', lambda m: m.group(1) + m.group(2).upper(), str(name).lower())


def e(s):
    return html.escape(str(s), quote=True)


def clause(text):
    first = text.split(';')[0].strip().rstrip('.')
    return first[:1].lower() + first[1:]


def title_for(rec):
    name = display(rec['locked']['name'])
    c = clause(rec['locked']['canonicalDefinition'])
    for t in (f'{name}: {c} · {NAME}', f'{name}: {c}'):
        if len(t) <= 70:
            return t
    return f'{name} · {NAME}: {TAGLINE.lower()}'


def desc_for(rec):
    d = rec['locked']['canonicalDefinition'].strip()
    ex = (rec['editorial'].get('compact') or {}).get('ex', '').strip()
    if ex and len(d) + len(ex) + 10 <= 158:
        d += ' Example: ' + ex
    elif len(d) + 36 <= 158:
        d += ' Three ways to try it on your work.'
    if len(d) > 158:
        d = d[:157].rsplit(' ', 1)[0].rstrip(',;:') + '…'
    return d


def head(title, desc, url, extra=''):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n'
            f'  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'  <title>{e(title)}</title>\n  <meta name="description" content="{e(desc)}">\n'
            f'  <link rel="canonical" href="{url}">\n'
            f'  <meta property="og:type" content="article">\n  <meta property="og:site_name" content="{NAME}">\n'
            f'  <meta property="og:title" content="{e(title)}">\n  <meta property="og:description" content="{e(desc)}">\n'
            f'  <meta property="og:url" content="{url}">\n  <meta property="og:image" content="{SITE}/share.png">\n'
            f'  <meta property="og:image:width" content="1500">\n  <meta property="og:image:height" content="787">\n'
            f'  <meta name="twitter:card" content="summary_large_image">\n'
            f'  {standalone.ICON_LINKS}\n  <meta name="theme-color" content="#f7f7f3">\n'
            f'  {FONT}\n  <style>{CSS}{wordmark.CSS}  </style>\n{extra}  {GOAT}\n</head>\n<body>\n<main>\n'
            f'  <header class="top">{wordmark.html(WM_SLUGS, link=SITE + "/")}'
            f'<a href="{SITE}/all/">All operations</a></header>\n')


def foot():
    return (f'  <footer><p>{NAME}: {TAGLINE.lower()}. © {datetime.date.today().year} '
            f'<a href="{standalone.HOME}">{HOME_LABEL}</a></p></footer>\n</main>\n' + wordmark.js(WM_SLUGS) + '</body>\n</html>\n')


def op_page(rec, by_name, order, pos, icons, meanings):
    L, ed = rec['locked'], rec['editorial']
    name = display(L['name'])
    s = slug(L['name'])
    url = f'{SITE}/{s}/'
    title, desc = title_for(rec), desc_for(rec)
    ld = {'@context': 'https://schema.org', '@type': 'DefinedTerm', 'name': name, 'description': L['canonicalDefinition'],
          'url': url, 'inDefinedTermSet': {'@type': 'DefinedTermSet', 'name': NAME, 'url': SITE + '/'}}
    extra = '  <script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'
    out = [head(title, desc, url, extra)]
    formerly = f'<p class="formerly">Formerly {e(display(ed["formerly"]))}</p>' if ed.get('formerly') else ''
    out.append(f'  <div class="hero"><div><h1>{e(name)}</h1><p class="line">{e(L["canonicalDefinition"])}</p>{formerly}</div>'
               f'<div class="symbol" aria-hidden="true">{L.get("symbol", "")}</div></div>\n')
    ex = (ed.get('compact') or {}).get('ex')
    if ex:
        out.append(f'  <p class="ex"><span aria-hidden="true">✓</span> {e(ex)}</p>\n')
    seen = ed.get('seenIn') or {}
    if seen.get('html'):
        inner = f'<a href="{e(seen["url"])}" rel="noopener">{seen["html"]}</a>' if seen.get('url') else seen['html']
        out.append(f'  <p class="seen">Seen in {inner}</p>\n')
    apps = ed.get('applications') or {}
    blocks = ''.join(f'<div class="task"><div class="label">{icons.get(label, "")}{e(label)}</div>'
                     + (f'<h3>{e(apps[k]["title"])}</h3>' if apps[k].get('title') else '')
                     + f'<p>{e(apps[k]["task"])}</p></div>'
                     for k, label in TASKS if (apps.get(k) or {}).get('task'))
    if blocks:
        out.append(f'  <section><h2>Try it on your work</h2><div class="tasks">{blocks}</div></section>\n')
    anec = ''.join(f'<p>{e(a)}</p>' for a in (ed.get('context') or {}).get('anecdotes', []))
    if anec:
        out.append(f'  <section><h2>How it has been used</h2>{anec}</section>\n')
    rel = ed.get('related') or {}
    items = ''
    for k, label in RELATED:
        for n in rel.get(k, []) or []:
            if str(n).upper() in by_name:
                items += f'<li><span class="rl">{e(label)}</span><a href="{SITE}/{slug(n)}/">{e(display(n))}</a></li>'
    if items:
        out.append(f'  <section><h2>Where it leads</h2><ul class="related">{items}</ul></section>\n')
    prof = L.get('profile') or {}
    m = prof.get('primaryMovement', '')
    out.append(f'  <p class="note">Grouped under <a href="{SITE}/all/#{slug(m)}">{e(meanings.get(m, display(m)))}</a></p>\n')
    q = '?operation=' + quote(name)
    out.append(f'  <div class="go"><a class="primary" href="{SITE}/#{s}">Open in the explorer</a>'
               f'<a href="{SITE}/">Find one for your situation</a>'
               f'<a href="{TRIED}{q}" rel="noopener">Tried it? Tell me how it went</a>'
               f'<a href="{EXAMPLE}{q}" rel="noopener">Know a better example?</a></div>\n')
    prev_r, next_r = order[pos - 1], order[(pos + 1) % len(order)]
    out.append(f'  <nav class="pager" aria-label="More operations"><a href="{SITE}/{slug(prev_r["locked"]["name"])}/">← {e(display(prev_r["locked"]["name"]))}</a>'
               f'<a href="{SITE}/{slug(next_r["locked"]["name"])}/">{e(display(next_r["locked"]["name"]))} →</a></nav>\n')
    out.append(foot())
    return s, ''.join(out)


def all_page(order, meanings):
    groups = {}
    for r in order:
        groups.setdefault(r['locked']['profile']['primaryMovement'], []).append(r)
    keys = sorted(groups, key=lambda m: meanings.get(m, m))
    title = f'All 144 operations · {NAME}'
    desc = f'Every operation in {NAME}, grouped by what it helps you do. Each one is a small thing you can do to your work.'
    out = [head(title, desc, f'{SITE}/all/')]
    out.append(f'  <h1 style="margin-top:56px">All {len(order)} operations</h1>\n'
               f'  <p class="lede">Grouped by what they help you do. Or <a href="{SITE}/">answer a few questions</a> to find one for your situation.</p>\n')
    for m in keys:
        lis = ''.join(f'<li><a href="{SITE}/{slug(r["locked"]["name"])}/">{e(display(r["locked"]["name"]))}</a>'
                      f'<span>{e(r["locked"]["canonicalDefinition"])}</span></li>' for r in groups[m])
        out.append(f'  <section class="group" id="{slug(m)}"><h2>{e(meanings.get(m, display(m)))}</h2><ul>{lis}</ul></section>\n')
    out.append(foot())
    return ''.join(out)


def write(out_dir, register, icons, npage):
    records = register['records']
    global WM_SLUGS
    WM_SLUGS = wordmark.sheet(records)[1]
    order = sorted(records, key=lambda r: r['index'])
    meanings = dict(re.findall(r"(\w+): '([^']*)'", re.search(r'movementMeanings = \{(.*?)\};', npage, re.S).group(1)))
    by_name = {r['locked']['name'].upper(): r for r in records}
    slugs = [slug(r['locked']['name']) for r in order]
    assert len(set(slugs)) == len(slugs), 'two operations share a slug'
    assert not set(slugs) & {'all', 'share.png', 'sitemap.xml', 'robots.txt'}, 'an operation slug clashes with a site path'
    for pos, rec in enumerate(order):
        s, page = op_page(rec, by_name, order, pos, icons, meanings)
        os.makedirs(os.path.join(out_dir, s), exist_ok=True)
        open(os.path.join(out_dir, s, 'index.html'), 'w', encoding='utf-8').write(page)
    os.makedirs(os.path.join(out_dir, 'all'), exist_ok=True)
    open(os.path.join(out_dir, 'all', 'index.html'), 'w', encoding='utf-8').write(all_page(order, meanings))
    today = datetime.date.today().isoformat()
    urls = [f'{SITE}/', f'{SITE}/all/'] + [f'{SITE}/{s}/' for s in slugs]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    open(os.path.join(out_dir, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
    open(os.path.join(out_dir, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    return len(slugs)
