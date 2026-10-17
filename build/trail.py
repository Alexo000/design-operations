"""trail.py — a trail at the top of every card (2026-10-17, work lane; preview only until the author says deploy).
Shows where the operation sits, in five steps: its group, the operation, the ways to try it, where it has been
seen, and where it leads. Each step jumps to its part of the card; the group step opens the other operations in
the same group. Built from data already on the card: nothing new is said, it is only arranged."""
import json
from pictograms import G

CSS = """
    /* trail 2026-10-17 */
    .trail { --tr-pad:14px; margin:0 0 26px; border:1px solid var(--line-strong); background:var(--paper); }
    .trail ol { list-style:none; margin:0; padding:0; display:grid; grid-template-columns:repeat(var(--tr-n,5), minmax(0,1fr)); }
    .trail li { min-width:0; border-left:1px solid var(--line); }
    .trail li:first-child { border-left:0; }
    .tr-step { display:flex; flex-direction:column; gap:6px; width:100%; height:100%; padding:10px var(--tr-pad) 12px; border:0; background:transparent; color:var(--ink); font:inherit; text-align:left; cursor:pointer; position:relative; }
    .tr-step:hover { background:var(--hover); }
    .tr-step:focus-visible { outline:2px solid var(--ink); outline-offset:-2px; }
    .tr-k { font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); font-variant-numeric:tabular-nums; white-space:nowrap; }
    .tr-k b { font-weight:500; color:var(--ink); margin-right:6px; }
    .tr-v { display:flex; align-items:center; gap:8px; min-width:0; font-size:15px; line-height:1.25; }
    .tr-v > span { min-width:0; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
    .tr-ico { flex:none; display:inline-flex; width:30px; height:20px; }
    .tr-ico svg { width:100%; height:100%; }
    .tr-sym { flex:none; display:inline-flex; align-items:center; height:22px; font-size:20px; line-height:1; }
    .tr-sym svg { height:22px; width:auto; }
    .tr-fmt { flex:none; display:inline-flex; align-items:center; gap:10px; margin-right:2px; }
    .tr-fmt i { display:inline-flex; height:15px; }
    .tr-fmt svg { height:100%; width:auto; }
    .trail li.is-here .tr-step { background:var(--ink); color:var(--paper); }
    .trail li.is-here .tr-k, .trail li.is-here .tr-k b { color:inherit; opacity:.75; }
    .trail li.is-here .tr-step:hover { background:var(--ink); }
    .tr-step[aria-expanded="true"] { background:var(--hover); }
    .tr-step[aria-expanded="true"] .tr-k::after { content:" ▴"; }
    .tr-step[aria-expanded="false"] .tr-k::after { content:" ▾"; }
    .tr-sibs { border-top:1px solid var(--line); padding:12px var(--tr-pad) 14px; }
    .tr-sibs p { margin:0 0 10px; font-size:13px; color:var(--muted); }
    .tr-sibs ul { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:8px; }
    .tr-sibs button { display:inline-flex; align-items:center; gap:8px; width:auto; padding:6px 10px; border:1px solid var(--line-strong); background:transparent; color:var(--ink); font:inherit; font-size:14px; cursor:pointer; }
    .tr-sibs button:hover { border-color:var(--ink); }
    .tr-sibs button[aria-current="true"] { background:var(--ink); color:var(--paper); border-color:var(--ink); cursor:default; }
    .tr-sibs .tr-sym, .tr-sibs .tr-sym svg { height:16px; font-size:15px; }
    @media (max-width:720px) {
      /* phones: a stack of one-line rows, like a card index */
      .trail ol { display:block; }
      .trail li { border-left:0; border-top:1px solid var(--line); }
      .trail li:first-child { border-top:0; }
      .tr-step { --tr-pad:12px; flex-direction:row; align-items:center; gap:10px; padding:9px var(--tr-pad); }
      .tr-k { flex:none; width:92px; }
      .tr-v { font-size:14px; }
      .tr-v > span { -webkit-line-clamp:1; }
      .tr-ico { width:24px; height:16px; }
      .tr-sym, .tr-sym svg { height:18px; font-size:16px; }
    }
"""

JS = """
<script>
(function(){
  var G = %s;
  var FMT = ['With your hands', 'In words', 'In the process', 'Try this'];
  var KEYS = {'With your hands':'hands', 'In words':'words', 'In the process':'process', 'Try this':'general'};
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function sectionFor(box, re){
    var h = Array.prototype.find.call(box.querySelectorAll('h3'), function(x){ return re.test(x.textContent); });
    return h ? (h.closest('section') || h) : null;
  }
  function shortSeen(plain){
    // maker and year only: "Lina Bo Bardi, 1951"
    var t = String(plain || '').replace(/\\s+/g, ' ').trim();
    var year = (t.match(/\\b(1[0-9]{3}|20[0-9]{2})\\b(?!.*\\b(1[0-9]{3}|20[0-9]{2})\\b)/) || [])[1] || '';
    var maker = t.split(', ')[0];
    if (maker.length > 34) maker = maker.slice(0, 32).replace(/\\s+\\S*$/, '') + '…';
    return year && maker.indexOf(year) < 0 ? maker + ', ' + year : maker;
  }
  function go(fromId, toId){
    if (!toId || toId === fromId) return;
    operationHistory.push(fromId);
    renderOperationDetail(toId);
    var back = document.querySelector('#operation-back'); if (back) back.hidden = false;
    operationDialog.scrollTo({top:0, behavior:motionBehavior});
  }
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var r = contentById.get(id); if (!r) return out;
    var old = box.querySelector('.trail'); if (old) old.remove();
    var move = r.locked.profile.primaryMovement, group = movementMeanings[move] || displayOperationName(move);
    var name = displayOperationName(r.locked.name);
    var apps = (r.editorial && r.editorial.applications) || {};
    var fmts = FMT.filter(function(f){ return apps[KEYS[f]] && apps[KEYS[f]].task; });
    var seen = r.editorial && r.editorial.seenIn;
    var leads = relationGroups(r).reduce(function(n, g){ return n + g[1].filter(function(x){ return contentIdByName.get(String(x).toUpperCase()); }).length; }, 0);
    var sibs = operations.filter(function(o){ return o.primary === move; });
    var steps = [];
    steps.push({k:'Group', key:'group', v:'<i class="tr-ico" aria-hidden="true">' + (G[group] || '') + '</i><span>' + esc(group) + '</span>', label:'Group: ' + group + '. Show the ' + sibs.length + ' operations in it'});
    steps.push({k:'Operation', key:'op', v:'<i class="tr-sym" aria-hidden="true">' + (r.locked.symbol || '') + '</i><span>' + esc(name) + '</span>', label:'Operation: ' + name});
    if (fmts.length) steps.push({k:'Try it', key:'try', v:'<span>' + (fmts.length === 1 ? 'One way' : fmts.length + ' ways') + '</span>', label:'Try it: ' + fmts.join(', ').toLowerCase()});
    if (seen && seen.plain) steps.push({k:'Seen in', key:'seen', v:'<span>' + esc(shortSeen(seen.plain)) + '</span>', label:'Seen in: ' + seen.plain});
    if (leads) steps.push({k:'Leads to', key:'next', v:'<span>' + (leads === 1 ? 'One operation' : leads + ' operations') + '</span>', label:'Leads to ' + leads + ' operations'});
    var nav = document.createElement('nav'); nav.className = 'trail'; nav.setAttribute('aria-label', 'Where this operation sits');
    nav.innerHTML = '<ol style="--tr-n:' + steps.length + '">' + steps.map(function(s, i){
      return '<li data-step="' + s.key + '"' + (s.key === 'op' ? ' class="is-here"' : '') + '><button type="button" class="tr-step" aria-label="' + esc(s.label) + '"' + (s.key === 'group' ? ' aria-expanded="false"' : '') + '>'
        + '<span class="tr-k"><b>0' + (i + 1) + '</b>' + s.k + '</span><span class="tr-v">' + s.v + '</span></button></li>';
    }).join('') + '</ol>'
      + '<div class="tr-sibs" hidden><p>' + esc(group) + ': ' + sibs.length + ' operations</p><ul>' + sibs.map(function(o){
        var here = o.id === id;
        return '<li><button type="button" data-sib="' + o.id + '"' + (here ? ' aria-current="true"' : '') + '><i class="tr-sym" aria-hidden="true">' + ((operationContent[o.id] || {}).symbol || '') + '</i>' + esc(displayOperationName(o.name)) + '</button></li>';
      }).join('') + '</ul></div>';
    box.insertBefore(nav, box.firstChild);
    var targets = {
      op: box.querySelector('.operation-hero'),
      try: sectionFor(box, /Try it on your work/i),
      seen: box.querySelector('.seen-in') || sectionFor(box, /How it has been used/i),
      next: sectionFor(box, /Where it leads/i)
    };
    var panel = nav.querySelector('.tr-sibs');
    nav.addEventListener('click', function(e){
      var sib = e.target.closest('[data-sib]');
      if (sib) { go(id, sib.dataset.sib); return; }
      var li = e.target.closest('li[data-step]'); if (!li) return;
      var key = li.dataset.step;
      if (key === 'group') {
        var btn = li.querySelector('.tr-step'), open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', open ? 'false' : 'true'); panel.hidden = open; return;
      }
      var t = targets[key]; if (!t) return;
      if (key === 'op') { operationDialog.scrollTo({top:0, behavior:motionBehavior}); return; }
      var bar = document.querySelector('.operation-dialog-bar');
      var y = t.getBoundingClientRect().top - operationDialog.getBoundingClientRect().top + operationDialog.scrollTop - (bar ? bar.offsetHeight : 0) - 12;
      operationDialog.scrollTo({top:y, behavior:motionBehavior});
    });
    return out;
  };
})();
</script>
""" % json.dumps(G, ensure_ascii=False)
