"""Onboarding step for the explorer (ruling 1a of 2026-10-11, work lane): a short opening screen with one worked
example from outside design, a 'Show me another' button cycling five, then into the existing questions.
The five examples are new visitor copy, desk-written 2026-10-11 and not yet through Front of House.
Each 'what you'd do' is adapted from the operation's In the process (Try now S) task."""
import json

EXAMPLES = [
    {'field': 'Teaching', 'id': 'DO-071',
     'situation': 'Your lessons have started to feel the same every week.',
     'do': 'For one week, keep a list of the last three ways you ran an activity, such as a quiz, pair work or a short talk. Anything on the list is off-limits for the next lesson. Stop at the end of the week and look at what you used instead.'},
    {'field': 'Running a team', 'id': 'DO-118',
     'situation': 'Team meetings drift, and nobody is quite sure who decides.',
     'do': 'Give one person the chair until a date you all agree now, say the end of the month. On that date the role ends unless the team chooses to renew it. Stop on that date.'},
    {'field': 'Research', 'id': 'DO-001',
     'situation': 'Your process has grown to twenty steps and you are no longer sure which ones matter.',
     'do': 'List every step. Drop one and work without it for a day, then drop another the next day. Put back only a step whose absence breaks something you can name.'},
    {'field': 'Writing', 'id': 'DO-003',
     'situation': 'Every report keeps coming out the way the last one did.',
     'do': 'Take one decision you have already made, such as how it opens or the order it follows, and write five sentences of the version where it went the other way. Add one line on what the original was quietly assuming.'},
    {'field': 'Planning', 'id': 'DO-151',
     'situation': 'You are planning the year and every week is already spoken for.',
     'do': 'Leave one day each month unscheduled and unnamed, free for whoever wants it. Stop when the calendar is set, and do not fill those days in advance.'},
]

HTML = """
    <section id="onboard" aria-labelledby="onboard-title" hidden>
      <h1 id="onboard-title">How it works</h1>
      <p class="intro">Each operation is one small instruction you can try on whatever you are working on: a lesson, a meeting, a report, a plan. Here is one in use.</p>
      <article class="onb-card" aria-live="polite">
        <div class="onb-kicker" id="onb-kicker"></div>
        <p class="onb-situation" id="onb-situation"></p>
        <div class="onb-op">
          <div class="onb-sym" id="onb-sym" aria-hidden="true"></div>
          <div><span class="onb-label">One operation that fits</span><strong id="onb-name"></strong><span class="onb-def" id="onb-def"></span></div>
        </div>
        <div class="onb-do"><span class="onb-label">What you would do</span><p id="onb-do"></p></div>
        <button type="button" class="onb-open" id="onb-open">Read the whole operation →</button>
      </article>
      <div class="onb-actions">
        <button type="button" class="onb-next" id="onb-next">Show me another</button>
        <button type="button" class="onb-go" id="onb-go">Find one for my situation →</button>
      </div>
    </section>
"""

CSS = """
    #onboard h1 { margin-bottom:10px; }
    .onb-card { background:#fff; border:1px solid var(--line-strong); padding:28px 30px; margin:26px 0 18px; max-width:760px; }
    .onb-kicker { font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .onb-situation { font-size:26px; line-height:1.25; margin:10px 0 22px; }
    .onb-op { display:grid; grid-template-columns:120px minmax(0,1fr); gap:18px; align-items:center; padding:16px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
    .onb-sym { width:120px; height:90px; } .onb-sym svg { width:100%; height:100%; display:block; }
    .onb-op strong { display:block; font-size:24px; font-weight:400; margin:2px 0 4px; }
    .onb-def { display:block; color:var(--muted); font-size:16px; }
    .onb-label { display:block; font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .onb-do { margin-top:18px; } .onb-do p { margin:6px 0 0; font-size:18px; line-height:1.5; max-width:62ch; }
    .onb-open { width:auto; margin-top:18px; padding:6px 0; border:0; border-bottom:1px solid var(--line-strong); background:transparent; font-size:15px; }
    .onb-actions { display:flex; flex-wrap:wrap; gap:12px; max-width:760px; }
    .onb-actions button { width:auto; padding:14px 20px; font-size:16px; border:1px solid var(--line-strong); background:transparent; }
    .onb-actions .onb-go { background:var(--ink); color:var(--paper); border-color:var(--ink); }
    .onb-actions button:hover { background:var(--selected); color:var(--ink); }
    .how-open { width:auto; padding:4px 0; border:0; border-bottom:1px solid var(--line-strong); background:transparent; font-size:15px; margin-right:14px; }
    @media (max-width:640px) { .onb-card { padding:20px; } .onb-situation { font-size:21px; } .onb-op { grid-template-columns:80px minmax(0,1fr); } .onb-sym { width:80px; height:64px; } }
"""

JS = """
<script>
(function(){
  var EX = %s, i = 0;
  var on = document.querySelector('#onboard'), op = document.querySelector('#opening');
  function show(k){
    var e = EX[k], rec = contentById.get(e.id);
    document.querySelector('#onb-kicker').textContent = 'Example ' + (k+1) + ' of ' + EX.length + ' · ' + e.field;
    document.querySelector('#onb-situation').textContent = e.situation;
    document.querySelector('#onb-sym').innerHTML = rec ? (rec.locked.symbol || '') : '';
    document.querySelector('#onb-name').textContent = rec ? displayOperationName(rec.locked.name) : '';
    document.querySelector('#onb-def').textContent = rec ? rec.locked.canonicalDefinition : '';
    document.querySelector('#onb-do').textContent = e.do;
  }
  // 2026-10-11: hold the card's parts at the height of the longest example, so the box and the buttons stay still
  var PARTS = ['#onb-situation', '.onb-op', '.onb-do'];
  function fit(){
    if (on.hidden) return;
    var els = PARTS.map(function(sel){ return document.querySelector(sel); }).filter(Boolean), max = els.map(function(){ return 0; });
    els.forEach(function(el){ el.style.minHeight = ''; });
    for (var k = 0; k < EX.length; k++) { show(k); els.forEach(function(el, n){ max[n] = Math.max(max[n], el.getBoundingClientRect().height); }); }
    show(i);
    els.forEach(function(el, n){ el.style.minHeight = Math.ceil(max[n]) + 'px'; el.style.boxSizing = 'border-box'; });
  }
  var fitTimer; window.addEventListener('resize', function(){ clearTimeout(fitTimer); fitTimer = setTimeout(fit, 150); });
  try { document.fonts.ready.then(fit); } catch (err) {}
  function openOnboard(){
    document.querySelectorAll('#opening,#branch,#results,#boundary').forEach(function(el){ if (el) el.hidden = true; });
    on.hidden = false; show(i); fit();
  }
  function leave(){
    try { localStorage.setItem('do-onboarded', '1'); } catch (err) {}
    on.hidden = true; showOpening();
  }
  document.querySelector('#onb-next').addEventListener('click', function(){ i = (i + 1) %% EX.length; show(i); });
  document.querySelector('#onb-go').addEventListener('click', leave);
  document.querySelector('#onb-open').addEventListener('click', function(ev){ openOperationDetail(EX[i].id, 'results', ev.currentTarget); });
  var how = document.createElement('button'); how.type = 'button'; how.className = 'how-open'; how.textContent = 'How it works';
  window.__openOnboard = openOnboard;
  how.addEventListener('click', function(){ window.__openOnboard(); });
  var tools = document.querySelector('.header-tools'); tools.insertBefore(how, tools.firstChild);
  var seen = false; try { seen = localStorage.getItem('do-onboarded') === '1'; } catch (err) {}
  if (!seen) openOnboard();
})();
</script>
""" % json.dumps(EXAMPLES, ensure_ascii=False)
