"""dialogue.py — the explorer talks back (2026-10-11, work lane, ruling 1b).
  - Every card ends with two links, "I tried this" and "Know a better example?", each opening a Tally form with the
    operation's name filled in (hidden field "operation").
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
  function nameOf(id){ var r = contentById.get(id); return r ? displayOperationName(r.locked.name) : ''; }
  function link(base, name, text){
    var a = document.createElement('a'); a.href = base + '?operation=' + encodeURIComponent(name); a.target = '_blank'; a.rel = 'noopener'; a.textContent = text; return a;
  }
  // every card ends with the two replies
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var old = box.querySelector('.talk-back'); if (old) old.remove();
    var name = nameOf(id); if (!name) return out;
    var tb = document.createElement('div'); tb.className = 'talk-back';
    var label = document.createElement('span'); label.className = 'tb-label'; label.textContent = 'Your turn';
    tb.appendChild(label);
    tb.appendChild(link(TRIED, name, 'I tried this →'));
    tb.appendChild(link(EXAMPLE, name, 'Know a better example? →'));
    box.appendChild(tb);
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
    anchor = '<p>Built from the Compendium of'
    assert npage.count(anchor) == 1, 'footer anchor'
    npage = npage.replace(anchor, FOOT_HTML + anchor, 1)
    assert npage.count('</footer>') == 1, 'footer end'
    npage = npage.replace('</footer>', '</footer>\n' + NEWS_HTML, 1)   # before the scripts, which look for it
    npage = npage.replace('</style>', CSS + '  </style>', 1)
    return npage
