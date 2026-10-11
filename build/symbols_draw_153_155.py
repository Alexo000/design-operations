"""Set A drawings (with E for small sizes) for the entries added after the symbol records of 2026-10-02:
153 LEAVE ONE OUT, 154 PRETEND, 155 RECALL. Same grammar as symbols_draw_112_152.py (symbols_dsl.py):
marks on a fixed grid, time running down, a cross only for a break or a refusal, a face only where a person is the subject.
Drawn 2026-10-10 for the explorer; status: proposed symbol."""
from symbols_dsl import S
A = {}; E = {}


def reg(n):
    def w(f):
        a, e = f(); A[n] = a.svg(); E[n] = e.svg(); return f
    return w


@reg(153)  # LEAVE ONE OUT: each round a different part is missing; at the end everything is back
def _():
    s = S(7, 9)
    marks = [lambda c, r: s.sq(c, r, 1.0), lambda c, r: s.tri(c, r, 1.0), lambda c, r: s.circ(c, r, 0.8),
             lambda c, r: s.osq(c, r, 1.0), lambda c, r: s.sq(c, r, 0.7)]
    cols = [1, 2, 3, 4, 5]
    for rnd in range(4):
        r = rnd * 1.6
        for i, c in enumerate(cols):
            if i == rnd:
                s.osq(c, r, 1.0, dash=True)
            else:
                marks[i](c, r)
    s.dbl(0, 6, 6.0)
    for i, c in enumerate(cols):
        marks[i](c, 7.2)
    e = S(5, 2)
    for c in (0, 1, 3, 4): e.sq(c, 0, 0.7)
    e.osq(2, 0, 0.7, dash=True)
    for c in range(5): e.sq(c, 1, 0.7)
    return s, e


@reg(154)  # PRETEND: one stated premise that is not true; acted under for a set time; never tested
def _():
    s = S(7, 9)
    s.box(1, 0, 5, 0, fill=False, dash=True, inset=0.8); s.rule(3, 0, 3, 1.6)
    s.arr(3, 1)
    for i, c in enumerate((1.5, 3.0, 4.5)):
        r = 2.2 + i * 1.6
        s.me(c, r); s.box(c - 0.45, r - 0.42, c + 0.45, r - 0.42, fill=False, dash=True, inset=0) if False else None
        s.osq(c + 0.9, r - 0.5, 0.6, dash=True)
    s.v(6.4, 1.6, 5.8)
    for r in (1.6, 2.6, 3.6, 4.6, 5.6): s.line(s.X(6.4) - 1.2, s.Y(r), s.X(6.4), s.Y(r))
    s.dbl(0, 6, 6.6)
    s.txt(3, 7.7, '?', 6); s.cross(4.4, 7.7, 0.8)
    e = S(4, 1); e.osq(0.6, 0, 1.0, dash=True); e.me(2.2, 0); e.v(3.4, -0.35, 0.35)
    return s, e


@reg(155)  # RECALL: the original is gone; it is made again from memory; the original is never checked
def _():
    s = S(7, 9)
    s.sq(1.5, 0, op=0.25); s.tri(3, 0, op=0.25); s.circ(4.5, 0, 0.8, op=0.25)
    s.dbl(0, 6, 0.9)
    s.me(0, 2.2); s.arr(3, 3.1)
    s.sq(1.5, 4.4); s.tri(3.3, 4.6, 0.85); s.osq(4.5, 4.4, 0.7, dash=True)
    s.arr(3, 5.7, 'u'); s.cross(4.3, 5.7, 0.8)
    s.dbl(0, 6, 6.8)
    e = S(4, 2); e.sq(0.5, 0, 0.7, op=0.25); e.tri(1.5, 0, 0.7, op=0.25); e.dbl(0, 3, 0.55)
    e.sq(0.5, 1.1, 0.7); e.tri(1.6, 1.15, 0.65); e.osq(2.6, 1.1, 0.6, dash=True)
    return s, e
