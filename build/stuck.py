"""stuck.py: a fifth way in, "I'm stuck on a project" (ruling 2b, 2026-10-13, Project Planning Toolkit session).
Tick what is wrong; each tick hands back one operation, with a button that opens its card.
The flags come from the red-flag check-in of the Project Planning Toolkit & Workbook (p.18), reworded for anyone.
Deep link: operations.ramos-saavedra.com/#stuck opens it straight away.

Used two ways:
  - in the build: build_explorer.py calls stuck.patch_page(npage) just before writing site/index.html;
  - on its own, to patch an already-built page:  python3 build/stuck.py site/index.html
Running it twice changes nothing (it checks for its own marker)."""
import sys

MARK = '<!-- stuck-doorway -->'

# (what is wrong, DO number of the operation it hands back, DO number of a second move)
# Second moves added 2026-10-17 (work lane, accepted "accept all"), drawn partly from the links written that day.
FLAGS = [
    ("I can't say what I'm after", 52, 42),             # NAME  # then SAY WHAT IT ISN'T
    ("I can't explain it in one sentence", 53, 1),     # COMPRESS  # then STRIP
    ("My tools feel too familiar", 9, 142),              # CONSTRAIN  # then SUBSTITUTE
    ("My own work has stopped surprising me", 4, 135),   # TRANSLATE  # then FOLD
    ("I don't really know who it's for", 61, 154),       # OCCUPY  # then PRETEND
    ("Nobody has tried it yet", 38, 29),                # ELICIT  # then EXCHANGE
    ("The people it's for are out of reach", 26, 65),   # LOCATE  # then RELOCATE
    ("I'm ignoring feedback I got", 47, 137),            # DEFECT  # then FOLLOW THROUGH
    ("I'm thinking instead of doing", 35, 86),          # MARK TIME  # then HEDGE
    ("I'm avoiding the parts I find hard", 22, 128),     # REHEARSE  # then SCAFFOLD
    ("My research isn't leading anywhere", 51, 40),     # GENERALISE  # then TRIANGULATE
    ("It's too complicated", 45, 131),                   # FIND THE KEYSTONE  # then HALVE
    ("I'm trying to do too many things", 60, 152),       # ARCHIVE  # then CUT THE BEATEN
    ("I haven't made anything yet", 87, 69),            # SCOUT  # then REPLICATE
    ("My restriction is just decoration", 112, 129),     # EXAGGERATE  # then RELAX
    ("I'm waiting for the perfect idea", 15, 115),       # DEFER  # then WEATHER
    ("Making is taking longer than I planned", 50, 138), # PREPARE EVERYTHING  # then ALLOW A MARGIN
]

BUTTON = ('<button class="route route-stuck" type="button" id="opening-stuck">\n'
          '          <span><strong>I’m stuck on a project</strong><small>Tick what’s wrong. Each one hands you a move, and a second to try.</small></span><span class="arrow" aria-hidden="true">→</span>\n'
          '        </button>\n        ')

SECTION = MARK + """
    <section id="stuck" hidden aria-labelledby="stuck-title">
      <div class="topline"><div class="nav-actions"><button class="back" type="button" id="stuck-back">← Pick another way in</button></div></div>
      <div class="eyebrow">Stuck on a project</div>
      <h2 id="stuck-title" tabindex="-1">What’s wrong right now?</h2>
      <p class="intro">Tick everything that is true this week. Each one hands you a move to try before you next look at the work. Come back whenever you’re stuck again: the list doesn’t change, but your ticks will.</p>
      <div class="stuck-flags" id="stuck-flags"></div>
      <p class="stuck-alarm" id="stuck-alarm" role="status"></p>
      <div class="stuck-moves" id="stuck-moves" aria-live="polite"></div>
    </section>
"""

CSS = """
    .route-stuck { border-style:solid; border-width:2px; }
    #stuck .stuck-flags { display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap:0 24px; margin-top:18px; }
    #stuck .stuck-flag { display:flex; gap:12px; align-items:flex-start; padding:12px 0; border-top:1px solid var(--line); cursor:pointer; font-size:17px; }
    #stuck .stuck-flag input { width:18px; height:18px; margin:3px 0 0; accent-color:var(--ink); flex:none; }
    #stuck .stuck-flag:has(input:checked) { font-weight:700; }
    #stuck .stuck-alarm { font-weight:700; min-height:1.2em; }
    #stuck .stuck-moves { display:grid; gap:18px; }
    #stuck .stuck-move { border-left:3px solid var(--ink); padding:2px 0 4px 16px; display:grid; gap:6px; }
    #stuck .stuck-why { font-size:13px; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); }
    #stuck .stuck-name { font-weight:700; font-size:20px; }
    #stuck .stuck-act { margin:0; max-width:60ch; }
    #stuck .stuck-open { justify-self:start; }
    #stuck .stuck-alt { display:grid; gap:4px; margin-top:8px; padding-top:10px; border-top:1px dashed var(--line-strong); }
    #stuck .stuck-alt .stuck-act { font-size:15px; }
"""

JS_TMPL = r"""
<script>
(function(){
  var FLAGS = %FLAGS%;
  var sec = document.querySelector('#stuck'), open = document.querySelector('#opening'), on = [];
  if (!sec || !open) return;
  ['showOpening','showRoute','showResults','showFollowup','showLimits'].forEach(function(n){
    var f = window[n]; if (typeof f !== 'function') return;
    window[n] = function(){ sec.hidden = true; return f.apply(this, arguments); };
  });
  function rec(n){ return contentById.get('DO-' + String(n).padStart(3, '0')); }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  try { on = JSON.parse(localStorage.getItem('do-stuck') || '[]'); } catch (e) { on = []; }
  function save(){ try { localStorage.setItem('do-stuck', JSON.stringify(on)); } catch (e) {} }
  function render(){
    document.querySelector('#stuck-flags').innerHTML = FLAGS.map(function(f, i){
      return '<label class="stuck-flag"><input type="checkbox" data-stuck="' + i + '"' + (on.indexOf(i) > -1 ? ' checked' : '') + '><span>' + esc(f[0]) + '</span></label>';
    }).join('');
    document.querySelector('#stuck-alarm').textContent = on.length > 2 ? 'More than two ticked: talk it through with someone you trust before you carry on.' : '';
    document.querySelector('#stuck-moves').innerHTML = on.slice().sort(function(a, b){ return a - b; }).map(function(i){
      var r = rec(FLAGS[i][1]); if (!r) return '';
      var act = (r.editorial && r.editorial.compact && r.editorial.compact.act) || r.locked.canonicalDefinition || '';
      var r2 = FLAGS[i][2] ? rec(FLAGS[i][2]) : null, alt = '';
      if (r2) {
        var act2 = (r2.editorial && r2.editorial.compact && r2.editorial.compact.act) || r2.locked.canonicalDefinition || '';
        alt = '<div class="stuck-alt"><span class="stuck-why">Or try</span><p class="stuck-act"><strong>' + esc(displayOperationName(r2.locked.name)) + '</strong>: ' + esc(act2) + '</p><button type="button" class="back stuck-open" data-open="' + r2.id + '">Read it →</button></div>';
      }
      return '<div class="stuck-move"><span class="stuck-why">' + esc(FLAGS[i][0]) + ' → try</span><span class="stuck-name">' + esc(displayOperationName(r.locked.name)) + '</span><p class="stuck-act">' + esc(act) + '</p><button type="button" class="back stuck-open" data-open="' + r.id + '">Read the whole operation →</button>' + alt + '</div>';
    }).join('');
  }
  function showStuck(){
    document.querySelectorAll('main > section').forEach(function(s){ s.hidden = s !== sec; });
    render(); window.scrollTo(0, 0); var h = document.querySelector('#stuck-title'); if (h) h.focus();
  }
  function hideStuck(){ sec.hidden = true; if (typeof window.showOpening === 'function') window.showOpening(); else open.hidden = false; }
  document.querySelector('#opening-stuck').addEventListener('click', showStuck);
  document.querySelector('#stuck-back').addEventListener('click', function(){ if (location.hash === '#stuck') history.replaceState(null, '', location.pathname + location.search); hideStuck(); });
  sec.addEventListener('change', function(e){
    var i = e.target.getAttribute('data-stuck'); if (i === null) return; i = +i;
    if (e.target.checked) { if (on.indexOf(i) < 0) on.push(i); } else on = on.filter(function(x){ return x !== i; });
    save(); render();
  });
  sec.addEventListener('click', function(e){ var b = e.target.closest('[data-open]'); if (b) openOperationDetail(b.getAttribute('data-open'), 'results', b); });
  function fromHash(){ if (location.hash === '#stuck') { var o = document.querySelector('#onboard'); if (o) o.hidden = true; showStuck(); } }
  window.addEventListener('hashchange', fromHash);
  setTimeout(fromHash, 0);
})();
</script>
"""


def patch_page(page):
    if MARK in page:
        return page
    import json
    anchor = '<button class="route route-map" type="button" id="opening-map">'
    assert anchor in page, 'opening-map button not found'
    page = page.replace(anchor, BUTTON + anchor, 1)
    assert '</main>' in page
    page = page.replace('</main>', SECTION + '  </main>', 1)
    page = page.replace('</style>', CSS + '  </style>', 1)
    js = JS_TMPL.replace('%FLAGS%', json.dumps(FLAGS, ensure_ascii=False))
    page = page.replace('</body>', js + '</body>', 1)
    return page


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'site/index.html'
    src = open(path, encoding='utf-8').read()
    out = patch_page(src)
    open(path, 'w', encoding='utf-8').write(out)
    print('patched' if out != src else 'already patched', path)
