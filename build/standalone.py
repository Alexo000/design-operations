"""standalone.py — 2026-10-11 (work lane, ruling 1a: the explorer gets its own full page at its own address,
and the Squarespace page links to it instead of embedding it).
Adds what a page needs once it stands alone: share tags (title, description, image), a tab icon,
a feedback link and a link back to ramos-saavedra.com in the footer. The share image is copied into site/.
SITE_URL is the explorer's own address; change it here or set it in the environment.
2026-10-15 (work lane, rulings 1a, 1b and 2b of that day): the collection is renamed Actionary, strapline
"Things to do to your work". The name lives here (TITLE, TAGLINE) and every visitor-facing use reads it from here."""
import os, shutil

SITE_URL = os.environ.get('SITE_URL', 'https://operations.ramos-saavedra.com').rstrip('/')
TITLE = 'Actionary'
TAGLINE = 'Things to do to your work'
DOC_TITLE = f'{TITLE}: {TAGLINE[0].lower() + TAGLINE[1:]}'
DESC = '144 operations you can try on any kind of work. Answer a few questions to find one for your situation, or browse them all.'
FEEDBACK = 'https://tally.so/r/QKgDo1'
HOME = 'https://www.ramos-saavedra.com/'

ICON = '/favicon.svg'   # the A built from squares (wordmark.py, 2026-10-15)
ICON_LINKS = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n  <link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">'

HEAD = f"""
  <meta name="description" content="{DESC}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{DOC_TITLE}">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:image" content="{SITE_URL}/share.png">
  <meta property="og:image:width" content="1500">
  <meta property="og:image:height" content="787">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{SITE_URL}/">
  {ICON_LINKS}
  <meta name="theme-color" content="#f7f7f3">
"""

OLD_FOOT_LINE = '<p>Built from the Compendium of 11 October 2026 · © 2026 Alejandro Ramos Saavedra</p>'
NEW_FOOT_LINE = (f'<p class="foot-ask">Tried one? <a href="{FEEDBACK}" target="_blank" rel="noopener">Tell me how it went</a>.</p>'
                 f'<p class="foot-ask"><a href="{SITE_URL}/all/">Every operation on one page</a></p>'
                 f'<p>Built from the Compendium of 11 October 2026 · © 2026 <a href="{HOME}">Alejandro Ramos Saavedra</a></p>')

CSS = """
    .explorer-foot a { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }
    .explorer-foot .foot-ask { color:var(--ink); font-size:16px; margin-bottom:14px; }
    .explorer-foot p { max-width:none; }
    h1 { font-size:clamp(30px,5vw,40px); }
"""


def patch_html(npage, rep, wm_slugs):
    import wordmark
    npage = rep(npage, '<title>Design Operations</title>', f'<title>{DOC_TITLE}</title>' + HEAD, 'share tags')
    npage = rep(npage, '<div class="brand">Design Operations</div>', wordmark.html(wm_slugs), 'wordmark')
    npage = npage.replace('</body>', wordmark.js(wm_slugs) + '</body>', 1)
    npage = npage.replace("Design Operations — ", f"{TITLE} · ")
    npage = rep(npage, '"title": "Design Operations"', f'"title": "{TITLE}"', 'register title')
    npage = rep(npage, OLD_FOOT_LINE, NEW_FOOT_LINE, 'footer links')
    import wordmark
    npage = npage.replace('</style>', CSS + wordmark.CSS + '  </style>', 1)
    return npage


def copy_share(root, out):
    shutil.copyfile(os.path.join(root, 'assets', 'social', 'Actionary-144.png'), os.path.join(out, 'share.png'))
