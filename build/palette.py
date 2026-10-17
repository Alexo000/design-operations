"""palette.py — the page's background and greys (2026-10-17, work lane, option b): cool grey paper in place of the
warm off-white, which read too close to another product's cream. Applied as a last pass on every page the build writes,
so the source page and the other modules keep their old values and this file is the one place the palette lives."""
MAP = {
    '#f7f7f3': '#f1f2f4',   # paper
    '#e5e5de': '#e2e4e8',   # selected
    '#c8c8c1': '#c6c9cf',   # line
    '#70706a': '#6c7079',   # strong line
    '#62625e': '#5e626a',   # muted text
}


def apply(text):
    for a, b in MAP.items():
        text = text.replace(a, b).replace(a.upper(), b)
    return text
