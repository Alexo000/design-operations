"""netmap.py — Connections: a map of how the operations link (2026-10-17, work lane, rulings 1c and 2c; preview only).
Two layers on one canvas, with the same positions so a switch keeps every operation where it was:
  Where it leads — the card's own links (Next, Alternative, Pairs with, Escalation from the Network field);
  Families — what each operation builds on, read from the first capitalised words of its Move line (the rung).
    A rung that is an operation's name makes that operation the parent. A rung with no entry of its own that two or
    more operations share becomes a small word on the map (for example "remove"). A rung no other operation shares
    leaves the operation standing alone in this layer.
The whole network opens first on wide screens; clicking an operation puts it in the middle with its links around it.
Phones open straight on one operation. Positions are worked out here, at build time, so the page does no physics.
Showing families is new to the public tool: the display rule in THE SINGLE CORPUS needs a line (draft offered)."""
import json, re, math, random

RUNG = re.compile(r"([A-Z][A-Z'’ \-]*[A-Z])\b")
KIND = {'continueTo': 'next', 'alternative': 'instead', 'pairs': 'pair', 'escalation': 'further'}


def build(E, main, records):
    import networkx as nx
    ids = {r['number']: r['id'] for r in records}
    by_name = {E[k]['name']: k for k in main}
    # 1. where it leads
    nxt = []
    for r in records:
        for key, kind in KIND.items():
            for nm in r['editorial']['related'].get(key, []):
                if nm in by_name and by_name[nm] != r['number']:
                    nxt.append([r['id'], ids[by_name[nm]], kind])
    # 2. families from the Move line
    rung_of = {}
    for k in main:
        mv = dict(E[k]['fields']).get('Move', '')
        m = RUNG.match(mv)
        if m:
            rung_of[k] = m.group(1).strip()
    shared = {}
    for k, rg in rung_of.items():
        if rg not in by_name:
            shared.setdefault(rg, []).append(k)
    fam, hubs = [], []
    for k, rg in rung_of.items():
        if rg in by_name and by_name[rg] != k:
            fam.append([ids[by_name[rg]], ids[k]])
    for rg, ks in sorted(shared.items()):
        if len(ks) >= 2:
            hid = 'r:' + rg.lower()
            hubs.append({'id': hid, 'label': rg.lower()})
            fam += [[hid, ids[k]] for k in ks]
    W, H = 1400.0, 720.0   # pixel box the layouts are tidied in; the page stretches it to fit
    rid = [r['id'] for r in records]

    def grid(nodes, x0, x1, y0, cols):
        out = {}
        rows = max(1, math.ceil(len(nodes) / cols))
        dx = (x1 - x0) / cols; dy = min(64, (H - y0) / rows)
        for i, n in enumerate(nodes):
            out[n] = [x0 + dx * (i % cols + .5), y0 + dy * (i // cols + .5)]
        return out

    def spread(P, need, box):
        rnd = random.Random(3)
        x0, y0, x1, y1 = box
        keys = list(P)
        for _ in range(400):
            moved = False
            for i, a in enumerate(keys):
                for b in keys[i + 1:]:
                    dx = P[b][0] - P[a][0]; dy = P[b][1] - P[a][1]
                    d = math.hypot(dx, dy)
                    if d < need:
                        if d < 1e-6:
                            dx, dy, d = rnd.uniform(-1, 1), rnd.uniform(-1, 1), 1
                        push = (need - d) / 2; ux, uy = dx / d, dy / d
                        P[a][0] -= ux * push; P[a][1] -= uy * push
                        P[b][0] += ux * push; P[b][1] += uy * push
                        moved = True
            for q in P.values():
                q[0] = min(max(q[0], x0), x1); q[1] = min(max(q[1], y0), y1)
            if not moved:
                break
        return P

    # 3a. Where it leads: the linked ones spread on the left, the rest in a block on the right
    G = nx.Graph()
    for a, b, _ in nxt:
        G.add_edge(a, b)
    linked = [n for n in rid if n in G]
    lone = [n for n in rid if n not in G]
    pos = nx.spring_layout(G, seed=11, k=2.6 / math.sqrt(len(linked)), iterations=600)
    xs = [pos[n][0] for n in linked]; ys = [pos[n][1] for n in linked]
    XL = W * .76
    P = {n: [(pos[n][0] - min(xs)) / (max(xs) - min(xs)) * (XL - 60) + 30, (pos[n][1] - min(ys)) / (max(ys) - min(ys)) * (H - 60) + 30] for n in linked}
    P = spread(P, 60, (24, 24, XL - 24, H - 24))
    P.update(grid(lone, W * .8, W, 70, 4))
    pos_next = P
    lab_next = [{'t': 'No links yet', 'x': W * .9, 'y': 34}]

    # 3b. Families: one small tree per family, packed in rows; those standing alone in a block on the right
    parent = {c: p for p, c in fam}
    kids = {}
    for p, c in fam:
        kids.setdefault(p, []).append(c)
    nodes = set(parent) | set(kids)
    roots = sorted([n for n in nodes if n not in parent], key=lambda n: -len(kids.get(n, [])))

    def leaves(n):
        return sum(leaves(c) for c in kids.get(n, [])) if kids.get(n) else 1

    def depth(n):
        return 1 + max((depth(c) for c in kids.get(n, [])), default=0)
    DX, DY = 62.0, 70.0
    trees = []
    for r in roots:
        loc = {}

        def lay(n, x, d):
            ch = kids.get(n, [])
            if not ch:
                loc[n] = [x + DX / 2, d * DY]; return x + DX
            start = x
            for c in ch:
                x = lay(c, x, d + 1)
            loc[n] = [(start + x) / 2, d * DY]
            return x
        w = lay(r, 0, 0)
        trees.append((w, depth(r) * DY, loc))
    trees.sort(key=lambda t: -t[1])
    XF = W * .72
    Pf, x, y, rowh = {}, 0, 0, 0
    for w, h, loc in trees:
        if x + w > XF and x > 0:
            x, y, rowh = 0, y + rowh + 26, 0
        for n, q in loc.items():
            Pf[n] = [x + q[0], y + q[1] + DY / 2]
        x += w + 18; rowh = max(rowh, h)
    total_h = y + rowh
    sy = min(1.0, (H - 20) / total_h) if total_h else 1
    sx = (XF - 20) / max(q[0] for q in Pf.values())
    for q in Pf.values():
        q[0] = 10 + q[0] * min(sx, 1.25); q[1] = 10 + q[1] * sy
    alone = [n for n in rid if n not in nodes]
    Pf.update(grid(alone, W * .76, W, 70, 5))
    lab_family = [{'t': 'Standing alone', 'x': W * .88, 'y': 34}]

    pct = lambda P: {n: [round(3 + q[0] / W * 94, 2), round(4 + q[1] / H * 92, 2)] for n, q in P.items()}
    pl = lambda L: [{'t': l['t'], 'x': round(3 + l['x'] / W * 94, 2), 'y': round(4 + l['y'] / H * 92, 2)} for l in L]
    stats = {'next': len(nxt), 'family': len(fam), 'hubs': len(hubs), 'trees': len(trees),
             'alone_family': len(alone), 'alone_next': len(lone), 'family_rows_h': round(total_h), 'sy': round(sy, 2)}
    return {'next': nxt, 'family': fam, 'hubs': hubs, 'pos': {'next': pct(pos_next), 'family': pct(Pf)},
            'regions': {'next': pl(lab_next), 'family': pl(lab_family)}}, stats


BUTTON = '<button class="map-open net-open" id="open-net" type="button">Connections</button>'

HTML = """
  <dialog id="net-dialog" class="net-dialog" aria-labelledby="net-title">
    <div class="net-head">
      <div class="net-title-wrap">
        <h2 id="net-title">Connections</h2>
        <p class="net-sub" id="net-sub">How the operations link. Click one to see its links up close.</p>
      </div>
      <div class="net-tools">
        <div class="net-switch" role="radiogroup" aria-label="Which links to show">
          <button type="button" role="radio" aria-checked="true" data-layer="next">Where it leads</button>
          <button type="button" role="radio" aria-checked="false" data-layer="family">Families</button>
        </div>
        <input class="net-find" id="net-find" type="search" list="net-names" placeholder="Find an operation" aria-label="Find an operation">
        <datalist id="net-names"></datalist>
        <button class="map-close" id="net-close" type="button">Close</button>
      </div>
    </div>
    <div class="net-stage" id="net-stage">
      <svg class="net-edges" id="net-edges" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"></svg>
      <div class="net-labels" id="net-labels" aria-hidden="true"></div>
      <div class="net-nodes" id="net-nodes"></div>
    </div>
    <div class="net-legend" id="net-legend" aria-hidden="true"></div>
    <section class="net-focus" id="net-focus" hidden aria-live="polite"></section>
  </dialog>
"""

CSS = """
    /* connections 2026-10-17 */
    .header-tools .net-open { background:transparent; color:var(--ink); }
    .header-tools .net-open:hover { background:var(--ink); color:var(--paper); }
    .net-dialog { width:100vw; max-width:none; height:100dvh; max-height:none; margin:0; padding:0; border:0; background:var(--paper); color:var(--ink); }
    .net-dialog[open] { display:flex; flex-direction:column; }
    .net-dialog::backdrop { background:var(--paper); }
    .net-head { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:12px 24px; padding:18px 28px 14px; border-bottom:1px solid var(--line); }
    .net-head h2 { margin:0; font-size:26px; }
    .net-sub { margin:4px 0 0; color:var(--muted); font-size:14px; }
    .net-tools { display:flex; flex-wrap:wrap; align-items:center; gap:10px 18px; }
    .net-switch { display:inline-flex; border:1px solid var(--ink); }
    .net-switch button { width:auto; padding:6px 12px; border:0; background:transparent; color:var(--ink); font:inherit; font-size:14px; cursor:pointer; }
    .net-switch button[aria-checked="true"] { background:var(--ink); color:var(--paper); }
    .net-find { width:200px; padding:6px 10px; border:1px solid var(--line-strong); background:transparent; font:inherit; font-size:14px; color:var(--ink); }
    .net-stage { position:relative; flex:1 1 auto; min-height:0; overflow:hidden; }
    .net-edges { position:absolute; inset:0; width:100%; height:100%; }
    .net-edges line, .net-edges path { vector-effect:non-scaling-stroke; fill:none; stroke:var(--ink); stroke-width:1; opacity:.22; transition:opacity .25s; }
    .net-edges .k-instead { stroke-dasharray:4 4; }
    .net-edges .k-pair { stroke-dasharray:1 3; stroke-linecap:round; stroke-width:1.6; }
    .net-edges .k-further { stroke-width:2; }
    .net-edges .k-family { stroke-width:1.3; }
    .net-edges .k-from { stroke:var(--muted); }
    .net-stage.focus .net-edges .k-from.hot { opacity:.45; }
    .net-edges .hot { opacity:.9; }
    .net-stage.has-hot .net-edges :not(.hot) { opacity:.06; }
    .net-node { position:absolute; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:3px; width:auto; padding:0; border:0; background:transparent; color:var(--ink); font:inherit; cursor:pointer; transition:left .45s ease, top .45s ease, opacity .3s; z-index:1; }
    .net-node .nn-sym { display:flex; align-items:center; justify-content:center; width:38px; height:32px; background:var(--paper); border:1px solid transparent; }
    .net-node .nn-sym svg { width:32px; height:26px; }
    .net-node .nn-name { position:absolute; top:100%; left:50%; transform:translateX(-50%); margin-top:2px; padding:1px 5px; background:var(--paper); font-size:12px; white-space:nowrap; opacity:0; pointer-events:none; transition:opacity .15s; }
    .net-node:hover .nn-sym, .net-node:focus-visible .nn-sym { border-color:var(--ink); }
    .net-node:hover .nn-name, .net-node:focus-visible .nn-name, .net-node.show-name .nn-name { opacity:1; }
    .net-node:focus-visible { outline:none; }
    .net-node:hover, .net-node:focus-visible { z-index:3; }
    .net-stage.has-hot .net-node:not(.hot) { opacity:.18; }
    .net-label { position:absolute; transform:translate(-50%,-50%); font-size:12px; font-style:italic; color:var(--muted); background:var(--paper); padding:0 3px; transition:left .45s ease, top .45s ease, opacity .3s; pointer-events:none; }
    .net-stage.layer-next .net-label { opacity:0; }
    .net-stage.has-hot .net-label:not(.hot) { opacity:.1; }
    .net-stage.layer-next.has-hot .net-label:not(.hot) { opacity:0; }
    /* focus */
    .net-stage.focus .net-node:not(.hot) { opacity:0; pointer-events:none; }
    .net-stage.focus .net-label:not(.hot) { opacity:0; }
    .net-stage.focus .net-node.hot .nn-name { opacity:1; font-size:13px; }
    .net-stage.focus .net-node.centre { z-index:4; }
    .net-stage.focus .net-node.centre .nn-sym { width:64px; height:54px; border-color:var(--ink); }
    .net-stage.focus .net-node.centre .nn-sym svg { max-width:52px; max-height:42px; }
    .net-stage.focus .net-node.centre .nn-name { font-size:16px; font-weight:500; }
    .net-sector { position:absolute; z-index:5; transform:translate(-50%,-50%); padding:1px 4px; background:var(--paper); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); white-space:nowrap; pointer-events:none; }
    .net-region { position:absolute; transform:translate(-50%,-50%); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); pointer-events:none; }
    .net-stage.has-hot .net-region { opacity:.3; }
    .net-legend { display:flex; flex-wrap:wrap; gap:6px 22px; padding:10px 28px; border-top:1px solid var(--line); font-size:13px; color:var(--muted); }
    .net-legend span { display:inline-flex; align-items:center; gap:8px; }
    .net-legend svg { width:34px; height:8px; }
    .net-legend line { stroke:var(--ink); }
    .net-focus { display:flex; flex-wrap:wrap; align-items:baseline; gap:8px 22px; padding:14px 28px 18px; border-top:1px solid var(--line-strong); }
    .net-focus h3 { margin:0; font-size:20px; }
    .net-focus p { margin:0; flex:1 1 320px; color:var(--ink); font-size:15px; }
    .net-focus .nf-actions { display:flex; gap:16px; align-items:center; }
    .net-focus button { width:auto; padding:6px 12px; border:1px solid var(--ink); background:transparent; color:var(--ink); font:inherit; font-size:14px; cursor:pointer; }
    .net-focus button.nf-open { background:var(--ink); color:var(--paper); }
    .net-focus .nf-empty { color:var(--muted); }
    .net-link { margin:22px 0 0; }
    .net-link button { width:auto; padding:4px 0; border:0; border-bottom:1px solid var(--ink); background:transparent; font:inherit; font-size:16px; color:var(--ink); cursor:pointer; }
    @media (max-width:720px) {
      .net-head { padding:14px 16px 10px; }
      .net-head h2 { font-size:22px; }
      .net-sub { display:none; }
      .net-find { width:150px; }
      .net-legend { padding:8px 16px; }
      .net-focus { padding:12px 16px 14px; }
      .net-stage.focus .net-node.hot .nn-name { font-size:12px; white-space:normal; width:92px; text-align:center; }
      .net-stage.focus .net-node.centre .nn-name { width:auto; white-space:nowrap; }
      .net-btn-overview { display:none; }
      .net-dialog[open] { overflow-y:auto; }
      .net-stage { flex:none; }
      .net-stage.focus .net-node.hot .nn-name { width:110px; }
    }
    @media (prefers-reduced-motion:reduce) { .net-node, .net-label { transition:none; } }
"""

JS_TMPL = r"""
<script>
(function(){
  var NET = __DATA__;
  var dlg = document.querySelector('#net-dialog'); if (!dlg) return;
  var stage = dlg.querySelector('#net-stage'), svg = dlg.querySelector('#net-edges'), nodesBox = dlg.querySelector('#net-nodes'),
      labelsBox = dlg.querySelector('#net-labels'), legend = dlg.querySelector('#net-legend'), focusBox = dlg.querySelector('#net-focus'),
      sub = dlg.querySelector('#net-sub'), find = dlg.querySelector('#net-find');
  var layer = 'next', centre = null, els = {}, narrow = function(){ return window.matchMedia('(max-width:720px)').matches; };
  var NAME = {}, HUB = {};
  contentRecords.forEach(function(r){ NAME[r.id] = displayOperationName(r.locked.name); });
  NET.hubs.forEach(function(h){ HUB[h.id] = h.label; });
  var KINDS = {next:'Continue to', instead:'Try instead', pair:'Works as a pair with', further:'To go further', from:'Leads here'};
  // nodes
  contentRecords.forEach(function(r){
    var b = document.createElement('button'); b.type = 'button'; b.className = 'net-node'; b.dataset.id = r.id;
    b.setAttribute('aria-label', NAME[r.id]);
    b.innerHTML = '<span class="nn-sym" aria-hidden="true">' + (r.locked.symbol || '') + '</span><span class="nn-name">' + NAME[r.id] + '</span>';
    nodesBox.appendChild(b); els[r.id] = b;
  });
  NET.hubs.forEach(function(h){
    var s = document.createElement('span'); s.className = 'net-label'; s.dataset.id = h.id; s.textContent = h.label;
    labelsBox.appendChild(s); els[h.id] = s;
  });
  var dl = dlg.querySelector('#net-names');
  dl.innerHTML = contentRecords.map(function(r){ return '<option value="' + NAME[r.id].replace(/"/g, '&quot;') + '">'; }).join('');
  function place(id, xy){ var e = els[id]; if (!e) return; e.style.left = xy[0] + '%'; e.style.top = xy[1] + '%'; e._xy = xy; }
  function edgesOf(id){
    if (layer === 'next') return NET.next.filter(function(e){ return e[0] === id || e[1] === id; });
    return NET.family.filter(function(e){ return e[0] === id || e[1] === id; });
  }
  function line(a, b, cls){ return '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + b[0] + '" y2="' + b[1] + '" class="' + cls + '"/>'; }
  function drawRegions(){
    stage.querySelectorAll('.net-region').forEach(function(x){ x.remove(); });
    (NET.regions[layer] || []).forEach(function(l){ var e = document.createElement('span'); e.className = 'net-region'; e.textContent = l.t; e.style.left = l.x + '%'; e.style.top = l.y + '%'; stage.appendChild(e); });
  }
  function elbow(a, b, cls){ var m = (a[1] + b[1]) / 2; return '<path d="M' + a[0] + ' ' + a[1] + ' V' + m + ' H' + b[0] + ' V' + b[1] + '" class="' + cls + '"/>'; }
  function drawAll(){
    var list = layer === 'next' ? NET.next.map(function(e){ return [e[0], e[1], 'k-' + e[2]]; }) : NET.family.map(function(e){ return [e[0], e[1], 'k-family']; });
    svg.innerHTML = list.map(function(e){ var a = els[e[0]]._xy, b = els[e[1]]._xy; var c = e[2] + ' e-' + e[0].replace(':', '_') + ' e-' + e[1].replace(':', '_'); return a && b ? (layer === 'family' ? elbow(a, b, c) : line(a, b, c)) : ''; }).join('');
  }
  function drawLegend(){
    var row = function(cls, t){ return '<span><svg viewBox="0 0 34 8"><line x1="1" y1="4" x2="33" y2="4" class="' + cls + '" style="vector-effect:none"/></svg>' + t + '</span>'; };
    var dash = {'k-next':'', 'k-instead':' stroke-dasharray="4 4"', 'k-pair':' stroke-dasharray="1 3" stroke-linecap="round" stroke-width="1.6"', 'k-further':' stroke-width="2"'};
    if (layer === 'next') {
      legend.innerHTML = ['next','instead','pair','further'].map(function(k){ return '<span><svg viewBox="0 0 34 8"><line x1="1" y1="4" x2="33" y2="4"' + dash['k-' + k] + '/></svg>' + KINDS[k] + '</span>'; }).join('')
        + '<span>' + NET.next.length + ' links · ' + contentRecords.filter(function(r){ return !NET.next.some(function(e){ return e[0] === r.id || e[1] === r.id; }); }).length + ' operations have none yet</span>';
    } else {
      legend.innerHTML = '<span><svg viewBox="0 0 34 8"><line x1="1" y1="4" x2="33" y2="4" stroke-width="1.3"/></svg>Builds on</span><span><i>remove</i>&nbsp; a shared root with no operation of its own</span>';
    }
  }
  function overview(){
    centre = null; stage.classList.remove('focus', 'has-hot'); focusBox.hidden = true; legend.hidden = false;
    stage.querySelectorAll('.net-sector').forEach(function(s){ s.remove(); });
    Object.keys(els).forEach(function(id){ els[id].classList.remove('hot', 'centre', 'show-name'); place(id, NET.pos[layer][id] || [50, 50]); });
    drawRegions();
    if (layer === 'family') NET.family.forEach(function(e){ if (!e[0].startsWith('r:') && !NET.family.some(function(f){ return f[1] === e[0]; })) els[e[0]].classList.add('show-name'); });
    sub.textContent = 'How the operations link. Click one to see its links up close.';
    drawAll(); drawLegend();
  }
  function hover(id){
    if (centre) return;
    stage.classList.toggle('has-hot', !!id);
    Object.keys(els).forEach(function(k){ els[k].classList.remove('hot'); });
    svg.querySelectorAll('.hot').forEach(function(l){ l.classList.remove('hot'); });
    if (!id) return;
    els[id].classList.add('hot');
    edgesOf(id).forEach(function(e){ els[e[0]].classList.add('hot'); els[e[1]].classList.add('hot'); });
    svg.querySelectorAll('.e-' + id.replace(':', '_')).forEach(function(l){ l.classList.add('hot'); });
  }
  function ring(ids, a0, a1, rx, ry){
    var out = {}, n = ids.length;
    ids.forEach(function(id, i){
      var t = n === 1 ? (a0 + a1) / 2 : a0 + (a1 - a0) * (i / (n - 1));
      var r = n > 4 ? (i % 2 ? 1 : .74) : 1;
      out[id] = [50 + Math.cos(t) * rx * r, 50 + Math.sin(t) * ry * r];
    });
    return out;
  }
  function focus(id){
    centre = id; stage.classList.add('focus', 'has-hot'); stage.querySelectorAll('.net-sector').forEach(function(s){ s.remove(); });
    Object.keys(els).forEach(function(k){ els[k].classList.remove('hot', 'centre', 'show-name'); });
    var small = narrow(), rx = small ? 34 : 30, ry = small ? 38 : 34;
    var groups = {};
    if (layer === 'next') {
      NET.next.forEach(function(e){
        if (e[0] === id) (groups[e[2]] = groups[e[2]] || []).push(e[1]);
        else if (e[1] === id) (groups.from = groups.from || []).push(e[0]);
      });
      Object.keys(groups).forEach(function(k){ groups[k] = groups[k].filter(function(x, i, a){ return a.indexOf(x) === i; }); });
      // a link both ways is shown once, under the card's own heading
      if (groups.from) groups.from = groups.from.filter(function(x){ return !['next','instead','pair','further'].some(function(k){ return (groups[k] || []).indexOf(x) >= 0; }); });
      var S = {further:[-2.05, -1.1], next:[-0.6, 0.6], instead:[0.9, 1.5], from:[1.65, 2.25], pair:[2.55, 3.7]};
    } else {
      var parent = null, kids = [], sibs = [];
      NET.family.forEach(function(e){ if (e[1] === id) parent = e[0]; if (e[0] === id) kids.push(e[1]); });
      if (parent) NET.family.forEach(function(e){ if (e[0] === parent && e[1] !== id) sibs.push(e[1]); });
      if (parent) groups.parent = [parent];
      if (kids.length) groups.kids = kids;
      if (sibs.length) groups.sibs = sibs;
      var S = {parent:[-1.5708, -1.5708], kids:[0.5, 2.64], sibs:[-0.35, 0.35]};
      if (sibs.length > 1) { groups.sibsR = sibs.filter(function(x, i){ return i % 2 === 0; }); groups.sibs = sibs.filter(function(x, i){ return i % 2 === 1; }); }
    }
    var LBL = {further:'To go further', next:'Continue to', instead:'Try instead', pair:'Works as a pair with', from:'Leads here', parent:'Builds on', kids:'Built on it', sibs:'Same root', sibsR:'Same root'};
    var placed = {};
    stage.style.height = '';
    if (small) {
      // phones: rows above and below the operation, sides beside it, so names never collide
      var PER = 3, ROWH = 96, rows = [], y = 34;
      var above = layer === 'next' ? ['further'] : ['parent'];
      var below = layer === 'next' ? ['instead', 'from'] : ['sibsR', 'sibs', 'kids'];
      var side = layer === 'next' ? {pair:'L', next:'R'} : {};
      if (layer === 'family' && groups.sibs) { groups.sibsR = (groups.sibsR || []).concat(groups.sibs); delete groups.sibs; }
      function addRows(k){
        var list = groups[k]; if (!list || !list.length) return;
        rows.push({label:k, y:y}); y += 26;
        for (var i = 0; i < list.length; i += PER) {
          var chunk = list.slice(i, i + PER);
          chunk.forEach(function(n, j){ if (!placed[n]) placed[n] = [(j + .5) / chunk.length * 100, y + 26]; });
          y += ROWH;
        }
      }
      above.forEach(addRows);
      var cy = y + 50, sideRows = Math.max((groups.pair || []).length, (groups.next || []).length, 1);
      if (side.pair || side.next) {
        ['pair', 'next'].forEach(function(k){
          var list = groups[k] || []; if (!list.length) return;
          rows.push({label:k, y:cy - 64, x:k === 'pair' ? 16 : 84});
          list.forEach(function(n, j){ if (!placed[n]) placed[n] = [k === 'pair' ? 15 : 85, cy + (j - (list.length - 1) / 2) * 78]; });
        });
      }
      placed[id] = [50, cy];
      y = cy + Math.max(80, (sideRows - 1) / 2 * 78 + 60);
      below.forEach(addRows);
      var total = Math.max(y + 10, stage.parentNode.clientHeight * .6);
      stage.style.height = total + 'px';
      Object.keys(placed).forEach(function(n){ placed[n] = [placed[n][0], placed[n][1] / total * 100]; });
      rows.forEach(function(r){
        var lab = document.createElement('span'); lab.className = 'net-sector'; lab.textContent = LBL[r.label];
        lab.style.top = (r.y / total * 100) + '%';
        if (r.x === 16) { lab.style.left = '8px'; lab.style.transform = 'translateY(-50%)'; }
        else if (r.x === 84) { lab.style.left = 'auto'; lab.style.right = '8px'; lab.style.transform = 'translateY(-50%)'; }
        else lab.style.left = '50%';
        stage.appendChild(lab);
      });
    } else {
    // each kind of link always sits in the same direction, so the picture reads the same on every operation
    var DIR = layer === 'next'
      ? {further:[-Math.PI / 2, 1.5], next:[0, 1.3], instead:[Math.PI * .34, .85], from:[Math.PI * .66, .85], pair:[Math.PI, 1.3]}
      : {parent:[-Math.PI / 2, .9], sibsR:[0, 1.3], kids:[Math.PI / 2, 2.0], sibs:[Math.PI, 1.3]};
    placed[id] = [50, 50];
    Object.keys(DIR).forEach(function(k){
      var list = groups[k]; if (!list || !list.length) return;
      var c = DIR[k][0], span = Math.min(DIR[k][1] * (small ? 1.45 : 1), (list.length - 1) * (small ? .5 : .34));
      if (small && k === 'from') c = Math.PI * .72; if (small && k === 'instead') c = Math.PI * .26;
      var p = ring(list, c - span / 2, c + span / 2, rx, ry);
      Object.keys(p).forEach(function(n){ if (!placed[n]) placed[n] = p[n]; });
      var lab = document.createElement('span'); lab.className = 'net-sector';
      var lx = 50 + Math.cos(c) * rx * (small ? 1.0 : 1.32), ly = 50 + Math.sin(c) * ry * (small ? 1.36 : 1.3);
      if (small && Math.abs(Math.cos(c)) > .5) ly = 50 + Math.sin(c) * ry + (Math.sin(c) < -.1 ? -14 : 12);
      lab.textContent = LBL[k]; lab.style.left = Math.min(Math.max(lx, small ? 24 : 8), small ? 76 : 92) + '%'; lab.style.top = Math.min(Math.max(ly, 4), 96) + '%';
      stage.appendChild(lab);
    });
    }
    Object.keys(els).forEach(function(k){ place(k, placed[k] || NET.pos[layer][k] || [50, 50]); });
    stage.querySelectorAll('.net-region').forEach(function(x){ x.remove(); });
    Object.keys(placed).forEach(function(k){ els[k].classList.add('hot'); });
    els[id].classList.add('centre');
    var ln = [];
    if (layer === 'next') {
      Object.keys(groups).forEach(function(k){ groups[k].forEach(function(n){ ln.push(line(placed[id], placed[n], 'hot k-' + k)); }); });
    } else {
      Object.keys(groups).forEach(function(k){ groups[k].forEach(function(n){
        if (k === 'sibs' || k === 'sibsR') { if (groups.parent) ln.push(line(placed[groups.parent[0]], placed[n], 'hot k-family')); }
        else ln.push(line(placed[id], placed[n], 'hot k-family'));
      }); });
    }
    svg.innerHTML = ln.join('');
    legend.hidden = true;
    var r = contentById.get(id), count = Object.keys(placed).length - 1;
    focusBox.hidden = false;
    focusBox.innerHTML = '<h3>' + NAME[id] + '</h3><p>' + (r.locked.canonicalDefinition || '') + (count ? '' : ' <span class="nf-empty">' + (layer === 'next' ? 'No links yet in Where it leads. Try Families.' : 'Stands alone: nothing it builds on, and nothing built on it.') + '</span>') + '</p>'
      + '<div class="nf-actions"><button type="button" class="nf-open">Open the card</button><button type="button" class="nf-back net-btn-overview">Whole map</button></div>';
    focusBox.querySelector('.nf-open').addEventListener('click', function(){ openOperationDetail(id, 'net'); });
    focusBox.querySelector('.nf-back').addEventListener('click', overview);
    sub.textContent = layer === 'next' ? 'Where ' + NAME[id] + ' leads, and what leads to it. Click any operation to move to it.' : 'What ' + NAME[id] + ' builds on, and what is built on it.';
    els[id].focus({preventScroll:true});
  }
  nodesBox.addEventListener('mouseover', function(e){ var b = e.target.closest('.net-node'); if (b && !narrow()) hover(b.dataset.id); });
  nodesBox.addEventListener('mouseleave', function(){ hover(null); });
  nodesBox.addEventListener('click', function(e){
    var b = e.target.closest('.net-node'); if (!b) return;
    if (centre === b.dataset.id) { openOperationDetail(b.dataset.id, 'net'); return; }
    focus(b.dataset.id);
  });
  dlg.querySelectorAll('.net-switch button').forEach(function(b){ b.addEventListener('click', function(){
    layer = b.dataset.layer;
    dlg.querySelectorAll('.net-switch button').forEach(function(x){ x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
    stage.classList.toggle('layer-next', layer === 'next');
    if (centre) focus(centre); else overview();
  }); });
  find.addEventListener('change', function(){
    var v = find.value.trim().toLowerCase(), hit = contentRecords.find(function(r){ return NAME[r.id].toLowerCase() === v; });
    if (hit) { focus(hit.id); find.value = ''; }
  });
  dlg.querySelector('#net-close').addEventListener('click', function(){ dlg.close(); });
  dlg.addEventListener('keydown', function(e){ if (e.key === 'Escape' && centre && !narrow()) { e.preventDefault(); overview(); } });
  window.__openNet = function(id){
    stage.classList.toggle('layer-next', layer === 'next');
    if (!dlg.open) dlg.showModal();
    overview();
    var start = id || (narrow() ? contentRecords[Math.floor(Math.random() * contentRecords.length)].id : null);
    if (start) requestAnimationFrame(function(){ focus(start); });
  };
  var openBtn = document.querySelector('#open-net');
  if (openBtn) openBtn.addEventListener('click', function(){ window.__openNet(null); });
  // every card links to its place on the map
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var old = box.querySelector('.net-link'); if (old) old.remove();
    var p = document.createElement('p'); p.className = 'net-link';
    p.innerHTML = '<button type="button">See how it connects →</button>';
    p.querySelector('button').addEventListener('click', function(){ window.__openNet(id); });
    var note = box.querySelector('.operation-profile-note');
    if (note) box.insertBefore(p, note); else box.appendChild(p);
    return out;
  };
})();
</script>
"""


def js(data):
    return JS_TMPL.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
