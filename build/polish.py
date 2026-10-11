"""polish.py — graphic-design pass of 2026-10-11 (work lane).
Fixes found in a review of every screen at desktop and phone sizes:
  - one left edge: footer and onboarding card line up with the main column; the card's bar lines up with its content;
  - header items sit on one line and one centre; the brand reads as a name, not a caption;
  - the only colour on the page was a stray blue (focus ring, 'None of these' box): now ink and a dashed outline,
    the same language as 'Browse the whole collection';
  - the 'seen' strip is one hairline row of 144 marks instead of a two-row dashed band (set in seen.py);
  - phone: header no longer wraps 'How it works'; onboarding buttons stack at full width;
  - opening a card no longer lights up the Close button;
  - names keep small words lower case ('Clear and Refill');
  - collection map: groups stack in two columns by their own height, so short groups no longer sit in tall empty boxes.
The typeface is set in FONT_CSS (and loaded in nav.py) so it can be swapped in one place.
Also 2026-10-11: the card shows the Compact action line under the name in place of the Definition (set in build_explorer.py)."""

# Typeface: IBM Plex Sans (ruling 1b, 2026-10-11), loaded in nav.py. Was Atkinson Hyperlegible.
FONT_CSS = """
    body, button, input, select, textarea { font-family:'IBM Plex Sans', Arial, sans-serif; }
    .operation-compact p.ex { margin-top:0; }
"""

CSS = """
    /* polish 2026-10-11 */
    :root { --focus:#161616; }
    :focus-visible { outline:2px solid var(--ink); outline-offset:3px; }
    header { align-items:center; }
    .header-tools { align-items:center; gap:18px; }
    .brand { font-size:16px; font-weight:700; letter-spacing:0; }
    .how-open { margin-right:0; font-size:15px; white-space:nowrap; }
    .explorer-foot { width:calc(100% - 36px); max-width:820px; padding:16px 0 0; box-sizing:border-box; }
    .onb-card, .onb-actions { max-width:none; }
    .option.utility, .utility-action { background:transparent; color:var(--ink); border-color:var(--line-strong); border-style:dashed; }
    .utility:hover, .utility-action:hover { background:var(--hover); color:var(--ink); border-color:var(--ink); }
    .utility[aria-pressed="true"] { background:var(--selected); color:var(--ink); border-color:var(--ink); }
    .operation-dialog-bar { padding:12px 38px; }
    #operation-dialog-position { text-align:left; }
    .map-grid { display:block; columns:2 340px; column-gap:14px; }
    .map-group { break-inside:avoid; margin:0 0 14px; }
    .map-search:focus-visible { outline:none; border-color:var(--ink); box-shadow:inset 0 0 0 1px var(--ink); }
    @media (max-width:640px) {
      header { align-items:flex-start; }
      .header-tools { gap:12px; }
      .operation-dialog-bar { padding:11px 22px; }
      .onb-actions button { flex:1 1 100%; text-align:left; }
    }
"""

JS = r"""
<script>
(function(){
  // small words stay lower case inside names: 'Clear and Refill', 'Suspend the Rules'
  if (typeof displayOperationName === 'function') {
    var dn = displayOperationName, small = /^(and|the|of|to|a|an|in|on|for|with|by|or|as|at|from|into|but|nor|yet|so)$/i;
    displayOperationName = function(name){ return dn(name).split(' ').map(function(w, i){ return i && small.test(w) && w !== 'Yet' ? w.toLowerCase() : w; }).join(' '); };
  }
  var c = document.querySelector('#operation-detail-content'); if (!c) return;
  c.setAttribute('tabindex', '-1'); c.style.outline = 'none';
  var o = openOperationDetail;
  openOperationDetail = function(){ var r = o.apply(this, arguments); setTimeout(function(){ try { c.focus({preventScroll:true}); } catch (e) {} }, 0); return r; };
})();
</script>
"""


import re


def patch_html(npage):
    # drop the beta's embedded Atkinson Hyperlegible: the page now loads IBM Plex Sans
    npage, n = re.subn(r"@font-face \{\s*font-family:'Atkinson Hyperlegible';.*?\}\s*", '', npage, flags=re.S)
    npage = npage.replace("font:400 17px/1.5 'Atkinson Hyperlegible', Arial, sans-serif;", "font:400 17px/1.5 'IBM Plex Sans', Arial, sans-serif;")
    return npage.replace('</style>', CSS + FONT_CSS + '  </style>', 1)
