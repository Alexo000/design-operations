"""Usability pass of 2026-10-11 (work lane), items 1, 2, 4, 5, 6 and 12 of the journey review:
1  the browser's Back button steps back through the explorer instead of leaving it;
2  every operation has its own link (#slug) that opens its card, plus a 'Copy link' button on the card;
4  results show three to five picks, each with a one-line 'why this one', and the count of other possibilities;
5  the 'Try this' on a result is the same task the card shows first (set in build_explorer.py);
6  visitor-facing codes and jargon removed (DO numbers, 'Public beta', 'movement', 'drawer'); map groups headed in plain words;
12 the page's typeface is loaded from Google Fonts (IBM Plex Sans since 2026-10-11, ruling 1b; was Atkinson Hyperlegible)."""

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap">')

CSS = """
    .result-why { margin:12px 0 0; color:var(--muted); font-size:14px; }
    .result-why b { color:var(--ink); font-weight:400; }
    .operation-dialog-bar .copy-link { margin-left:auto; margin-right:18px; }
"""


def patch_js(njs, rep):
    # 6: codes and jargon
    njs = rep(njs, "heading.textContent = displayOperationName(movement);", "heading.textContent = movementMeanings[movement] || displayOperationName(movement);", 'map heading')
    njs = rep(njs, ".sort(([movementA], [movementB]) => movementA.localeCompare(movementB))",
              ".sort(([movementA], [movementB]) => (movementMeanings[movementA] || movementA).localeCompare(movementMeanings[movementB] || movementB))", 'map sort')
    njs = rep(njs, "name.innerHTML = `${displayOperationName(operation.name)} <small>${operation.id}</small>`;", "name.textContent = displayOperationName(operation.name);", 'map name')
    njs = rep(njs, "<div><small>${operation.id}</small><h3>", "<div><h3>", 'map detail id')
    njs = rep(njs, " · ${operation.conditions.map(displayOperationName).join(' · ')}</p>`;", "</p>`;", 'map detail codes')
    njs = rep(njs, '<div class="result-number">${operation.id}</div>', '', 'result id')
    njs = rep(njs, "<span class=\"operation-number\">'+record.id+'</span>", "", 'card id')
    njs = rep(njs, "record.id+' · '+record.index+' of '+contentRecords.length", "record.index+' of '+contentRecords.length", 'position')
    # 4: fuller results with reasons
    njs = rep(njs, "      ).slice(0, 8);\n      return {exploratory, primary, more};",
              "      ).slice(0, 8);\n      while (primary.length < 3 && more.length) primary.push(more.shift());\n      return {exploratory, primary, more};", 'min three')
    njs = rep(njs, "document.querySelector('#result-more-label').textContent = exploratory ? 'More from the collection' : 'Other possibilities';",
              "document.querySelector('#result-more-label').textContent = (exploratory ? 'More from the collection' : 'Other possibilities') + (moreResults.length ? ' (' + moreResults.length + ')' : '');", 'more count')
    njs = rep(njs, "          ${taskBlock}\n          ${definition}",
              "          ${taskBlock}\n          ${(operation.reasons || []).filter(r => r !== 'fits the practical limits').length ? `<p class=\"result-why\"><b>Why this one:</b> ${(operation.reasons || []).filter(r => r !== 'fits the practical limits').slice(0, 2).join('; ')}.</p>` : ''}\n          ${definition}", 'why')
    return njs


def patch_html(npage, rep):
    npage = rep(npage, '<div class="brand">Design Operations <span class="beta-label">Public beta</span></div>', '<div class="brand">Design Operations</div>', 'beta label')
    npage = rep(npage, '<small>Open a drawer in the collection.</small>', '<small>See a varied set from the collection.</small>', 'drawer')
    npage = npage.replace('Search by operation or movement', 'Search by name or any word')
    npage = rep(npage, 'Browse all 144 operations by the kind of movement they make, or search by name, former name or word.',
                'Browse all 144 operations, grouped by what they help you do, or search by name, former name or any word.', 'map intro')
    npage = npage.replace('<head>', '<head>' + FONT, 1)
    npage = npage.replace('</style>', CSS + '  </style>', 1)
    return npage


JS = r"""
<script>
(function(){
  var od = document.querySelector('#operation-dialog'), md = document.querySelector('#collection-map');
  var handling = false, ignorePop = false, goingBack = false, closingFromPop = false, closingMapFromPop = false, suppressMapClose = false;
  function slug(name){ return String(name).toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  var bySlug = {}; contentRecords.forEach(function(r){ bySlug[slug(r.locked.name)] = r.id; });
  function slugOf(id){ var r = contentById.get(id); return r ? slug(r.locked.name) : ''; }
  function stepState(){ if (handling || goingBack) { goingBack = false; history.replaceState({layer:'step'}, '', location.pathname + location.search); } else history.pushState({layer:'step'}, '', location.pathname + location.search); }
  ['showRoute','showFollowup','showConditionMovement','showMovementContext','showLimits','showResults','showOpening'].forEach(function(n){
    var f = window[n]; if (typeof f !== 'function') return;
    window[n] = function(){ var out = f.apply(this, arguments); stepState(); return out; };
  });
  if (window.__openOnboard) { var oo = window.__openOnboard; window.__openOnboard = function(){ oo(); stepState(); }; }
  ['.back', '.back-to-answers', '.how-open'].forEach(function(sel){
    document.querySelectorAll(sel).forEach(function(b){ b.addEventListener('click', function(){ goingBack = true; }, true); });
  });
  var origOpen = openOperationDetail;
  openOperationDetail = function(id, origin, invoker){
    if (md.open) suppressMapClose = true;
    origOpen(id, origin, invoker);
    if (!handling) history.pushState({layer:'card'}, '', '#' + slugOf(id));
  };
  var origRender = renderOperationDetail;
  renderOperationDetail = function(id){ origRender(id); if (od.open && history.state && history.state.layer === 'card') history.replaceState({layer:'card'}, '', '#' + slugOf(id)); };
  od.addEventListener('close', function(){
    if (closingFromPop) { closingFromPop = false; return; }
    if (history.state && history.state.layer === 'card') { ignorePop = true; history.back(); }
  });
  md.addEventListener('close', function(){
    if (suppressMapClose) { suppressMapClose = false; return; }
    if (closingMapFromPop) { closingMapFromPop = false; return; }
    if (history.state && history.state.layer === 'map') { ignorePop = true; history.back(); }
  });
  document.querySelector('#open-map').addEventListener('click', function(){ history.pushState({layer:'map'}, '', '#collection'); });
  window.addEventListener('popstate', function(){
    if (ignorePop) { ignorePop = false; return; }
    handling = true;
    try {
      var opening = document.querySelector('#opening'), branch = document.querySelector('#branch'), results = document.querySelector('#results'), onboard = document.querySelector('#onboard');
      if (od.open) { closingFromPop = true; od.close(); }
      else if (md.open) { closingMapFromPop = true; md.close(); }
      else if (!results.hidden) document.querySelector('.back-to-answers').click();
      else if (!branch.hidden) document.querySelector('.back').click();
      else if (!opening.hidden && onboard && window.__openOnboard) window.__openOnboard();
    } finally { handling = false; }
  });
  // copy link
  var bar = document.querySelector('.operation-dialog-bar');
  if (bar) {
    var cl = document.createElement('button'); cl.type = 'button'; cl.className = 'copy-link'; cl.textContent = 'Copy link';
    cl.addEventListener('click', function(){
      var url = location.href, done = function(){ cl.textContent = 'Link copied'; setTimeout(function(){ cl.textContent = 'Copy link'; }, 1600); };
      try { navigator.clipboard.writeText(url).then(done, function(){ cl.textContent = url; }); } catch (err) { cl.textContent = url; }
    });
    var closeBtn = bar.querySelector('#operation-close'); bar.insertBefore(cl, closeBtn);
  }
  history.replaceState({layer:'step'}, '', location.pathname + location.search + location.hash);
  // deep links
  var h = location.hash.replace(/^#/, '');
  if (h && bySlug[h]) {
    var on = document.querySelector('#onboard'); if (on && !on.hidden) { handling = true; showOpening(); handling = false; }
    history.replaceState({layer:'step'}, '', location.pathname + location.search);
    openOperationDetail(bySlug[h], 'results', null);
  } else if (h === 'collection') {
    history.replaceState({layer:'step'}, '', location.pathname + location.search);
    document.querySelector('#open-map').click();
  }
})();
</script>
"""
