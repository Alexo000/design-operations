"""share_image.py — 2026-10-15: draws the share image (assets/social/Actionary-144.png) with the wordmark:
the name in small capitals under nine operation symbols, the strapline below, and the six example cards
on the right kept from the earlier image. Run by hand after a build, when the name or the look changes.

Usage: python3 build/share_image.py <folder holding IBMPlexSans-Regular.ttf and IBMPlexSans-Light.ttf>
Needs: Python with playwright and its Chromium (pip install playwright; python3 -m playwright install chromium).
The fonts come from the @ibm/plex-sans package, converted from WOFF to TTF with fonttools."""
import asyncio, base64, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wordmark

FONTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'fonts')
BASE = os.path.join(ROOT, 'assets', 'social', 'Design-Operations-144.png')   # supplies the cards on the right
OUT = os.path.join(ROOT, 'assets', 'social', 'Actionary-144.png')
SHEET = os.path.join(ROOT, 'site', 'wordmark-symbols.svg')


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


def page():
    import re
    sheet = open(SHEET, encoding='utf-8').read()
    items = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'<symbol id="wm-([^"]+)" viewBox="([^"]+)">(.*?)</symbol>', sheet, re.S)}
    picks = random.Random(15).sample(list(items), len(wordmark.LETTERS))
    cells = ''.join(f'<div class="c"><svg viewBox="{items[p][0]}">{items[p][1]}</svg><span>{ch}</span></div>' for ch, p in zip(wordmark.LETTERS, picks))
    return f"""<!doctype html><html><head><style>
@font-face {{ font-family:P; src:url(data:font/ttf;base64,{b64(os.path.join(FONTS, 'IBMPlexSans-Regular.ttf'))}); font-weight:400; }}
@font-face {{ font-family:P; src:url(data:font/ttf;base64,{b64(os.path.join(FONTS, 'IBMPlexSans-Light.ttf'))}); font-weight:300; }}
body {{ margin:0; width:1500px; height:787px; background:url(data:image/png;base64,{b64(BASE)}); font-family:P; color:#161616; }}
.left {{ position:absolute; left:0; top:0; width:760px; height:787px; background:#f7f7f3; }}
.row {{ position:absolute; left:72px; top:250px; display:grid; grid-template-columns:repeat(9, 68px); }}
.c {{ display:grid; grid-template-rows:52px auto; row-gap:16px; justify-items:center; align-items:end; }}
.c svg {{ width:52px; height:52px; display:block; overflow:visible; }}
.c span {{ font-size:22px; font-weight:400; line-height:1; }}
.rule {{ position:absolute; left:90px; top:400px; width:430px; height:3px; background:#161616; }}
.tag {{ position:absolute; left:90px; top:440px; font-size:58px; font-weight:300; line-height:70px; }}
</style></head><body><div class="left"></div><div class="row">{cells}</div><div class="rule"></div>
<div class="tag">Things to do<br>to your work</div></body></html>"""


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1500, 'height': 787})
        await pg.set_content(page())
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=OUT)
        await b.close()
    print('wrote', OUT)


asyncio.run(main())
