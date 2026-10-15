"""share_image.py — 2026-10-15: redraws the left half of the share image with the new name and strapline.
Usage: python3 build/share_image.py assets/social/Design-Operations-144.png assets/social/Actionary-144.png <font folder>
The font folder must hold IBMPlexSans-Light.ttf (from the @ibm/plex-sans package, converted from WOFF with fonttools)."""
import sys
from PIL import Image, ImageDraw, ImageFont
src, out, fontdir = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert('RGB')
paper = im.getpixel((20, 20)); ink = (22, 22, 22)
d = ImageDraw.Draw(im)
d.rectangle([0, 0, 760, im.height], fill=paper)
light = ImageFont.truetype(f'{fontdir}/IBMPlexSans-Light.ttf', 128)
reg = ImageFont.truetype(f'{fontdir}/IBMPlexSans-Light.ttf', 58)
x = 90
d.text((x, 300), 'Actionary', font=light, fill=ink, anchor='ls')
d.rectangle([x, 410, x + 430, 413], fill=ink)
for i, line in enumerate(['Things to do', 'to your work']):
    d.text((x, 500 + i * 70), line, font=reg, fill=ink, anchor='ls')
im.save(out, optimize=True)
print(paper, im.size)
