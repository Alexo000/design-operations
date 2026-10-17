"""build_explorer.py — the Design Operations explorer (symbols: set A for cards, E for lists, from the claude.ai artifact
"Design Operations Symbols", saved locally as symbols_page.html and extracted to symbols_AE.json; 153-155 drawn by
symbols_draw_153_155.py with symbols_dsl.py; task-card icons ☞ ✍ ⚙ ☛ from DejaVu Sans via glyphs.py)
 (public web edition, second form), 2026-10-10.
Takes the August public-beta shell (design_operations_public_beta.html: three ways in, routing, collection map,
operation cards) and its content register, and refills them from the current Compendium:
  - the main sequence only (144 operations); candidates out;
  - names, definitions, Compact lines, In the studio, Try now M/V/S, Task translations and Network from the Compendium;
  - the beta's hands / words / process tasks kept only for entries 1-70, which have no Try now lines in the Compendium;
  - routing profiles from the beta for entries up to 111 (keyed by DO number), and DRAFT profiles for 112-155,
    written 2026-10-10 from each entry's definition and family head (task scale marked Untested);
  - images kept where the beta had them (hosted on the current tool's Netlify site), captions show the credit only;
  - symbols, source links ("Go deeper") and the research-detail panels left out.
Usage: python3 build_explorer.py   (paths below; needs parse_full.py)"""
import re, json, html, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from parse_full import parse
import knowledge

SRC = os.environ.get('SRC', os.path.join(ROOT, 'sources', 'compendium_2026-10-17d.md'))
BETA = os.environ.get('BETA', os.path.join(ROOT, 'sources', 'design_operations_public_beta.html'))
REG = os.environ.get('REG', os.path.join(ROOT, 'sources', 'design_operations_content_register.json'))
OUT = os.environ.get('OUT', os.path.join(ROOT, 'site'))
os.makedirs(OUT, exist_ok=True)

E = parse(SRC)
page = open(BETA, encoding='utf-8').read()
reg = {r['number']: r for r in json.load(open(REG, encoding='utf-8'))['records']}
js_start = page.index('<script>') + len('<script>') if '<script>' in page else None
js = re.findall(r'<script[^>]*>(.*?)</script>', page, re.S)[0]
SYM = json.load(open(os.environ.get('SYMS', os.path.join(ROOT, 'sources', 'symbols_AE.json')), encoding='utf-8'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symbols_draw_153_155 import A as _A3, E as _E3
SYM_A = {int(k): v['A'] for k, v in SYM.items()}; SYM_E = {int(k): v['E'] for k, v in SYM.items()}
SYM_A.update(_A3); SYM_E.update(_E3)
SYM_FONT = re.search(r"@font-face\{font-family:Sym;src:url\((data:[^)]*)\)", open(os.environ.get('SYMPAGE', os.path.join(ROOT, 'sources', 'symbols_page.html')), encoding='utf-8').read()).group(1)
GLY = json.load(open(os.environ.get('GLYPHS', os.path.join(ROOT, 'sources', 'glyphs.json')), encoding='utf-8'))
ICONS = {'With your hands': GLY['0x261e'], 'In words': GLY['0x270d'], 'In the process': GLY['0x2699'], 'Try this': GLY['0x261b']}
old_rows = {int(r[0][3:]): r for r in json.loads(re.search(r'const operationRows = (\[.*?\]);\n', js, re.S).group(1))}

STAMP = re.compile(r'\s*\[(?:\d{4}-\d{2}-\d{2}|S\])[^\]]*\]')


def clean(v):
    v = STAMP.sub('', (v or '').strip())
    v = re.sub(r'\s*\[S\]', '', v).strip()
    v = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'\1', v)   # drop markdown italics in plain text
    return '' if re.fullmatch(r'[—\-\s]*', v) else v


# Draft routing profiles for the entries added after the beta (2026-10-10, desk work, unratified).
# conditions, primary, secondary, time, predictability, starting state, social, loss, exposure
U = 'Untested'
DRAFT = {
 112: ('STUCKNESS · NARROWNESS · AMBIGUITY', 'TRANSFORM', 'REVEAL', 'Strong T1-2; Works T3', 'Medium - what the excess shows', 'existing', 'either', 'no destruction', 'private-compatible'),
 113: ('STUCKNESS · REPETITION · BLANKNESS', 'REFRAME', 'COMBINE', 'Strong T1-2; Works T3', 'Medium - context supplies the transformation', 'existing', 'either', 'no destruction', 'private-compatible'),
 114: ('MISALIGNMENT · CAPABILITY', 'REPEAT', 'TEST', 'Strong T2-3; Works T1', 'Medium - whether it passes', 'existing', 'either', 'no destruction', 'private-compatible'),
 115: ('UNCERTAINTY · ATTACHMENT · STUCKNESS', 'TRANSFER', 'OPEN', 'Strong T3-5; Works T2', 'Low - chance/system/other decides', 'either', 'either', 'no destruction', 'private-compatible'),
 116: ('OVERLOAD · STUCKNESS · DRIFT', 'PRESERVE', 'DIVERGE', 'Strong T1-2; Works T3', 'Medium - variation around the fixed part', 'existing', 'either', 'no destruction', 'private-compatible'),
 117: ('ATTACHMENT · FINISHING · DRIFT', 'ADAPT', 'RECOVER', 'Strong T2-3; Works T1', 'Medium - what changes once reopened', 'existing', 'either', 'reversible loss', 'private-compatible'),
 118: ('DEPENDENCY · COORDINATION · TRANSITION', 'TRANSFER', 'FINISH', 'Strong T3-4; Works T2', 'Medium - whether it is renewed', 'either', 'with others', 'no destruction', 'observable'),
 119: ('STUCKNESS · CONFLICT · NARROWNESS', 'TEST', 'REFRAME', 'Strong T1-2; Works T3', 'Medium - what the loophole exposes', 'existing', 'either', 'no destruction', 'private-compatible'),
 120: ('OVERLOAD · DEPENDENCY', 'REDUCE', 'CLARIFY', 'Strong T1-2; Works T3', 'Medium - what the surroundings already carry', 'existing', 'either', 'reversible loss', 'private-compatible'),
 121: ('STUCKNESS · REPETITION · TRANSITION', 'REFRAME', 'TRANSFORM', 'Strong T1-2', 'Low - chance/system/other decides', 'either', 'either', 'no destruction', 'private-compatible'),
 122: ('BLANKNESS · UNCERTAINTY · ATTACHMENT', 'TRANSFER', 'OPEN', 'Strong T3-5; Works T2', 'Low - chance/system/other decides', 'either', 'either', 'no destruction', 'observable'),
 123: ('REPETITION · STUCKNESS · BLANKNESS', 'ADAPT', 'DIVERGE', 'Strong T3-4; Works T2', 'Low - chance/system/other decides', 'either', 'with others', 'no destruction', 'private-compatible'),
 124: ('COORDINATION · OVERLOAD', 'DISTRIBUTE', 'ORDER', 'Strong T2-3; Works T1', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 125: ('ATTACHMENT · REPETITION · STUCKNESS', 'HIDE', 'COMBINE', 'Strong T1-2; Works T3', 'Low - chance/system/other decides', 'either', 'with others', 'no destruction', 'private-compatible'),
 126: ('OVERLOAD · COORDINATION · ATTENTION', 'CONSTRAIN', 'ORDER', 'Strong T2-3; Works T1', 'Medium - what queues at the opening', 'existing', 'either', 'no destruction', 'private-compatible'),
 127: ('FRAGILITY · ATTACHMENT · DRIFT', 'PRESERVE', 'TEST', 'Strong T2-3; Works T1', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 128: ('FRAGILITY · CAPABILITY · TRANSITION', 'TEST', 'REDUCE', 'Strong T2-3; Works T1', 'Medium - whether it stands alone', 'either', 'either', 'reversible loss', 'private-compatible'),
 129: ('STUCKNESS · CONFLICT · NARROWNESS', 'CONSTRAIN', 'OPEN', 'Strong T1-2; Works T3', 'Medium - where the price gets paid', 'either', 'either', 'reversible loss', 'private-compatible'),
 130: ('OVERLOAD · DEPENDENCY · COORDINATION', 'COORDINATE', 'REDUCE', 'Strong T3-4; Works T2', 'Medium - what gets taken', 'existing', 'with others', 'no destruction', 'observable'),
 131: ('AMBIGUITY · OVERLOAD · FAILURE', 'TEST', 'CLARIFY', 'Strong T1-2', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 132: ('AMBIGUITY · MISALIGNMENT · OVERLOAD', 'COMBINE', 'REVEAL', 'Strong T1-2; Works T3', 'Medium - what the overlap shows', 'existing', 'either', 'no destruction', 'private-compatible'),
 133: ('ATTACHMENT · FINISHING', 'HIDE', 'FINISH', 'Strong T3-5; Works T2', 'Medium - how it reads when it arrives', 'existing', 'with others', 'no destruction', 'private-compatible'),
 134: ('BLANKNESS · STUCKNESS', 'REPEAT', 'TRANSFORM', 'Strong T1-2; Works T3', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 135: ('STUCKNESS · BLANKNESS · ATTACHMENT', 'COMBINE', 'TRANSFORM', 'Strong T1-2', 'Low - chance/system/other decides', 'existing', 'either', 'no destruction', 'private-compatible'),
 136: ('AMBIGUITY · CONFLICT · UNCERTAINTY', 'OPEN', 'PRESERVE', 'Strong T1-2; Works T3', 'Medium - what holding both shows', 'either', 'either', 'no destruction', 'private-compatible'),
 137: ('NARROWNESS · CONFLICT · AMBIGUITY', 'TEST', 'REVEAL', 'Strong T1-2; Works T3', 'Medium - where the premise leads', 'existing', 'either', 'no destruction', 'private-compatible'),
 138: ('ATTACHMENT · FRAGILITY · FINISHING', 'CONSTRAIN', 'FINISH', 'Strong T1-2; Works T3', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 139: ('OVERLOAD · MISALIGNMENT · BLANKNESS', 'ORDER', 'PRESERVE', 'Strong T1-2; Works T3', 'High', 'either', 'either', 'no destruction', 'private-compatible'),
 140: ('OVERLOAD · ORDERING · ATTENTION', 'ORDER', 'CLARIFY', 'Strong T1-2; Works T3', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 141: ('MISALIGNMENT · BLANKNESS · COORDINATION', 'CONSTRAIN', 'CONVERGE', 'Strong T1-2; Works T3', 'High', 'either', 'either', 'no destruction', 'private-compatible'),
 142: ('STUCKNESS · REPETITION · ATTACHMENT', 'TRANSFORM', 'PRESERVE', 'Strong T1-2', 'Medium - what the new part does in the old place', 'existing', 'either', 'no destruction', 'private-compatible'),
 143: ('REPETITION · DRIFT · BLANKNESS', 'REPEAT', 'ORDER', 'Strong T1-2; Works T3', 'High', 'either', 'either', 'no destruction', 'private-compatible'),
 144: ('STUCKNESS · NARROWNESS', 'TRANSFORM', 'PRESERVE', 'Strong T1-2; Works T3', 'Medium - what changes with size', 'existing', 'either', 'no destruction', 'private-compatible'),
 145: ('DEPENDENCY · COORDINATION · STUCKNESS', 'COMBINE', 'COORDINATE', 'Strong T1-2; Works T3', 'Low - chance/system/other decides', 'either', 'either', 'no destruction', 'private-compatible'),
 146: ('CONFLICT · MISALIGNMENT · ATTACHMENT', 'CONVERGE', 'COMBINE', 'Strong T2-3; Works T1', 'Medium - what the blend becomes', 'existing', 'either', 'no destruction', 'private-compatible'),
 147: ('OVERLOAD · CONFLICT · DEPENDENCY', 'COMBINE', 'SEPARATE', 'Strong T1-2; Works T3', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 148: ('TRANSITION · FRAGILITY · STUCKNESS', 'ADAPT', 'TRANSFORM', 'Strong T3-4; Works T2', 'Medium - where the steps lead', 'existing', 'either', 'no destruction', 'private-compatible'),
 149: ('OVERLOAD · ATTACHMENT · MEMORY', 'REDUCE', 'PRESERVE', 'Strong T1-2', 'High', 'existing', 'either', 'reversible loss', 'observable'),
 150: ('AMBIGUITY · ORDERING · CONFLICT', 'REFRAME', 'CLARIFY', 'Strong T1-2; Works T3', 'Medium - where things fall', 'existing', 'either', 'no destruction', 'private-compatible'),
 151: ('OVERLOAD · FRAGILITY · UNCERTAINTY', 'PRESERVE', 'OPEN', 'Strong T1-2; Works T3', 'High', 'either', 'either', 'no destruction', 'private-compatible'),
 152: ('OVERLOAD · AMBIGUITY · CONFLICT', 'REDUCE', 'CLARIFY', 'Strong T1-2', 'High', 'existing', 'either', 'no destruction', 'private-compatible'),
 153: ('REPETITION · DEPENDENCY · STUCKNESS', 'SEPARATE', 'TEST', 'Strong T1-2; Works T3', 'Medium - what holds without each part', 'existing', 'either', 'no destruction', 'private-compatible'),
 154: ('STUCKNESS · REPETITION · ATTACHMENT', 'REFRAME', 'DIVERGE', 'Strong T1-2', 'Medium - what the premise changes', 'either', 'either', 'no destruction', 'private-compatible'),
 155: ('MEMORY · AMBIGUITY · BLANKNESS', 'RECOVER', 'REVEAL', 'Strong T1-2; Works T3', 'Medium - what memory keeps', 'either', 'either', 'no destruction', 'private-compatible'),
}

main = sorted(k for k, e in E.items() if not e['candidate'] and isinstance(k, int))
assert len(main) == 144
names = {k: E[k]['name'] for k in main}
by_name = {v: k for k, v in names.items()}

records, rows, content, tasks, report = [], [], {}, {}, []
for idx, k in enumerate(main, 1):
    f = {l: clean(v) for l, v in E[k]['fields']}
    did = f'DO-{k:03d}'
    if k in old_rows:
        r = list(old_rows[k]); r[1] = names[k]
    else:
        d = DRAFT[k]
        r = [did, names[k], d[0], d[1], d[2], U, d[3], d[4], d[5], d[6], d[7], d[8]]
    rows.append(r)
    # Compact
    act = ex = ''
    if f.get('Compact'):
        m = re.match(r'⟶\s*(.*?)\s*·\s*✓\s*(.*)$', f['Compact'])
        act, ex = (m.group(1), m.group(2)) if m else (f['Compact'].lstrip('⟶ '), '')
    # tasks
    apps = {}
    if f.get('Try now — M') or f.get('Try now — V') or f.get('Try now — S'):
        for key, lab in (('hands', 'Try now — M'), ('words', 'Try now — V'), ('process', 'Try now — S')):
            if f.get(lab):
                apps[key] = {'task': f[lab]}
        src = 'compendium'
    elif k in reg and reg[k]['editorial'].get('applications'):
        for key in ('hands', 'words', 'process'):
            t = (reg[k]['editorial']['applications'].get(key) or {}).get('task')
            if t:
                apps[key] = {'task': t}
        src = 'beta (published 70)'
    if not apps:
        apps['general'] = {'task': f.get('Task translation', '')}
        src = 'task translation'
    # related
    rel = {'continueTo': [], 'alternative': [], 'pairs': [], 'escalation': []}
    keymap = {'Next': 'continueTo', 'Alternative': 'alternative', 'Pairs with': 'pairs', 'Escalation': 'escalation'}
    for part in re.split(r'\s+·\s+', f.get('Network', '')):
        m = re.match(r'(Next|Alternative|Pairs with|Escalation)\s*→\s*(.*)', part.strip())
        if m:
            for nm in m.group(2).split(','):
                nm = re.sub(r'\s*\(.*?\)', '', nm).strip()
                if nm in by_name:
                    rel[keymap[m.group(1)]].append(nm)
    # image
    assets = []  # images retired 2026-10-11: the site that hosted them is gone
    if False:
        for a in (reg[k]['editorial'].get('image') or {}).get('assets', []):
            if a.get('url'):
                credit = a.get('credit') or ''
                if credit.lower() in ('unidentified', 'unknown', ''):
                    credit = ''
                assets.append({'url': a['url'], 'credit': credit, 'alt': ''})
                break
    _seen = knowledge.seen_in(f.get('Canonic example', ''))   # 'Seen in' line (ruling 1a, 2026-10-11)
    rec = {'id': did, 'number': k, 'index': idx,
           'locked': {'name': names[k], 'symbol': SYM_A.get(k, ''), 'canonicalDefinition': act or f['Definition'],
                      'profile': {'primaryMovement': r[3], 'time': r[6], 'startingState': r[8]}},
           'editorial': {'compact': {'act': act, 'ex': ex}, 'formerly': f.get('Formerly', ''), 'seenIn': _seen,
                         'applications': apps,
                         'context': {'anecdotes': [f['In the studio']] if f.get('In the studio') else [], 'sources': []},
                         'image': {'assets': assets}, 'related': rel}}
    records.append(rec)
    # 2026-10-11: the Compact action line is the public line under each name (THE SINGLE CORPUS lists Compact, not Definition)
    search = ' '.join([f.get('Formerly', ''), act, ex, _seen['plain'] if _seen else '']).lower()
    content[did] = {'instruction': act or f['Definition'], 'symbol': SYM_E.get(k, ''), 'search': search}
    _first = next((apps[k2]['task'] for k2 in ('hands', 'words', 'process', 'general') if apps.get(k2, {}).get('task')), '')
    tasks[did] = _first or f.get('Task translation', '')
    report.append((k, names[k], 'draft profile' if k not in old_rows else 'beta profile', src, 'image' if assets else ''))

register = {'schemaVersion': 'explorer-2026-10-10', 'title': 'Design Operations', 'records': records}   # title renamed on the page by standalone.py

# ---------------------------------------------------------------- splice the data into the beta script
def splice(src, start_pat, end_pat, new):
    i = src.index(start_pat)
    j = src.index(end_pat, i) + len(end_pat)
    return src[:i] + new + src[j:]

njs = js
njs = splice(njs, 'const CONTENT_REGISTER = ', ';\n    const contentRecords', 'const CONTENT_REGISTER = ' + json.dumps(register, ensure_ascii=False) + ';\n    const contentRecords')
njs = splice(njs, 'const operationRows = ', '];\n', 'const operationRows = ' + json.dumps(rows, ensure_ascii=False) + ';\n')
njs = splice(njs, 'const operationContent = ', '};\n', 'const operationContent = ' + json.dumps(content, ensure_ascii=False) + ';\n')
njs = splice(njs, 'const operationTasks = {', '\n    };', 'const operationTasks = ' + json.dumps(tasks, ensure_ascii=False) + ';')


def rep(src, a, b, label):
    assert src.count(a) == 1, (label, src.count(a))
    return src.replace(a, b)

# relation groups: add "pair with", rename labels
njs = rep(njs, """        ['Continue', related.continueTo || []],
        ['Try instead', related.alternative || []],
        ['Escalation', related.escalation || []]""",
          """        ['If this lands, continue to', related.continueTo || []],
        ['If it doesn’t fit, try instead', related.alternative || []],
        ['Works as a pair with', related.pairs || []],
        ['To go further', related.escalation || []]""", 'relations')
# detail card
njs = rep(njs, """      const image = asset ? '<figure class="operation-media"><img loading="lazy" src="'+escapeContent(asset.url)+'" alt="'+escapeContent(asset.alt || asset.credit || record.locked.name)+'"><figcaption>'+escapeContent(asset.credit || asset.file || '')+(asset.status ? ' · '+escapeContent(asset.status) : '')+'</figcaption></figure>' : '';""",
          """      const image = asset ? '<figure class="operation-media"><img loading="lazy" src="'+escapeContent(asset.url)+'" alt=""><figcaption>'+escapeContent(asset.credit || '')+'</figcaption></figure>' : '';
      const compact = editorial.compact && editorial.compact.ex ? '<div class="operation-compact"><p class="ex"><span aria-hidden="true">✓</span> '+escapeContent(editorial.compact.ex)+'</p></div>' : '';
      const formerly = editorial.formerly ? '<p class="operation-formerly">Formerly '+escapeContent(displayOperationName(editorial.formerly))+'</p>' : '';""", 'image')
njs = rep(njs, """<p class="operation-definition">'+escapeContent(record.locked.canonicalDefinition)+'</p></div><div class="operation-symbol" aria-hidden="true">'+escapeContent(record.locked.symbol)+'</div></header>'+""",
          """<p class="operation-definition">'+escapeContent(record.locked.canonicalDefinition)+'</p>'+formerly+'</div><div class="operation-symbol" aria-hidden="true">'+(record.locked.symbol || '')+'</div></header>'+compact+""", 'hero')
njs = rep(njs, """        '<section class="operation-section"><h3>How it has been used</h3><div class="operation-context"><div>'+anecdotes+'</div><div><h4>Go deeper</h4><ul class="operation-sources">'+sources+'</ul></div></div></section>'+""",
          """        (anecdotes ? '<section class="operation-section"><h3>How it has been used</h3><div class="operation-context one"><div>'+anecdotes+'</div></div></section>' : '')+""", 'context')
njs = rep(njs, """applicationBlock('Try this', applications.general);""", """applicationBlock('Try this', applications.general);
      const taskCount = ['hands','words','process','general'].filter(key => applications[key] && applications[key].task).length;""", 'taskcount')
njs = rep(njs, """'<section class="operation-section"><h3>Try it on your work</h3><div class="operation-applications">'+tasks+'</div></section>'+""",
          """'<section class="operation-section"><h3>Try it on your work</h3><div class="operation-applications'+(taskCount === 1 ? ' single' : '')+'">'+tasks+'</div></section>'+""", 'apps')
njs = rep(njs, """record.id+' · '+record.number+' of '+contentRecords.length;""", """record.id+' · '+record.index+' of '+contentRecords.length;""", 'position')
# map search: include former names, definitions and Compact lines
njs = rep(njs, "const searchable = `${operation.id} ${operation.name} ${operation.primary}`.toLocaleLowerCase();",
          "const searchable = `${operation.id} ${operation.name} ${operation.primary} ${movementMeanings[operation.primary] || ''} ${operationContent[operation.id]?.search || ''}`.toLocaleLowerCase();", 'search')
njs = njs.replace('the unchanged 111-operation collection', 'the collection')
import nav
njs = nav.patch_js(njs, rep)
njs = rep(njs, "      if (!record) return;\n", "      if (!record) return;\n      if (window.__markSeen) window.__markSeen(id);\n", 'seen hook')
njs = rep(njs, "button.setAttribute('aria-label', `${displayOperationName(operation.name)}, ${operation.id}`);", "button.setAttribute('aria-label', `${displayOperationName(operation.name)}, ${operation.id}`); button.dataset.id = operation.id;", 'map id')
njs = rep(njs, "      const grid = document.querySelector('#map-grid');", "      setTimeout(() => window.__markMap && window.__markMap(), 0);\n      const grid = document.querySelector('#map-grid');", 'map mark')
njs = rep(njs, "function showOpening() {\n      currentRoute = null;", "function showOpening() {\n      document.querySelector('#onboard').hidden = true;\n      currentRoute = null;", 'showOpening hides onboard')
njs = rep(njs, "return '<section class=\"operation-application\"><span class=\"operation-format\">'+escapeContent(label)+'</span>'+",
          "return '<section class=\"operation-application\"><span class=\"operation-format\"><span class=\"op-icon\" aria-hidden=\"true\">'+(TASK_ICONS[label] || '')+'</span>'+escapeContent(label)+'</span>'+", 'task icon')
njs = rep(njs, "function applicationBlock(label, application) {", "const TASK_ICONS = " + json.dumps(ICONS, ensure_ascii=False) + ";\n    function applicationBlock(label, application) {", 'icons const')
njs = rep(njs, "'</span><strong>'+escapeContent(displayOperationName(item.name))+'</strong></button>'",
          "'</span><strong>'+escapeContent(displayOperationName(item.name))+'</strong><i class=\"related-symbol\" aria-hidden=\"true\">'+(operationContent[item.id]?.symbol || '')+'</i></button>'", 'related symbol')
njs = rep(njs, "symbol.textContent = operationContent[operation.id]?.symbol || '';", "symbol.innerHTML = operationContent[operation.id]?.symbol || '';", 'map symbol')
njs = rep(njs, "function symbolLengthClass(symbol = '') {", "function symbolLengthClass(symbol = '') {\n      if (String(symbol).startsWith('<svg')) return '';", 'symbol class')

npage = page.replace(js, njs)
npage = rep(npage, '<div class="count">111 operations<br>routing prototype</div>', '<div class="count">144 operations</div>', 'count')
from seen import TALLY_HTML, STRIP_HTML, OPENING_MAP, CSS as SEEN_CSS, JS as SEEN_JS
npage = rep(npage, '<div class="count">144 operations</div>', TALLY_HTML, 'tally')
npage = rep(npage, '      </div>\n    </header>\n', '      </div>\n    </header>\n' + STRIP_HTML + '\n', 'strip')
npage = rep(npage, '<span><strong>I’m just looking around</strong><small>Open a drawer in the collection.</small></span><span class="arrow" aria-hidden="true">→</span>\n        </button>\n', '<span><strong>I’m just looking around</strong><small>Open a drawer in the collection.</small></span><span class="arrow" aria-hidden="true">→</span>\n        </button>\n' + OPENING_MAP, 'opening map')
npage = rep(npage, 'Browse all 111 operations by the kind of movement they make.', 'Browse all 144 operations by the kind of movement they make, or search by name, former name or word.', 'map intro')
npage = rep(npage, '<title>Design Operations — Public beta</title>', '<title>Design Operations</title>', 'title')
npage = re.sub(r'<details>\s*<summary>Research details</summary>', '<details hidden><summary>Research details</summary>', npage)
assert npage.count('<details hidden><summary>Research details</summary>') == 2
CSS_ADD = """
    .operation-compact { margin:0; padding:18px 0; border-bottom:1px solid var(--line-strong); }
    .operation-compact p { margin:0; font-size:20px; line-height:1.35; }
    .operation-compact p.ex { margin-top:6px; color:var(--muted); font-size:17px; }
    .operation-compact span { display:inline-block; width:1.4em; }
    .operation-formerly { margin:10px 0 0; color:var(--muted); font-size:14px; }
    .operation-context.one { display:block; max-width:760px; }
    .operation-applications.single { grid-template-columns:1fr; max-width:760px; }
    @font-face { font-family:Sym; src:url(SYMFONT); }
    .operation-hero { grid-template-columns:minmax(0,1fr) 210px; }
    .operation-symbol { min-width:0; width:210px; height:170px; padding-top:6px; }
    .operation-symbol svg { width:100%; height:100%; display:block; }
    .map-symbol { width:72px; height:26px; flex:none; }
    .map-symbol svg { width:100%; height:100%; display:block; }
    .map-detail-symbol { width:150px; height:64px; }
    .map-detail-symbol svg { width:100%; height:100%; display:block; }
    .result-symbol { width:110px; height:52px; flex:none; }
    .result-symbol svg { width:100%; height:100%; display:block; }
    .operation-application { background:#fff; }
    .operation-format { display:flex; align-items:center; gap:10px; }
    .op-icon { display:inline-block; width:30px; height:24px; flex:none; color:var(--ink); }
    .op-icon svg { width:100%; height:100%; display:block; }
    .operation-related button { background:#fff; display:grid; grid-template-columns:minmax(0,1fr) 72px; column-gap:12px; align-items:center; }
    .operation-related button > span, .operation-related button > strong { grid-column:1; }
    .related-symbol { grid-column:2; grid-row:1 / span 2; width:72px; height:44px; display:block; font-style:normal; color:var(--ink); }
    .related-symbol svg { width:100%; height:100%; display:block; }
    .operation-related button:hover { background:var(--selected); }
    @media (max-width:640px) { .operation-hero { grid-template-columns:minmax(0,1fr); } .operation-symbol { width:160px; height:120px; padding-top:14px; } }
    .explorer-foot { max-width:820px; margin:56px auto 32px; padding:16px 18px 0; border-top:1px solid var(--line); color:var(--muted); font-size:14px; line-height:1.5; }
    .explorer-foot p { margin:0 0 8px; }
  </style>"""
npage = npage.replace('</style>', CSS_ADD.replace('SYMFONT', SYM_FONT), 1)
FOOT = """<footer class="explorer-foot"><p>The symbols are a first set and will change.</p><p>Built from the Compendium of 17 October 2026 · © 2026 Alejandro Ramos Saavedra</p></footer>"""
npage = npage.replace('<script>', FOOT + '\n<script>', 1)
from onboarding import HTML as ONB_HTML, CSS as ONB_CSS, JS as ONB_JS
npage = rep(npage, '    <section id="opening" aria-labelledby="opening-title">', ONB_HTML + '    <section id="opening" aria-labelledby="opening-title">', 'onboard html')
npage = npage.replace('</style>', ONB_CSS + '  </style>', 1)
assert npage.count('</body>') == 1
import polish
import discover
npage = rep(npage, OPENING_MAP + '      </div>\n    </section>\n', OPENING_MAP + '      </div>\n' + discover.FIELD_HTML + '    </section>\n', 'field')
import pictograms
import dialogue
import trail   # trail at the top of each card (2026-10-17, preview)
import netmap   # Connections map (2026-10-17, preview)
NET, NET_STATS = netmap.build(E, main, records)
print('connections', NET_STATS)
npage = npage.replace('</body>', ONB_JS + SEEN_JS + discover.JS + pictograms.js() + knowledge.JS + dialogue.JS + trail.JS + netmap.js(NET) + polish.JS + nav.JS + '</body>')
npage = nav.patch_html(npage, rep)
import standalone
import wordmark   # the name with a symbol over each letter, drawn again on every visit (2026-10-15)
npage = standalone.patch_html(npage, rep, wordmark.write_assets(OUT, records, {d: c['symbol'] for d, c in content.items()}))   # small set E (2026-10-17)
standalone.copy_share(ROOT, OUT)
npage = polish.patch_html(npage)
npage = dialogue.patch_html(npage, rep)
npage = rep(npage, '<button class="map-open" id="open-map" type="button">Collection map</button>', '<button class="map-open" id="open-map" type="button">Collection map</button>' + netmap.BUTTON, 'connections button')
npage = rep(npage, '  <dialog id="collection-map"', netmap.HTML + '  <dialog id="collection-map"', 'connections dialog')
npage = npage.replace('</style>', SEEN_CSS + discover.CSS + pictograms.CSS + knowledge.CSS + trail.CSS + netmap.CSS + '  </style>', 1)
npage = rep(npage, '<button type="button" class="onb-go" id="onb-go">Find one for my situation →</button>', '<button type="button" class="onb-go" id="onb-go">Find one for my situation →</button>\n        <button type="button" class="onb-next" id="onb-map">Browse all 144</button>', 'onb map')
import stuck   # 'I'm stuck on a project' way in (2026-10-13)
npage = stuck.patch_page(npage)
import palette   # cool grey paper (2026-10-17)
npage = palette.apply(npage)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(npage)
assert 'Design Operations' not in npage, 'the old name is still on the page'
import pages   # one page per operation, /all/, sitemap.xml, robots.txt (2026-10-15)
print('operation pages', pages.write(OUT, register, ICONS, npage))
with open(os.path.join(HERE, 'build_report.tsv'), 'w', encoding='utf-8') as fh:
    fh.write('number\tname\tprofile\ttasks from\timage\n')
    for r in report:
        fh.write('\t'.join(map(str, r)) + '\n')
print('records', len(records), 'bytes', len(npage),
      'draft profiles', sum(1 for r in report if r[2] == 'draft profile'),
      'images', sum(1 for r in report if r[4]))
