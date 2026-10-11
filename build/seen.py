"""Seen tally and a stronger collection map for the explorer (2026-10-11, work lane).
Counts the operations a visitor has opened, in this browser only (localStorage), shows the count and a strip of
144 cells under the header, and marks seen operations in the collection map.
2026-10-11: strip in group order with gaps and two tones (ruling d); paint() also marks any [data-seen-id] element (the field)."""
TALLY_HTML = '<div class="tally" id="tally"><span><b id="tally-n">0</b> of 144 seen</span></div>'
STRIP_HTML = '<div class="strip-wrap"><div class="tally-strip" id="tally-strip" aria-hidden="true"></div><div class="op-preview strip-preview" id="strip-preview" hidden></div></div>'
OPENING_MAP = """        <button class="route route-map" type="button" id="opening-map">
          <span><strong>Browse the whole collection</strong><small>All 144 operations, grouped by what they help you do.</small></span><span class="arrow" aria-hidden="true">→</span>
        </button>
"""
CSS = """
    .map-open { padding:9px 16px; border:1px solid var(--ink); background:var(--ink); color:var(--paper); font-size:15px; }
    .map-open:hover { background:var(--paper); color:var(--ink); }
    .tally { color:var(--muted); font-size:14px; white-space:nowrap; }
    .tally b { color:var(--ink); font-weight:500; }
    /* 2026-10-11 (ruling d): the strip runs in the collection map's group order, a small gap between groups,
       two greys taking turns; on screens with a pointer, hovering a mark previews it (discover.py) */
    .strip-wrap { position:relative; }
    .tally-strip { display:flex; align-items:flex-start; height:20px; margin:-1px 0 0; padding:7px 0 0; }
    .tally-strip i { flex:1 1 0; min-width:0; height:13px; padding:0 .5px; }
    .tally-strip i::after { content:''; display:block; height:3px; background:#d6d6ce; transition:height .12s ease, background .12s ease, opacity .12s ease; }
    .tally-strip i.tb::after { background:#b0b0a7; }
    .tally-strip i.on::after { background:var(--ink); }
    .tally-strip .gap { flex:0 0 4px; }
    .route-map { border-style:dashed; }
    .map-operation.seen > span:first-child::before { content:'●'; font-size:9px; margin-right:7px; vertical-align:2px; }
    .map-operation:not(.seen) > span:first-child::before { content:'○'; font-size:9px; margin-right:7px; vertical-align:2px; color:var(--muted); }
"""
JS = """
<script>
(function(){
  var KEY = 'do-seen', seen = [];
  try { seen = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (err) { seen = []; }
  var set = new Set(seen), ids = contentRecords.map(function(r){ return r.id; });
  var strip = document.querySelector('#tally-strip');
  // group order as in the collection map (by what they help you do), then by number
  var meaning = function(r){ var m = r.locked.profile.primaryMovement; return (typeof movementMeanings !== 'undefined' && movementMeanings[m]) || m; };
  var ordered = contentRecords.slice().sort(function(a, b){ return meaning(a).localeCompare(meaning(b)) || a.index - b.index; });
  var lastG = null, tone = false;
  ordered.forEach(function(r){
    var g = meaning(r);
    if (lastG !== null && g !== lastG) { var gap = document.createElement('span'); gap.className = 'gap'; strip.appendChild(gap); tone = !tone; }
    var c = document.createElement('i'); c.dataset.id = r.id; c.dataset.g = g; if (tone) c.className = 'tb'; strip.appendChild(c); lastG = g;
  });
  function paint(){
    document.querySelector('#tally-n').textContent = set.size;
    strip.querySelectorAll('i').forEach(function(c){ c.classList.toggle('on', set.has(c.dataset.id)); });
    document.querySelectorAll('.map-operation[data-id]').forEach(function(b){ b.classList.toggle('seen', set.has(b.dataset.id)); });
    document.querySelectorAll('[data-seen-id]').forEach(function(el){ el.classList.toggle('seen', set.has(el.dataset.seenId)); });
  }
  window.__markSeen = function(id){
    if (set.has(id)) return; set.add(id);
    try { localStorage.setItem(KEY, JSON.stringify(Array.from(set))); } catch (err) {}
    paint();
  };
  window.__markMap = paint;
  window.__isSeen = function(id){ return set.has(id); };
  var om = document.querySelector('#opening-map');
  if (om) om.addEventListener('click', function(){ document.querySelector('#open-map').click(); });
  var ob = document.querySelector('#onb-map');
  if (ob) ob.addEventListener('click', function(){ document.querySelector('#open-map').click(); });
  paint();
})();
</script>
"""
