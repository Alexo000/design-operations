"""dialogue.py — the explorer talks back (2026-10-11, work lane, ruling 1b).
  - Every card ends with a one-tap "I tried this" button (counted privately with GoatCounter, never shown; rulings 1a
    and 2a), then "Tell me more" and "Know a better example?", each opening a Tally form with the operation's name
    filled in (hidden field "operation"). The same button sits in the card's top bar, which stays in view.
  - "Suggest an operation": a form that asks the Compendium's standing test in plain words (the instruction with its
    stop, the rule it adds, a real work where it is used, the nearest existing operation). Linked from the footer and
    from the end of the collection map.
  - "What's new": a short list in a dialog, opened from the footer. Entries live in WHATS_NEW below, newest first.
Nothing a visitor sends reaches the page directly: it is read, and what fits enters the Compendium by its own rules.
Visitor wording here is new and unratified."""
import html, json

TRIED = 'https://tally.so/r/QKgDo1'      # Design Operations feedback (hidden field: operation)
EXAMPLE = 'https://tally.so/r/RGXJpK'    # Design Operations: a better example (hidden field: operation)
SUGGEST = 'https://tally.so/r/EkjJ9l'    # Design Operations: suggest an operation

# One-tap "I tried this" (rulings 1a and 2a, 2026-10-11): counted privately with GoatCounter (no cookies), never shown
# on the page. Empty code: the button still works for the visitor, nothing is counted. Dashboard: https://<code>.goatcounter.com
GOATCOUNTER = 'alexo000'

WHATS_NEW = [
    ('11 October 2026', 'You can now answer back. Every operation ends with two links: tell me you tried it, or send a better example. Know a move that isn’t here? Suggest one.'),
    ('11 October 2026', 'The explorer has its own address, a field of all 144 operations on the first screen, previews in the strip under the header, and a small picture for every answer.'),
    ('2 October 2026', 'The collection now holds 144 operations, 44 more than the first public version. The newest are Leave One Out, Pretend and Recall.'),
]

FOOT_HTML = (f'<p class="foot-ask">Know a move that isn’t here? <a href="{SUGGEST}" target="_blank" rel="noopener">Suggest an operation</a>.</p>'
             '<p class="foot-ask"><button type="button" class="news-open" id="news-open">What’s new</button></p>')

NEWS_HTML = ('<dialog class="news-dialog" id="news-dialog" aria-labelledby="news-title">'
             '<div class="news-head"><h2 id="news-title">What’s new</h2><button type="button" class="news-close" id="news-close">Close</button></div>'
             '<ol class="news-list">'
             + ''.join(f'<li><span class="news-date">{html.escape(d)}</span><p>{html.escape(t)}</p></li>' for d, t in WHATS_NEW)
             + '</ol>'
             f'<p class="news-ask">Something you’d like to see here? <a href="{SUGGEST}" target="_blank" rel="noopener">Suggest an operation</a> or <a href="{TRIED}" target="_blank" rel="noopener">tell me how one went</a>.</p>'
             '</dialog>')

CSS = """
    /* dialogue 2026-10-11 */
    .talk-back { display:flex; flex-wrap:wrap; gap:12px 28px; align-items:center; margin:36px 0 6px; padding-top:20px; border-top:1px solid var(--line-strong); }
    .talk-back .tb-label { width:100%; font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .talk-back a { color:var(--ink); text-decoration:none; border-bottom:1px solid var(--ink); padding:4px 0; font-size:16px; }
    .talk-back a:hover { border-bottom-width:2px; }
    .tried-btn { width:auto; display:inline-flex; align-items:center; gap:8px; padding:9px 16px; border:1px solid var(--ink); background:transparent; color:var(--ink); font-size:16px; cursor:pointer; }
    .tried-btn:hover { background:var(--hover); border-color:var(--ink); }
    .tried-btn[aria-pressed="true"] { background:var(--ink); color:var(--paper); }
    .tried-btn[aria-pressed="true"]:hover { background:var(--ink); }
    .tb-thanks { width:100%; margin:0; font-size:14px; color:var(--muted); min-height:1.4em; }
    .operation-dialog-bar .tried-bar { margin-left:auto; padding:5px 12px; font-size:14px; border:1px solid var(--ink); }
    .operation-dialog-bar .copy-link { margin-left:0; }
    @media (max-width:640px) { .operation-dialog-bar { gap:12px; } .operation-dialog-bar .tried-bar { padding:5px 10px; } }
    .map-suggest { display:block; margin:6px 0 0; padding:16px; border:1px dashed var(--line-strong); color:var(--ink); text-decoration:none; font-size:15px; break-inside:avoid; }
    .map-suggest:hover { border-color:var(--ink); background:var(--hover); }
    .news-open { width:auto; padding:0; border:0; border-bottom:1px solid var(--ink); background:transparent; font:inherit; color:var(--ink); cursor:pointer; }
    .news-open:hover { background:transparent; }
    .news-dialog { width:min(620px, calc(100% - 32px)); max-height:calc(100% - 48px); padding:0; border:1px solid var(--ink); background:var(--paper); color:var(--ink); }
    .news-dialog::backdrop { background:rgba(22,22,22,.35); }
    .news-head { display:flex; justify-content:space-between; align-items:center; gap:16px; padding:18px 24px; border-bottom:1px solid var(--line); }
    .news-head h2 { margin:0; font-size:24px; }
    .news-close { width:auto; padding:4px 0; border:0; border-bottom:1px solid var(--line-strong); background:transparent; font-size:14px; }
    .news-list { list-style:none; margin:0; padding:8px 24px 0; }
    .news-list li { display:grid; gap:4px; padding:16px 0; border-bottom:1px solid var(--line); }
    .news-list li:last-child { border-bottom:0; }
    .news-date { font-size:13px; letter-spacing:.04em; color:var(--muted); }
    .news-list p { margin:0; font-size:16px; line-height:1.5; }
    .news-ask { margin:0; padding:14px 24px 22px; color:var(--muted); font-size:15px; }
    .news-ask a { color:var(--ink); }
"""

JS = """
<script>
(function(){
  var TRIED = %s, EXAMPLE = %s, SUGGEST = %s;
  // one-tap 'I tried this': remembered in this browser; the first tap per browser is counted, privately
  var TKEY = 'do-tried', triedSet = new Set(), counted = new Set();
  try { triedSet = new Set(JSON.parse(localStorage.getItem(TKEY) || '[]')); counted = new Set(JSON.parse(localStorage.getItem(TKEY + '-counted') || '[]')); } catch (e) {}
  function saveTried(){ try { localStorage.setItem(TKEY, JSON.stringify(Array.from(triedSet))); localStorage.setItem(TKEY + '-counted', JSON.stringify(Array.from(counted))); } catch (e) {} }
  function slug(n){ return String(n).toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  function countTried(id, name){
    if (counted.has(id)) return; counted.add(id); saveTried();
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({path: 'tried/' + slug(name), title: 'Tried: ' + name, event: true}); } catch (e) {}
  }
  function nameOf(id){ var r = contentById.get(id); return r ? displayOperationName(r.locked.name) : ''; }
  function link(base, name, text){
    var a = document.createElement('a'); a.href = base + '?operation=' + encodeURIComponent(name); a.target = '_blank'; a.rel = 'noopener'; a.textContent = text; return a;
  }
  // every card ends with the two replies
  // one state, two buttons: a compact one in the card's top bar (always in view) and the fuller one at the end
  var cur = {id: '', name: ''}, thanks = null;
  function paintTried(){
    var on = !!cur.id && triedSet.has(cur.id);
    document.querySelectorAll('.tried-btn').forEach(function(b){ b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.textContent = on ? '✓ Tried' : 'I tried this'; });
  }
  function toggleTried(){
    if (!cur.id) return;
    if (triedSet.has(cur.id)) { triedSet.delete(cur.id); saveTried(); paintTried(); if (thanks) thanks.textContent = ''; return; }   // undo is local only
    triedSet.add(cur.id); saveTried(); paintTried(); countTried(cur.id, cur.name);
    if (thanks) thanks.textContent = (window.goatcounter && window.goatcounter.count) ? 'Thanks. Noted, anonymously.' : 'Thanks.';
  }
  function triedButton(extra){ var b = document.createElement('button'); b.type = 'button'; b.className = 'tried-btn' + (extra ? ' ' + extra : ''); b.addEventListener('click', toggleTried); return b; }
  var bar = document.querySelector('.operation-dialog-bar');
  if (bar) {
    var barBtn = triedButton('tried-bar'), before = bar.querySelector('.copy-link') || bar.querySelector('#operation-close');
    bar.insertBefore(barBtn, before);
  }
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var old = box.querySelector('.talk-back'); if (old) old.remove();
    var name = nameOf(id); cur = {id: id, name: name};
    if (!name) return out;
    var tb = document.createElement('div'); tb.className = 'talk-back';
    var label = document.createElement('span'); label.className = 'tb-label'; label.textContent = 'Your turn';
    tb.appendChild(label);
    tb.appendChild(triedButton());
    tb.appendChild(link(TRIED, name, 'Tell me more →'));
    tb.appendChild(link(EXAMPLE, name, 'Know a better example? →'));
    thanks = document.createElement('p'); thanks.className = 'tb-thanks'; thanks.setAttribute('aria-live', 'polite');
    tb.appendChild(thanks);
    box.appendChild(tb);
    paintTried();
    return out;
  };
  // the end of the collection map invites a new one
  var origMap = typeof renderCollectionMap === 'function' ? renderCollectionMap : null;
  if (origMap) renderCollectionMap = function(){
    var out = origMap.apply(this, arguments);
    var grid = document.querySelector('.map-grid');
    if (grid && !grid.querySelector('.map-suggest')) {
      var a = document.createElement('a'); a.className = 'map-suggest'; a.href = SUGGEST; a.target = '_blank'; a.rel = 'noopener';
      a.textContent = 'Know a move that isn’t here? Suggest an operation →'; grid.appendChild(a);
    }
    return out;
  };
  // what's new
  var dlg = document.querySelector('#news-dialog'), openBtn = document.querySelector('#news-open'), closeBtn = document.querySelector('#news-close');
  if (dlg && openBtn) {
    openBtn.addEventListener('click', function(){ try { dlg.showModal(); } catch (e) { dlg.setAttribute('open', ''); } });
    closeBtn.addEventListener('click', function(){ dlg.close(); });
    dlg.addEventListener('click', function(e){ if (e.target === dlg) dlg.close(); });
  }
})();
</script>
""" % (json.dumps(TRIED), json.dumps(EXAMPLE), json.dumps(SUGGEST))


def patch_html(npage, rep):
    if GOATCOUNTER:
        gc = f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
        npage = npage.replace('</head>', gc + '\n</head>', 1)
    anchor = '<p>Built from the Compendium of'
    assert npage.count(anchor) == 1, 'footer anchor'
    npage = npage.replace(anchor, FOOT_HTML + anchor, 1)
    assert npage.count('</footer>') == 1, 'footer end'
    npage = npage.replace('</footer>', '</footer>\n' + NEWS_HTML, 1)   # before the scripts, which look for it
    npage = npage.replace('</style>', CSS + '  </style>', 1)
    return npage
