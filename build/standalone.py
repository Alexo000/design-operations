"""standalone.py — 2026-10-11 (work lane, ruling 1a: the explorer gets its own full page at its own address,
and the Squarespace page links to it instead of embedding it).
Adds what a page needs once it stands alone: share tags (title, description, image), a tab icon,
a feedback link and a link back to ramos-saavedra.com in the footer. The share image is copied into site/.
SITE_URL is the explorer's own address; change it here or set it in the environment."""
import os, shutil

SITE_URL = os.environ.get('SITE_URL', 'https://operations.ramos-saavedra.com').rstrip('/')
TITLE = 'Design Operations'
DESC = '144 small moves you can try on any kind of work. Answer a few questions to find one for your situation, or browse them all.'
FEEDBACK = 'https://tally.so/r/QKgDo1'
HOME = 'https://www.ramos-saavedra.com/'

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' rx='6' fill='%23161616'/%3E"
        "%3Ctext x='16' y='21.5' font-family='Arial,Helvetica,sans-serif' font-weight='700' font-size='14' "
        "text-anchor='middle' fill='%23fff'%3EDO%3C/text%3E%3C/svg%3E")

HEAD = f"""
  <meta name="description" content="{DESC}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:image" content="{SITE_URL}/share.png">
  <meta property="og:image:width" content="1500">
  <meta property="og:image:height" content="787">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{SITE_URL}/">
  <link rel="icon" href="{ICON}">
  <meta name="theme-color" content="#f7f7f3">
"""

OLD_FOOT_LINE = '<p>Built from the Compendium of 2 October 2026 · © 2026 Alejandro Ramos Saavedra</p>'
NEW_FOOT_LINE = (f'<p class="foot-ask">Tried one? <a href="{FEEDBACK}" target="_blank" rel="noopener">Tell me how it went</a>.</p>'
                 f'<p>Built from the Compendium of 2 October 2026 · © 2026 <a href="{HOME}">Alejandro Ramos Saavedra</a></p>')

CSS = """
    .explorer-foot a { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }
    .explorer-foot .foot-ask { color:var(--ink); font-size:16px; margin-bottom:14px; }
"""


def patch_html(npage, rep):
    npage = rep(npage, '<title>Design Operations</title>', '<title>Design Operations</title>' + HEAD, 'share tags')
    npage = rep(npage, OLD_FOOT_LINE, NEW_FOOT_LINE, 'footer links')
    npage = npage.replace('</style>', CSS + '  </style>', 1)
    return npage


def copy_share(root, out):
    shutil.copyfile(os.path.join(root, 'assets', 'social', 'Design-Operations-144.png'), os.path.join(out, 'share.png'))
