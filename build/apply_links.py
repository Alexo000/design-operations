"""apply_links.py — writes accepted links tranches into a Compendium cut (2026-10-17, rulings 1a and 2b).
NEW: entry name -> full Network line (replaces "Network: —"). ADD: (entry name, kind, target) appended to that kind.
Every touched line keeps its earlier stamps and gains STAMP."""
import re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from parse_full import parse

TRAIL = re.compile(r'((?:\s*\[[^\]]*\])+)\s*$')


def apply(src, out, new, add, stamp, dateline):
    E = parse(src)
    L = open(src).read().split('\n')
    line_of = {}
    for k, e in E.items():
        i = int(e['line'])
        for j in range(i - 1, i + 60):
            if L[j].startswith('Network:'):
                line_of[e['name']] = j
                break
    def split(l):
        body = l[len('Network:'):].strip()
        m = TRAIL.search(body)
        stamps = m.group(1).strip() if m else ''
        body = body[:m.start()].strip() if m else body
        return body, stamps
    for name, v in new.items():
        j = line_of[name]
        body, stamps = split(L[j])
        assert body in ('—', ''), (name, L[j])
        L[j] = 'Network: ' + v + (' ' + stamps if stamps else '') + ' ' + stamp
    for name, kind, target in add:
        j = line_of[name]
        body, stamps = split(L[j])
        parts = [] if body in ('—', '') else body.split(' · ')
        for i, p in enumerate(parts):
            if p.startswith(kind + ' → '):
                assert target not in p.split(' → ')[1].split(', '), (name, target)
                parts[i] = p + ', ' + target
                break
        else:
            parts.append(kind + ' → ' + target)
        st = stamps if stamp in stamps else ((stamps + ' ' if stamps else '') + stamp)
        L[j] = 'Network: ' + ' · '.join(parts) + ' ' + st
    i = next(i for i, l in enumerate(L) if l.startswith('AMENDED '))
    L[i:i] = [dateline, '']
    open(out, 'w').write('\n'.join(L))
