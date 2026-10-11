"""Seen tally and a stronger collection map for the explorer (2026-10-11, work lane).
Counts the operations a visitor has opened, in this browser only (localStorage), shows the count and a strip of
144 cells under the header, and marks seen operations in the collection map."""
TALLY_HTML = '<div class="tally" id="tally"><span><b id="tally-n">0</b> of 144 seen</span></div>'
STRIP_HTML = '<div class="tally-strip" id="tally-strip" aria-hidden="true"></div>'
OPENING_MAP = """        <button class="route route-map" type="button" id="opening-map">
          <span><strong>Browse the whole collection</strong><small>All 144 operations, grouped by what they help you do.</small></span><span class="arrow" aria-hidden="true">→</span>
        </button>
"""
CSS = """
    .map-open { padding:9px 16px; border:1px solid var(--ink); background:var(--ink); color:var(--paper); font-size:15px; }
    .map-open:hover { background:var(--paper); color:var(--ink); }
    .tally { color:var(--muted); font-size:14px; white-space:nowrap; }
    .tally b { color:var(--ink); font-weight:500; }
    .tally-strip { display:grid; grid-template-columns:repeat(144,1fr); gap:1px; margin:-1px 0 0; padding:8px 0 0; }
    .tally-strip i { display:block; height:3px; background:var(--line); }
    .tally-strip i.on { background:var(--ink); }
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
  ids.forEach(function(id){ var c = document.createElement('i'); c.dataset.id = id; strip.appendChild(c); });
  function paint(){
    document.querySelector('#tally-n').textContent = set.size;
    strip.querySelectorAll('i').forEach(function(c){ c.classList.toggle('on', set.has(c.dataset.id)); });
    document.querySelectorAll('.map-operation[data-id]').forEach(function(b){ b.classList.toggle('seen', set.has(b.dataset.id)); });
  }
  window.__markSeen = function(id){
    if (set.has(id)) return; set.add(id);
    try { localStorage.setItem(KEY, JSON.stringify(Array.from(set))); } catch (err) {}
    paint();
  };
  window.__markMap = paint;
  var om = document.querySelector('#opening-map');
  if (om) om.addEventListener('click', function(){ document.querySelector('#open-map').click(); });
  var ob = document.querySelector('#onb-map');
  if (ob) ob.addEventListener('click', function(){ document.querySelector('#open-map').click(); });
  paint();
})();
</script>
"""
