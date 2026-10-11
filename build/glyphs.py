from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import json
f=TTFont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'); cmap=f.getBestCmap(); gs=f.getGlyphSet()
cps=[0x261E,0x261B,0x270D,0x270E,0x2710,0x2712,0x2699,0x21BB,0x27F3,0x2702,0x275D,0x270B,0x270C,0x2766,0x2740,0x273F,0x2726,0x2736,0x2732,0x263C,0x2672,0x267A,0x21C4,0x2194,0x2707,0x2701,0x2709,0x231A,0x2318]
out={}; cells=''
for cp in cps:
    if cp not in cmap: print('missing',hex(cp)); continue
    g=gs[cmap[cp]]; bp=BoundsPen(gs); g.draw(bp)
    if not bp.bounds: print('empty',hex(cp)); continue
    x0,y0,x1,y1=bp.bounds; pen=SVGPathPen(gs); g.draw(pen)
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d"><path transform="scale(1,-1)" d="%s" fill="currentColor"/></svg>'%(x0,-y1,x1-x0,y1-y0,pen.getCommands())
    out[hex(cp)]=svg
    sv=svg.replace('<svg ','<svg style="height:40px;width:48px" ')
    cells+='<div style="display:inline-block;margin:10px;text-align:center">%s<br>%s</div>'%(sv,hex(cp))
json.dump(out,open('glyphs.json','w'))
open('glyphs.html','w').write('<html><body style="background:#fff;font:11px monospace">%s</body></html>'%cells)
