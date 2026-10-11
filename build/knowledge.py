"""knowledge.py — "Seen in" on every card (2026-10-11, work lane, ruling 1a; display rule amended 2026-10-11b).
Each operation's Canonic example line (one real work of art or design where the move is used) is shown as one line,
"Seen in: maker, title, date", linked to its source. The line is cut at the first colon, semicolon or sentence end,
so only maker, title and date show; the detail stays in the Compendium. Reading lists (Go deeper) are not shown."""
import re, html

URL = re.compile(r'https?://[^\s\]]+')
STAMP = re.compile(r'\s*\[(?:\d{4}-\d{2}-\d{2}|S\])[^\]]*\]')


def seen_in(canonic):
    """Return {'html': ..., 'url': ..., 'plain': ...} from a Canonic example line, or None."""
    c = STAMP.sub('', canonic or '').strip()
    if not c:
        return None
    m = URL.search(c)
    url = m.group(0) if m else ''
    url = url.rstrip('.,;')
    while url.endswith(')') and url.count(')') > url.count('('):   # keep Wikipedia's (film) etc.
        url = url[:-1]
    head = c.split(': ', 1)[0]
    head = head.split('; ', 1)[0]
    # cut at a sentence end that is not an initial ("E. W.") or a numbered edition
    cut = re.search(r'(?<![A-Z])(?<!\b[A-Z][a-z])\.\s+(?=[A-Z])', head)
    if cut:
        head = head[:cut.start()]
    head = head.strip().rstrip('.,')
    if len(head) > 90:
        # long: keep maker, title and year, drop the middle
        t = re.search(r'\*[^*]+\*', head)
        if t:
            y = re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b', head[t.end():])
            short = head[:t.start()].rstrip(' ,') + ', ' + t.group(0) + (', ' + y.group(0) if y else '')
            if len(short) < len(head):
                head = short.lstrip(', ')
        else:
            y = re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b', head)
            if y and y.end() < len(head):
                head = head[:y.end()]
    if len(head) > 100:
        t = re.search(r'\*([^*]+)\*', head)
        if t and ' (' in t.group(1):                      # long bracketed title: keep the part before the bracket
            head = head[:t.start()] + '*' + t.group(1).split(' (', 1)[0] + '*' + head[t.end():]
    if len(head) > 100:
        t = re.search(r'\*', head)
        maker = head[:t.start()] if t else ''
        if maker.count(', ') >= 3:                         # many makers: first name and others
            head = maker.split(', ', 1)[0] + ' and others, ' + head[t.start():]
    if len(head) > 120:
        head = head[:117].rsplit(' ', 1)[0].rstrip(',;')
        if head.count('*') % 2:
            head += '*'
        head += '…'
    if head.count('(') > head.count(')') and not head.endswith('…'):
        head += ')'
    plain = re.sub(r'\*([^*]+)\*', r'\1', head)
    out = html.escape(head, quote=False)
    out = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', out)
    return {'html': out, 'url': url, 'plain': plain}


CSS = """
    /* knowledge 2026-10-11 */
    .seen-in { display:flex; flex-wrap:wrap; gap:4px 10px; align-items:baseline; margin:18px 0 0; font-size:16px; line-height:1.45; }
    .seen-in .si-label { font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    .seen-in a { color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line-strong); }
    .seen-in a:hover { border-bottom-color:var(--ink); }
    .seen-in a .si-arrow { font-size:.9em; margin-left:4px; }
"""

JS = r"""
<script>
(function(){
  // "Seen in": the real work behind each operation, under "How it has been used"
  var orig = renderOperationDetail;
  renderOperationDetail = function(id){
    var out = orig.apply(this, arguments);
    var box = document.querySelector('#operation-detail-content'); if (!box) return out;
    var r = contentById.get(id), s = r && r.editorial && r.editorial.seenIn; if (!s) return out;
    var old = box.querySelector('.seen-in'); if (old) old.remove();
    var p = document.createElement('p'); p.className = 'seen-in';
    var l = document.createElement('span'); l.className = 'si-label'; l.textContent = 'Seen in';
    var a = document.createElement(s.url ? 'a' : 'span');
    if (s.url) { a.href = s.url; a.target = '_blank'; a.rel = 'noopener'; }
    a.innerHTML = s.html + (s.url ? '<span class="si-arrow" aria-hidden="true">↗</span>' : '');
    p.appendChild(l); p.appendChild(a);
    var heads = Array.prototype.filter.call(box.querySelectorAll('h2, h3'), function(h){ return /How it has been used/i.test(h.textContent); });
    var sec = heads.length ? heads[0].closest('section') || heads[0].parentElement : null;
    if (sec) sec.appendChild(p);
    else { var c = box.querySelector('.operation-compact'); if (c) c.appendChild(p); else box.appendChild(p); }
    return out;
  };
})();
</script>
"""
