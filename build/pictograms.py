"""pictograms.py — small pictograms for the ways in and every answer on the question screens (2026-10-11, work lane).
First the ways in and each route's first question (P); then the 25 groups (G, reusable by the map and the field), the
follow-up answers, starting points and practical limits (F).
Drawn in the symbols' vocabulary (dots, squares, bars, arrows) on a 48 x 32 grid, one stroke weight, ink only.
They describe the visitor's situation; they are not operation symbols, and they sit lighter than them.
Keys are the exact visible answer texts, so a reworded answer simply loses its pictogram until redrawn."""
import math

SW = 1.6


def _svg(body):
    return ('<svg viewBox="0 0 48 32" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
            f'stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def dot(x, y, r=2.4, op=None):
    o = f' opacity="{op}"' if op else ''
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="currentColor" stroke="none"{o}/>'


def ring(x, y, r, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{x}" cy="{y}" r="{r}"{d}/>'


def sq(x, y, s=6, fill=True, h=None):
    h = h or s
    return f'<rect x="{x}" y="{y}" width="{s}" height="{h}"' + (' fill="currentColor" stroke="none"/>' if fill else '/>')


def box(x, y, w, h, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{d}/>'


def line(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}"/>'


def arrow(x1, y1, x2, y2, head=4.2):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    px, py = -math.sin(a) * head * .55, math.cos(a) * head * .55
    tri = f'<path d="M{x2:.1f} {y2:.1f} L{bx + px:.1f} {by + py:.1f} L{bx - px:.1f} {by - py:.1f} Z" fill="currentColor" stroke="none"/>'
    return line(x1, y1, f'{bx:.1f}', f'{by:.1f}') + tri


def cross(x, y, s=3.2):
    return line(x - s, y - s, x + s, y + s) + line(x - s, y + s, x + s, y - s)


NONE = _svg(box(13, 7, 22, 18, dash='2.5 2.5'))

P = {
    # ways in
    'Something needs fixing': _svg(sq(5, 13) + line(11, 16, 21, 16) + line(27, 20, 37, 20) + sq(37, 17)),
    'I want to make something happen': _svg(ring(9, 16, 4) + arrow(16, 16, 31, 16) + dot(38, 16, 4.6)),
    'I’m just looking around': _svg(dot(8, 10, 2) + dot(17, 22, 3) + dot(27, 9, 1.6) + dot(35, 19, 2.4) + dot(42, 8, 1.4)),
    'Browse the whole collection': _svg(''.join(sq(7 + i * 9, 7 + j * 10, 6, fill=(i, j) in ((1, 0), (3, 1))) for i in range(4) for j in range(2))),
    # something needs fixing
    'There isn’t enough': _svg(box(8, 6, 32, 20, dash='2.5 2.5') + dot(24, 16, 2.2)),
    'There’s too much': _svg(box(12, 6, 22, 20) + ''.join(dot(16.5 + i * 4.3, 10.5 + j * 5.5, 1.5) for i in range(4) for j in range(3)) + dot(38, 9, 1.5) + dot(41, 15, 1.5) + dot(38, 21, 1.5)),
    'I’m stuck in familiar territory': _svg('<path d="M31.5 11.5 A9 9 0 1 0 33 18.5"/>' + '<path d="M33.8 8.2 L32.6 13.4 L28.2 10.6 Z" fill="currentColor" stroke="none"/>' + dot(24, 16, 2)),
    'I can’t tell what’s going on': _svg(dot(10, 11, 2.2, .3) + dot(19, 21, 2.6, .3) + dot(27, 10, 2, .3) + dot(36, 20, 2.4, .3) + dot(41, 10, 1.8, .3) + dot(24, 16, 2.4)),
    'Things aren’t lining up': _svg(sq(9, 9, 4, h=14) + sq(17, 13, 4, h=14) + sq(25, 6, 4, h=14) + sq(33, 11, 4, h=14) + line(6, 30, 42, 30)),
    'People or parts are getting in each other’s way': _svg(arrow(5, 16, 22, 16) + arrow(43, 16, 26, 16)),
    'Something keeps going wrong': _svg(cross(12, 16) + cross(24, 16) + cross(36, 16)),
    'Things are changing': _svg(sq(6, 12, 8) + '<path d="M24 11.5 L28.6 19.8 L19.4 19.8 Z" fill="currentColor" stroke="none"/>' + dot(38, 16, 4.2)),
    'I can’t get this finished': _svg(line(5, 16, 30, 16) + '<path d="M40 8 L40 24" stroke-width="2.6"/>'),
    'None of these feels close': NONE,
    # i want to make something happen
    'Make it different': _svg(sq(6, 11, 10) + arrow(20, 16, 31, 16) + dot(38, 16, 5)),
    'Make more or open it up': _svg('<path d="M22 8 H10 V24 H22"/>' + dot(28, 10, 1.8) + dot(33, 16, 2) + dot(28, 22, 1.8) + dot(39, 16, 1.6)),
    'Change what can be seen or understood': _svg(ring(5, 16, 2.2) + ring(13, 16, 2.2) + dot(24, 16, 2.6) + ring(24, 16, 6) + ring(35, 16, 2.2) + ring(43, 16, 2.2)),
    'Bring things together': _svg(dot(5, 16, 2.4) + arrow(9, 16, 18, 16) + dot(24, 16, 4.4) + arrow(39, 16, 30, 16) + dot(43, 16, 2.4)),
    'Break things apart or narrow the field': _svg(sq(9, 9, 11, h=14) + sq(28, 9, 11, h=14) + '<path d="M24 5 L24 27" stroke-dasharray="2 2.5"/>'),
    'Get it moving or finished': _svg(arrow(5, 16, 35, 16) + '<path d="M40 8 L40 24" stroke-width="2.6"/>'),
    # i'm just looking around
    'Choose for me': _svg(box(13, 5, 22, 22) + dot(18.5, 10.5, 1.9) + dot(24, 16, 1.9) + dot(29.5, 21.5, 1.9)),
    'Quick': _svg(line(5, 11, 13, 11) + line(3, 16, 13, 16) + line(5, 21, 13, 21) + arrow(18, 16, 42, 16)),
    'Strange': _svg(box(9, 9, 18, 18) + dot(29, 9, 5)),
    'Useful': _svg('<path d="M13 16.5 L20.5 24 L35 8.5" stroke-width="2"/>'),
    'Risky': _svg(line(7, 27, 41, 27) + '<path d="M15.5 6 L32.5 6 L24 26.2 Z"/>'),
    'Clarifying': _svg(ring(24, 16, 9) + dot(24, 16, 2.2) + line(24, 2.5, 24, 6) + line(24, 26, 24, 29.5) + line(10.5, 16, 14, 16) + line(34, 16, 37.5, 16)),
    'Generative': _svg(dot(8, 16, 2.6) + line(10.5, 16, 24, 7) + line(10.5, 16, 24, 16) + line(10.5, 16, 24, 25) + dot(24, 7, 2) + dot(24, 16, 2) + dot(24, 25, 2) + line(26, 7, 38, 4) + line(26, 7, 38, 10) + dot(39.5, 4, 1.5) + dot(39.5, 10, 1.5)),
    'Social': _svg(line(12, 10, 24, 6) + line(24, 6, 36, 12) + line(12, 10, 18, 24) + line(18, 24, 32, 25) + line(32, 25, 36, 12) + line(24, 6, 18, 24) + dot(12, 10) + dot(24, 6) + dot(36, 12) + dot(18, 24) + dot(32, 25)),
    'Solitary': _svg(ring(24, 16, 11, dash='1.5 3') + dot(24, 16, 2.8)),
}


def arc(cx, cy, r, a0, a1, head=False):
    """arc from angle a0 to a1 (degrees, 0 = right, clockwise in screen space)"""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    out = f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"/>'
    if head:
        t = math.radians(a1 + 90)
        hx, hy = x1 + 4 * math.cos(t), y1 + 4 * math.sin(t)
        out += arrow(x1 - 0.01 * math.cos(t), y1 - 0.01 * math.sin(t), hx, hy, head=4)
    return out


def tri(x, y, s=8, fill=True, down=False):
    h = s * .87
    pts = f'{x} {y + h} {x + s / 2} {y} {x + s} {y + h}' if not down else f'{x} {y} {x + s} {y} {x + s / 2} {y + h}'
    return f'<polygon points="{pts}"' + (' fill="currentColor" stroke="none"/>' if fill else '/>')


# what they help you do (the collection map's 25 groups): reused later by the map and the field
G = {
    'Take something away': _svg(dot(9, 16) + dot(19, 16) + dot(29, 16) + ring(39, 16, 2.6, dash='1.4 1.6')),
    'Give me more to work with': _svg(dot(7, 16, 2) + arrow(12, 16, 23, 16) + dot(30, 11, 2) + dot(37, 11, 2) + dot(30, 21, 2) + dot(37, 21, 2) + dot(43, 16, 2)),
    'Change what it is': _svg(sq(6, 11, 10) + arrow(20, 16, 31, 16) + dot(38, 16, 5)),
    'Help me see it from another angle': _svg(box(7, 10, 12, 12) + '<path d="M34 7 L43 16 L34 25 L25 16 Z"/>'),
    'Put different things into contact': _svg(sq(10, 10, 12) + dot(28, 16, 6)),
    'Put the parts into contact': _svg(sq(10, 10, 12) + dot(28, 16, 6)),
    'Pull the parts apart': _svg(arrow(14, 16, 4, 16) + sq(16, 11, 6, h=10) + sq(26, 11, 6, h=10) + arrow(34, 16, 44, 16)),
    'Help me decide what comes first': _svg(sq(10, 20, 6, h=6) + sq(19, 15, 6, h=11) + sq(28, 9, 6, h=17) + line(6, 29, 40, 29)),
    'Shake up the order it is in': _svg('<rect x="8" y="12" width="7" height="7" transform="rotate(-18 11.5 15.5)" fill="currentColor" stroke="none"/>' + '<rect x="20" y="8" width="7" height="7" transform="rotate(22 23.5 11.5)" fill="currentColor" stroke="none"/>' + '<rect x="31" y="16" width="7" height="7" transform="rotate(-8 34.5 19.5)" fill="currentColor" stroke="none"/>'),
    'Help the parts agree': _svg(arrow(6, 6, 20, 14) + arrow(5, 16, 20, 16) + arrow(6, 26, 20, 18) + dot(26, 16, 3.6)),
    'Push me beyond what I’d normally do': _svg(box(5, 7, 22, 18) + dot(14, 16, 2.2) + arrow(18, 16, 43, 16)),
    'Give me a useful restriction': _svg('<path d="M15 8 H11 V24 H15"/><path d="M33 8 H37 V24 H33"/>' + dot(24, 16, 3)),
    'Give me another way in': _svg('<path d="M20 7 H40 V25 H20 V20"/><path d="M20 12 V7"/>' + arrow(5, 16, 28, 16)),
    'Help me name what matters': _svg(ring(8, 14, 2.4) + ring(17, 14, 2.4) + dot(27, 14, 2.8) + ring(37, 14, 2.4) + '<path d="M22 22 H32" stroke-width="2.4"/>'),
    'Show me what I’m missing': _svg(sq(4, 8, 12, h=16) + dot(33, 16, 3) + line(33, 6, 33, 9) + line(33, 23, 33, 26) + line(23, 16, 26, 16) + line(40, 16, 43, 16) + line(26, 9, 28, 11) + line(40, 9, 38, 11) + line(26, 23, 28, 21) + line(40, 23, 38, 21)),
    'Take something out of view for now': _svg(ring(27, 16, 5, dash='1.6 1.8') + sq(10, 8, 16, h=16)),
    'Let me find out what holds up': _svg(line(6, 20, 42, 20) + '<path d="M24 20 L19 28 L29 28 Z"/>' + sq(32, 12, 8)),
    'Move the decision or responsibility': _svg(box(4, 9, 14, 14) + arrow(20, 16, 28, 16) + box(30, 9, 14, 14) + dot(37, 16, 2.6)),
    'Spread it across more people or parts': _svg(sq(4, 11, 10) + arrow(16, 16, 23, 16) + sq(27, 5, 5) + sq(36, 5, 5) + sq(27, 22, 5) + sq(36, 22, 5)),
    'Help the parts work together': _svg(ring(18, 16, 7) + ring(30, 16, 7)),
    'Protect what still needs to work': _svg(arc(24, 22, 12, 180, 360) + dot(24, 21, 3)),
    'Let it respond to what happens': _svg('<path d="M4 16 C10 6, 16 6, 22 16 S34 26, 44 16"/>' + dot(22, 16, 3)),
    'Make it something I can try again': _svg(box(7, 7, 7, 7) + box(20, 7, 7, 7) + box(33, 7, 7, 7) + '<path d="M38 20 C38 28, 10 28, 10 21"/>' + '<path d="M10 17.5 L7.4 22.5 L12.6 22.5 Z" fill="currentColor" stroke="none"/>'),
    'Break the pattern it is following': _svg(dot(6, 16, 1.8) + dot(13, 16, 1.8) + dot(20, 16, 1.8) + '<path d="M26 6 L26 26" stroke-width="2.6"/>' + dot(33, 16, 1.8, .3) + dot(40, 16, 1.8, .3)),
    'Break the pattern I’m in': _svg(dot(6, 16, 1.8) + dot(13, 16, 1.8) + dot(20, 16, 1.8) + '<path d="M26 6 L26 26" stroke-width="2.6"/>' + dot(33, 16, 1.8, .3) + dot(40, 16, 1.8, .3)),
    'Help me bring it to a close': _svg(line(5, 16, 26, 16) + ring(34, 16, 7) + dot(34, 16, 3)),
    'Get it back to a workable state': _svg(line(5, 24, 43, 24) + '<path d="M12 24 C12 8, 30 8, 30 21"/>' + '<path d="M30 24.5 L27.2 19.5 L32.8 19.5 Z" fill="currentColor" stroke="none"/>'),
}

F = {
    'I have nothing to work with': _svg(box(10, 6, 28, 20, dash='2.5 2.5')),
    'I’m missing something I need': _svg(dot(14, 11) + dot(24, 11) + dot(34, 11) + dot(14, 21) + ring(24, 21, 2.6, dash='1.4 1.6') + dot(34, 21)),
    'Neither of these feels right': NONE,
    'I don’t know—show me different approaches': _svg(sq(9, 6, 8) + dot(26, 12, 4) + tri(32, 16, 10)),
    'I can’t get moving': _svg(dot(30, 16, 4) + '<path d="M37 7 L37 25" stroke-width="2.6"/>' + line(6, 16, 20, 16) ),
    'I keep making the same moves': _svg(arc(10, 18, 5, 180, 360) + arc(21, 18, 5, 180, 360) + arc(32, 18, 5, 180, 360) + dot(42, 18, 2)),
    'Everything I think of feels too familiar': _svg(''.join(ring(10 + i * 9.5, 10 + j * 12, 2.6) for i in range(4) for j in range(2))),
    'I know what I should change, but I can’t let go of it': _svg(sq(5, 12, 8) + line(13, 16, 28, 16) + dot(31, 16, 3) + arrow(36, 16, 45, 16)),
    'I can’t tell what deserves attention': _svg(''.join(dot(9 + i * 10, 10 + j * 12, 2.2) for i in range(4) for j in range(2))),
    'I can’t reconstruct what happened': _svg(dot(5, 16, 2.6) + '<path d="M10 16 H16 M21 16 H24 M30 16 H32" />' + dot(43, 16, 2.6) + line(36, 16, 38, 16)),
    'I don’t know what this means yet': _svg(dot(9, 16, 3.4) + line(14, 16, 20, 16) + box(22, 9, 20, 14, dash='2 2')),
    'The parts are pulling in different directions': _svg(dot(24, 18, 2.6) + arrow(24, 18, 9, 8) + arrow(24, 18, 39, 8) + arrow(24, 18, 24, 31)),
    'The right things are happening in the wrong order': _svg(sq(9, 9, 6, h=17) + sq(19, 14, 6, h=12) + sq(29, 19, 6, h=7) + line(5, 29, 39, 29) + '<path d="M12 5 C18 0, 28 0, 33 13" />' + '<path d="M33.6 16 L30.3 11.6 L35.6 10.8 Z" fill="currentColor" stroke="none"/>'),
    'One thing can’t happen until something else does': _svg(dot(9, 16, 3.4) + arrow(14, 16, 28, 16) + ring(36, 16, 4, dash='1.6 1.8')),
    'They are actively pulling against each other': _svg(arrow(18, 16, 4, 16) + dot(20, 16, 2.8) + line(22, 16, 26, 16) + dot(28, 16, 2.8) + arrow(30, 16, 44, 16)),
    'They aren’t working together well enough': _svg(ring(16, 13, 7) + ring(32, 19, 7)),
    'One point is holding everything else up': _svg('<path d="M4 6 L20 14 L28 14 L44 6 M4 26 L20 18 L28 18 L44 26"/>' + dot(8, 16, 1.6) + dot(13, 16, 1.6) + dot(24, 16, 1.6)),
    'The same problem keeps returning': _svg(cross(24, 12) + '<path d="M33 12 C40 12, 40 25, 24 25 C12 25, 9 16, 15 13"/>' + '<path d="M17.6 11.4 L13.2 10.6 L14.4 15.3 Z" fill="currentColor" stroke="none"/>'),
    'One failure makes everything collapse': _svg(line(6, 29, 42, 29) + sq(14, 21, 8) + cross(18, 25, 2.2).replace('<path', '<path stroke="#f7f7f3"') + '<rect x="16" y="11" width="8" height="8" transform="rotate(14 20 15)" fill="currentColor" stroke="none"/>' + '<rect x="23" y="2" width="8" height="8" transform="rotate(30 27 6)" fill="currentColor" stroke="none"/>'),
    'It slowly gets worse or further off course': _svg('<path d="M5 12 H43" stroke-dasharray="2 2.5" opacity=".45"/>' + '<path d="M5 12 C20 12, 30 15, 43 25"/>' + dot(43, 25, 2.2)),
    'We need to move from the old situation to the new one': _svg(box(4, 9, 13, 14, dash='2 2') + arrow(20, 16, 29, 16) + sq(31, 9, 13, h=14)),
    'I don’t know what is going to happen': _svg(dot(6, 16, 2.6) + line(9, 16, 18, 16) + '<path d="M18 16 L42 6 M18 16 L42 16 M18 16 L42 26" stroke-dasharray="2 2.5"/>'),
    'Almost nothing': _svg(line(6, 26, 42, 26) + dot(12, 22.6, 1.8)),
    'Something already taking shape': _svg('<path d="M28 7 H10 V25 H38 V14"/>' + '<path d="M38 7 H32 M38 7 V10" stroke-dasharray="2 2"/>' + dot(18, 16, 2) + dot(27, 18, 2)),
    'Too many possibilities': _svg(dot(7, 16, 2.6) + ''.join(arrow(10, 16, 40, y) for y in (4, 10, 16, 22, 28))),
    'Something quite established': _svg(line(6, 28, 42, 28) + sq(14, 18, 9) + sq(25, 18, 9) + sq(19.5, 8, 9)),
    # practical limits
    'It has to fit into a few minutes': _svg(ring(24, 16, 11) + line(24, 16, 24, 9) + line(24, 16, 29, 18)),
    'I need something I can do by myself': _svg(dot(24, 14, 3.4) + line(14, 26, 34, 26)),
    'Keep it away from an audience': _svg(dot(11, 16, 3.4) + '<path d="M22 5 L22 27" stroke-width="2.6"/>' + dot(31, 10, 1.8, .35) + dot(38, 14, 1.8, .35) + dot(32, 20, 1.8, .35) + dot(39, 23, 1.8, .35)),
    'Don’t destroy anything': _svg(arc(24, 24, 13, 180, 360) + sq(18, 15, 12, h=9)),
}

P.update(G)
P.update(F)

CSS = """
    /* pictograms 2026-10-11 */
    .pict { display:block; width:54px; height:36px; color:var(--ink); }
    .pict svg { width:100%; height:100%; display:block; overflow:visible; }
    .route.has-pict { grid-template-columns:54px minmax(0,1fr) auto; gap:20px; }
    .option.has-pict { display:grid; grid-template-columns:54px minmax(0,1fr); gap:18px; align-items:center; }
    .option.has-pict > .pict { opacity:.85; align-self:center; }
    .option.has-pict > :not(.pict) { grid-column:2; }
    .option.has-pict:has(> small) > .pict { grid-row:1 / span 2; }
    .option.has-pict:has(> small) > strong { align-self:end; }
    .option.has-pict:has(> small) > small { align-self:start; }
    .option.has-pict:hover > .pict, .route.has-pict:hover > .pict { opacity:1; }
    @media (max-width:640px) {
      .route.has-pict { grid-template-columns:44px minmax(0,1fr) auto; gap:14px; }
      .option.has-pict { grid-template-columns:44px minmax(0,1fr); gap:14px; }
      .pict { width:44px; height:29px; }
    }
"""

JS_TMPL = r"""
<script>
(function(){
  var P = __P__;
  function norm(t){ return String(t || '').replace(/\s+/g, ' ').trim(); }
  function add(btn, key){
    if (!btn || btn.querySelector(':scope > .pict')) return;
    var svg = P[key]; if (!svg) return;
    var s = document.createElement('span'); s.className = 'pict'; s.innerHTML = svg;
    btn.insertBefore(s, btn.firstChild); btn.classList.add('has-pict');
  }
  document.querySelectorAll('#opening .route').forEach(function(b){ var st = b.querySelector('strong'); if (st) add(b, norm(st.textContent)); });
  var box = document.querySelector('#options');
  if (!box) return;
  function decorate(){ box.querySelectorAll('button.option').forEach(function(b){ var st = b.querySelector('strong'); add(b, norm(st ? st.textContent : b.textContent)); }); }
  new MutationObserver(decorate).observe(box, {childList:true});
  decorate();
})();
</script>
"""


def js():
    import json
    return JS_TMPL.replace('__P__', json.dumps(P, ensure_ascii=False))
