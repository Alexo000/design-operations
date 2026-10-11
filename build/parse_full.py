"""Parser for the full printed edition. Same entry-finding rules as parse_compendium.py (project file),
but keeps every field in file order as a list of (label, value), so nothing is merged or lost."""
import re
LABELS = ["Definition", "Z/XY (proposed)", "Z", "XY", "Category", "Origin", "Cross-domain", "Description", "Example",
          "Design application", "Training exercise", "Visual reference", "Training", "Applications", "Contemporary",
          "Added rule", "Scale", "Move", "Family", "Nest", "Object", "Canonic example", "Task translation", "Formerly",
          "Key", "Status", "Provenance", "Evidence", "Contrast lines", "Where this comes from", "In the studio",
          "Try now — M", "Try now — V", "Try now — S", "Go deeper", "Image", "Compact", "Network", "Affinity", "Route"]
LAB_RE = re.compile(r'(?:(?<=\s)|^)(' + '|'.join(re.escape(x) for x in LABELS) + r')( \(Check B, [0-9\-]+\))?: ')
HEAD_NUM = re.compile(r'^(\d+)\. ([A-ZÉ][A-ZÉ \-\x27’]+?)(?:\s\s|\s*$| Definition| \[DO)')
HEAD_C = re.compile(r'^(C\d+)\. ([A-ZÉ][A-ZÉ \-\x27’]+?)\s*$')


def split_fields(text):
    out = []
    pos = [(m.start(), m.end(), m.group(1), m.group(2) or '') for m in LAB_RE.finditer(text)]
    pre = text[:pos[0][0]].strip() if pos else text.strip()
    if pre:
        out.append(('_pre', pre))
    for k, (s, e, lab, extra) in enumerate(pos):
        nxt = pos[k + 1][0] if k + 1 < len(pos) else len(text)
        val = text[e:nxt].strip()
        val = re.sub(r'\s*·\s*$', '', val).strip()
        out.append((lab + extra, val))
    return out


def parse(path):
    L = open(path, encoding='utf-8').read().split('\n')
    cand_at = next(i for i, l in enumerate(L) if l.strip() == 'CANDIDATES')
    heads = []
    for i, l in enumerate(L):
        if i < 345:      # the INDEX block at the top
            continue
        m = HEAD_NUM.match(l)
        if m:
            heads.append((i, int(m.group(1)), m.group(2).strip()))
        m = HEAD_C.match(l)
        if m:
            heads.append((i, m.group(1), m.group(2).strip()))
    ents = {}
    for k, (i, num, name) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(L)
        for j in range(i + 1, end):
            if re.match(r'^_{6,}\s*$', L[j]) or re.match(r'^[A-Z][A-Z ,&\-]{8,}$', L[j].strip()) or L[j].strip() == 'End of file.':
                end = j
                break
        block = '\n'.join(L[i:end])
        if 'Definition:' not in block:
            continue
        first = L[i]
        do = re.search(r'\[DO-(\d+)\]', first)
        formerly_p = re.search(r'\(formerly (P\d)\)', first)
        rest = re.sub(r'^(\d+|C\d+)\. [A-ZÉ][A-ZÉ \-\x27’]+?(\s\s|\s*$| (?=Definition)| \[DO-\d+\])', '', first, count=1).strip()
        rest = re.sub(r'^\(formerly P\d\)\s*', '', rest)
        rest = re.sub(r'^\[DO-\d+\]\s*(\(formerly P\d\))?\s*', '', rest)
        body = (rest + '\n' + '\n'.join(L[i + 1:end])).strip()
        body = re.sub(r'\s*\n\s*', ' ', body)
        assert num not in ents, num
        ents[num] = {'num': num, 'name': name, 'do': do.group(1) if do else None,
                     'formerly_p': formerly_p.group(1) if formerly_p else None,
                     'fields': split_fields(body), 'line': i, 'candidate': i > cand_at}
    return ents
