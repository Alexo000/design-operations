"""chatprompt.py — "With a chatbot": a ready-made prompt on the card, under the three tasks (2026-11-03, work lane,
rulings 1a and 2a of that day; preview first).
1a: the prompt makes the chatbot a coach. It asks about the visitor's work and holds them to the rule and the stop;
    it does not do the move for them.
2a: every prompt is built by one template from lines the entry already has: its name, the action of its Compact line,
    and the sentence of In the studio that says what the move forbids or forces, when there is one.
PREVIEW lists the cards that show it while it is being tried; set PROMPTS=all in the environment to show it on every card.
A copy is counted privately in GoatCounter as an event (prompt/<slug>), the way "I tried this" is."""
import json, os, re

PREVIEW = {'DO-118', 'DO-001', 'DO-136'}   # LEASE, STRIP, LEAVE OPEN
STAMP = re.compile(r'\s*\[[^\]]*\]')
FORB = re.compile(r'The move (?:forbids|forces)[^.]*(?:\.[^.\s][^.]*)*\.')


def _clean(v):
    return STAMP.sub('', v or '').strip()


def build(E, records):
    """Return {DO id: prompt text} for the cards that show a prompt."""
    show_all = os.environ.get('PROMPTS') == 'all'
    out = {}
    for r in records:
        if not show_all and r['id'] not in PREVIEW:
            continue
        f = dict(E[r['number']]['fields'])
        act = (r['editorial'].get('compact') or {}).get('act') or ''
        act = act.strip().rstrip('.') + '.' if act else ''
        studio = _clean(f.get('In the studio', ''))
        m = FORB.search(studio)
        rule = (' ' + m.group(0)) if m else ''
        name = r['locked']['name'].title().replace("'S", "'s").replace("’S", "’s")
        if not act:
            continue
        out[r['id']] = (
            "I'm working on [describe your work in a sentence or two]. "
            f"Help me apply one move to it, called {name}: {act}{rule}\n\n"
            "Ask me about my work first. Then help me choose where the move applies, and let me do it myself, one step at a time. "
            "Hold me to the rule: don't let me soften it, and don't do the work for me. "
            "When I reach the point where the move says to stop, tell me, and stop there."
        )
    return out


CSS = """
    /* chatbot prompt 2026-11-03 */
    .chat-prompt { margin:26px 0 0; padding-top:18px; border-top:1px dashed var(--line-strong); }
    .chat-prompt .cp-head { display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:6px 18px; }
    .chat-prompt .cp-label { font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .chat-prompt .cp-note { margin:6px 0 10px; font-size:15px; color:var(--muted); max-width:62ch; }
    .chat-prompt .cp-text { margin:0; padding:16px 18px; border:1px solid var(--line); background:#fff; font:inherit; font-size:15px; line-height:1.5; white-space:pre-wrap; max-width:72ch; }
    .chat-prompt .cp-copy { width:auto; margin-top:12px; padding:8px 16px; border:1.5px solid var(--ink); background:transparent; color:var(--ink); font:inherit; font-size:15px; cursor:pointer; }
    .chat-prompt .cp-copy:hover { background:var(--ink); color:var(--paper); }
    .chat-prompt .cp-copy[data-done] { background:var(--ink); color:var(--paper); }
"""

JS_TMPL = r"""
<script>
(function(){
  var PROMPTS = __DATA__;
  function slug(n){ return String(n).toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var old = box.querySelector('.chat-prompt'); if (old) old.remove();
    var text = PROMPTS[id]; if (!text) return out;
    var r = contentById.get(id), name = r ? displayOperationName(r.locked.name) : '';
    var d = document.createElement('div'); d.className = 'chat-prompt';
    d.innerHTML = '<div class="cp-head"><span class="cp-label">With a chatbot</span></div>'
      + '<p class="cp-note">Paste this into any chatbot. It asks about your work, then holds you to the rule while you do the move yourself.</p>'
      + '<p class="cp-text"></p><button type="button" class="cp-copy">Copy the prompt</button>';
    d.querySelector('.cp-text').textContent = text;
    var btn = d.querySelector('.cp-copy');
    btn.addEventListener('click', function(){
      var done = function(){ btn.textContent = 'Copied'; btn.setAttribute('data-done', ''); setTimeout(function(){ btn.textContent = 'Copy the prompt'; btn.removeAttribute('data-done'); }, 2200); };
      var fallback = function(){ var t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select(); try { document.execCommand('copy'); } catch (e) {} t.remove(); done(); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback); else fallback();
      try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({path: 'prompt/' + slug(name), title: 'Prompt copied: ' + name, event: true}); } catch (e) {}
    });
    var after = box.querySelector('.tried-after') || box.querySelector('.operation-applications');
    if (after && after.parentNode) after.parentNode.insertBefore(d, after.nextSibling); else box.appendChild(d);
    return out;
  };
})();
</script>
"""


def js(prompts):
    return JS_TMPL.replace('__DATA__', json.dumps(prompts, ensure_ascii=False))
