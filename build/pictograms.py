"""pictograms.py — small pictograms for the ways in and the first question of each route (2026-10-11, work lane).
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

CSS = """
    /* pictograms 2026-10-11 */
    .pict { display:block; width:54px; height:36px; color:var(--ink); }
    .pict svg { width:100%; height:100%; display:block; overflow:visible; }
    .route.has-pict { grid-template-columns:54px minmax(0,1fr) auto; gap:20px; }
    .option.has-pict { display:grid; grid-template-columns:54px minmax(0,1fr); gap:18px; align-items:center; }
    .option.has-pict > .pict { opacity:.85; }
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
  // only the first question of each route; later steps stay text
  function firstStep(){ try { return currentStep === 'route'; } catch (e) { return false; } }
  function decorate(){ if (!firstStep()) return; box.querySelectorAll('button.option').forEach(function(b){ var st = b.querySelector('strong'); add(b, norm(st ? st.textContent : b.textContent)); }); }
  new MutationObserver(decorate).observe(box, {childList:true});
  decorate();
})();
</script>
"""


def js():
    import json
    return JS_TMPL.replace('__P__', json.dumps(P, ensure_ascii=False))
