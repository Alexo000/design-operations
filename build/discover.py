"""discover.py — the seen strip and the field as ways in (2026-10-11, work lane, ruling d).
  - Header strip (seen.py draws it in group order): on screens with a pointer, hovering a mark previews the operation
    under the strip, and clicking opens its card. Phones keep the strip as a quiet record.
  - Field on the opening screen: one row for each group in the collection map, longest first, one square per
    operation; filled squares are seen. Hover or tap previews, click (or a second tap) opens the card; the picked
    row's name is highlighted, and a row name picks that row's first unseen operation.
  - Both previews hold the height of the longest operation, so nothing moves while pointing around; the field's
    preview sticks to the bottom of the screen while the field is in view, so a tap near the top still shows it.
Visitor wording here is new and unratified."""

FIELD_HTML = """      <div class="field-way" id="field-way">
        <h2 class="field-title" id="field-title">Or pick from the field</h2>
        <p class="field-intro">Each square is one operation, in rows by what they help you do. Filled squares are ones you have opened.</p>
        <div class="field" id="field" tabindex="0" role="listbox" aria-labelledby="field-title"></div>
        <div class="op-preview field-preview" id="field-preview" aria-live="polite"></div>
      </div>
"""

CSS = """
    /* discover 2026-10-11 */
    .op-preview { display:grid; grid-template-columns:72px minmax(0,1fr) auto; gap:18px; align-items:center; padding:14px 18px; background:#fff; border:1px solid var(--line-strong); box-sizing:border-box; }
    .op-preview .pv-sym { width:72px; height:52px; }
    .op-preview .pv-sym svg { width:100%; height:100%; display:block; }
    .op-preview .pv-txt { min-width:0; display:grid; gap:2px; }
    .op-preview .pv-g { font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .op-preview .pv-n { font-size:20px; line-height:1.25; }
    .op-preview .pv-a { color:var(--muted); font-size:15px; line-height:1.4; }
    .op-preview .pv-open { width:auto; padding:4px 0; border:0; border-bottom:1px solid var(--ink); background:transparent; font-size:14px; white-space:nowrap; }
    .op-preview .pv-open:hover { background:transparent; }
    .op-preview .pv-idle { grid-column:1 / -1; color:var(--muted); font-size:15px; }
    .strip-preview { position:absolute; left:0; right:0; top:100%; z-index:6; box-shadow:0 10px 28px rgba(22,22,22,.08); }
    .tally-strip.can-point { cursor:pointer; }
    .tally-strip.hot i.dim::after { opacity:.45; }
    .tally-strip i.hl::after { height:12px; background:var(--ink); }
    .field-way { display:grid; gap:14px; margin-top:52px; }
    .field-way .field-title { margin:0; font-size:26px; line-height:1.2; letter-spacing:-.01em; }
    .field-intro { margin:0; color:var(--muted); font-size:16px; }
    .field { display:grid; gap:6px; margin-top:6px; outline:none; }
    .field:focus-visible { outline:2px solid var(--ink); outline-offset:8px; }
    .f-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:16px; align-items:center; }
    .f-name { width:100%; padding:0; border:0; background:transparent; font-size:14px; color:var(--muted); text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .f-name:hover { background:transparent; color:var(--ink); }
    .f-row.active .f-name { color:var(--ink); font-weight:700; }
    .f-cells { display:grid; grid-template-columns:repeat(12, 22px); gap:4px; }
    .f-c { width:22px; height:22px; padding:0; border:1px solid #b0b0a7; background:transparent; }
    .f-c:hover { background:transparent; border-color:var(--ink); }
    .f-row.active .f-c { border-color:var(--ink); }
    .f-c.seen, .f-c.seen:hover { background:var(--ink); border-color:var(--ink); }
    .f-c.hl { box-shadow:0 0 0 2px var(--paper), 0 0 0 4px var(--ink); }
    .field-preview { margin-top:8px; position:sticky; bottom:calc(12px + env(safe-area-inset-bottom, 0px)); z-index:3; box-shadow:0 10px 28px rgba(22,22,22,.10); }
    @media (max-width:640px) {
      .op-preview { grid-template-columns:56px minmax(0,1fr); gap:14px; padding:14px; }
      .op-preview .pv-sym { width:56px; height:44px; }
      .op-preview .pv-open { grid-column:2; justify-self:start; }
      .f-row { grid-template-columns:1fr; gap:3px; }
      .f-name { text-align:left; }
      .f-cells { grid-template-columns:repeat(12, minmax(0, 1fr)); gap:3px; }
      .f-c { width:auto; height:auto; aspect-ratio:1; }
      .field { gap:9px; }
    }
    @media (prefers-reduced-motion:reduce) { .tally-strip i::after { transition:none; } }
"""

JS = r"""
<script>
(function(){
  var recs = contentRecords;
  function meaning(r){ var m = r.locked.profile.primaryMovement; return (typeof movementMeanings !== 'undefined' && movementMeanings[m]) || m; }
  function symOf(r){ var c = null; try { c = operationContent.get ? operationContent.get(r.id) : operationContent[r.id]; } catch (e) {} return (c && c.symbol) || r.locked.symbol || ''; }
  function isSeen(id){ return window.__isSeen ? window.__isSeen(id) : false; }
  function openCard(r){ openOperationDetail(r.id, 'results', null); }

  // one preview, two places; it holds the height of the longest operation at its current width
  function fill(box, r, idle){
    box.innerHTML = '';
    if (!r) { var p = document.createElement('div'); p.className = 'pv-idle'; p.textContent = idle || ''; box.appendChild(p); return; }
    var s = document.createElement('div'); s.className = 'pv-sym'; s.setAttribute('aria-hidden', 'true'); s.innerHTML = symOf(r);
    var t = document.createElement('div'); t.className = 'pv-txt';
    var g = document.createElement('span'); g.className = 'pv-g'; g.textContent = meaning(r) + (isSeen(r.id) ? ' · seen' : '');
    var n = document.createElement('span'); n.className = 'pv-n'; n.textContent = displayOperationName(r.locked.name);
    var a = document.createElement('span'); a.className = 'pv-a'; a.textContent = r.locked.canonicalDefinition || '';
    t.appendChild(g); t.appendChild(n); t.appendChild(a);
    var o = document.createElement('button'); o.type = 'button'; o.className = 'pv-open'; o.textContent = 'Open the card →';
    o.addEventListener('click', function(){ openCard(r); });
    box.appendChild(s); box.appendChild(t); box.appendChild(o);
  }
  function fit(box, width){
    if (!width || box.dataset.fitW == String(width)) return;
    var m = box.cloneNode(false); m.removeAttribute('id'); m.hidden = false;
    m.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;top:0;bottom:auto;right:auto;min-height:0;box-shadow:none;width:' + width + 'px';
    document.body.appendChild(m);
    var max = 0;
    recs.forEach(function(r){ fill(m, r); max = Math.max(max, m.getBoundingClientRect().height); });
    m.remove();
    box.style.minHeight = Math.ceil(max) + 'px'; box.dataset.fitW = String(width);
  }

  // ---- header strip: preview on hover (pointer screens only)
  var strip = document.querySelector('#tally-strip'), sp = document.querySelector('#strip-preview'), wrap = strip && strip.parentElement;
  if (strip && sp && window.matchMedia && matchMedia('(hover:hover) and (pointer:fine)').matches) {
    strip.classList.add('can-point');
    var marks = function(){ return strip.querySelectorAll('i'); }, cur = null, hideT = null;
    function show(el){
      clearTimeout(hideT);
      if (cur === el) return; cur = el;
      var r = contentById.get(el.dataset.id); if (!r) return;
      strip.classList.add('hot');
      marks().forEach(function(m){ m.classList.toggle('hl', m === el); m.classList.toggle('dim', m.dataset.g !== el.dataset.g); });
      sp.hidden = false; fit(sp, wrap.getBoundingClientRect().width); fill(sp, r);
    }
    function hide(){ cur = null; strip.classList.remove('hot'); marks().forEach(function(m){ m.classList.remove('hl', 'dim'); }); sp.hidden = true; }
    strip.addEventListener('mousemove', function(e){ var el = e.target.closest('i'); if (el) show(el); });
    strip.addEventListener('click', function(e){ var el = e.target.closest('i') || cur; if (!el) return; var r = contentById.get(el.dataset.id); hide(); if (r) openCard(r); });
    wrap.addEventListener('mouseleave', function(){ hideT = setTimeout(hide, 180); });
    wrap.addEventListener('mouseenter', function(){ clearTimeout(hideT); });
    sp.addEventListener('click', function(e){ if (e.target.closest('.pv-open')) hide(); });
  }

  // ---- field on the opening screen
  var field = document.querySelector('#field'), fp = document.querySelector('#field-preview');
  if (!field || !fp) return;
  var IDLE = 'Point at a square, or tap one, to see which operation it is.';
  var sizes = {}; recs.forEach(function(r){ var g = meaning(r); sizes[g] = (sizes[g] || 0) + 1; });
  var groups = Object.keys(sizes).sort(function(a, b){ return sizes[b] - sizes[a] || a.localeCompare(b); });
  var list = [], cells = [], rows = [], rowOf = [];
  groups.forEach(function(g, gi){
    var row = document.createElement('div'); row.className = 'f-row'; row.dataset.g = g;
    var name = document.createElement('button'); name.type = 'button'; name.className = 'f-name'; name.textContent = g; name.tabIndex = -1;
    var box = document.createElement('div'); box.className = 'f-cells';
    recs.filter(function(r){ return meaning(r) === g; }).sort(function(a, b){ return a.index - b.index; }).forEach(function(r){
      var k = list.length;
      var c = document.createElement('button'); c.type = 'button'; c.className = 'f-c'; c.tabIndex = -1; c.id = 'f-c-' + k;
      c.dataset.seenId = r.id; c.setAttribute('role', 'option'); c.setAttribute('aria-label', displayOperationName(r.locked.name));
      box.appendChild(c); list.push(r); cells.push(c); rowOf.push(gi);
    });
    name.addEventListener('click', function(){
      var first = -1; for (var k = 0; k < list.length; k++) { if (rowOf[k] === gi) { if (first < 0) first = k; if (!isSeen(list[k].id)) { first = k; break; } } }
      if (first >= 0) { setActive(first); field.focus({preventScroll:true}); }
    });
    row.appendChild(name); row.appendChild(box); field.appendChild(row); rows.push(row);
  });
  var active = -1, lastPointer = 'mouse';
  function setActive(i){
    active = i;
    cells.forEach(function(c, k){ c.classList.toggle('hl', k === i); c.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
    rows.forEach(function(r, gi){ r.classList.toggle('active', i >= 0 && rowOf[i] === gi); });
    fit(fp, fp.getBoundingClientRect().width);
    fill(fp, i >= 0 ? list[i] : null, IDLE);
    if (i >= 0) field.setAttribute('aria-activedescendant', cells[i].id);
  }
  field.addEventListener('pointerdown', function(e){ lastPointer = e.pointerType || 'mouse'; });
  cells.forEach(function(c, k){
    c.addEventListener('mouseenter', function(){ if (lastPointer === 'mouse') setActive(k); });
    c.addEventListener('click', function(){
      if (lastPointer !== 'mouse' && active !== k) { setActive(k); return; }   // first tap previews, second opens
      setActive(k); openCard(list[k]);
    });
  });
  field.addEventListener('keydown', function(e){
    var i = active < 0 ? 0 : active, to = null;
    if (e.key === 'ArrowRight') to = i + 1;
    else if (e.key === 'ArrowLeft') to = i - 1;
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      var gi = rowOf[i] + (e.key === 'ArrowDown' ? 1 : -1);
      if (gi >= 0 && gi < groups.length) to = rowOf.indexOf(gi);
    } else if ((e.key === 'Enter' || e.key === ' ') && active >= 0) { e.preventDefault(); openCard(list[active]); return; }
    if (to !== null) { e.preventDefault(); setActive(Math.max(0, Math.min(list.length - 1, to))); }
  });
  field.addEventListener('focus', function(){ if (active < 0) setActive(0); });
  var od = document.querySelector('#operation-dialog');
  if (od) od.addEventListener('close', function(){ if (active >= 0) fill(fp, list[active], IDLE); });
  // refit whenever the preview's width changes (first shown, window resized) and once the typeface has loaded
  function refit(){ fp.dataset.fitW = ''; if (sp) sp.dataset.fitW = ''; setActive(active); }
  if (window.ResizeObserver) { var lastW = 0; new ResizeObserver(function(){ var w = Math.round(fp.getBoundingClientRect().width); if (w && w !== lastW) { lastW = w; refit(); } }).observe(fp); }
  else { var t; window.addEventListener('resize', function(){ clearTimeout(t); t = setTimeout(refit, 150); }); }
  try { document.fonts.ready.then(refit); } catch (e) {}
  setActive(-1);
})();
</script>
"""
