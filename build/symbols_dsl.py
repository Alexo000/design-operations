# Set A grammar: cell 6 wide, 10 tall; centre of cell (c,r) at (3+6c, 5+10r). Time runs down.
SW=0.6
class S:
    def __init__(s,cols,rows): s.cols=cols; s.rows=rows; s.el=[]
    @staticmethod
    def X(c): return 3+6*c
    @staticmethod
    def Y(r): return 5+10*r
    def add(s,t): s.el.append(t); return s
    def _op(s,op): return '' if op in (None,1) else f' fill-opacity="{op}"'
    def sq(s,c,r,k=1.0,op=None):
        a=4.2*k; x,y=s.X(c),s.Y(r)
        return s.add(f'<rect x="{x-a/2:.2f}" y="{y-a/2:.2f}" width="{a:.2f}" height="{a:.2f}" fill="currentColor"{s._op(op)}/>')
    def osq(s,c,r,k=1.0,dash=False):
        a=4.2*k; x,y=s.X(c),s.Y(r); d=' stroke-dasharray="0.9 0.7"' if dash else ''
        return s.add(f'<rect x="{x-a/2:.2f}" y="{y-a/2:.2f}" width="{a:.2f}" height="{a:.2f}" fill="none" stroke="currentColor" stroke-width="{SW}"{d}/>')
    def box(s,c0,r0,c1,r1,op=None,fill=True,dash=False,inset=1.0):
        x0=6*c0+inset; y0=10*r0+inset; x1=6*(c1+1)-inset; y1=10*(r1+1)-inset
        if fill: return s.add(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}" fill="currentColor"{s._op(op)}/>')
        d=' stroke-dasharray="0.9 0.7"' if dash else ''
        return s.add(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}" fill="none" stroke="currentColor" stroke-width="{SW}"{d}/>')
    def rect(s,x,y,w,h,op=None):
        return s.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="currentColor"{s._op(op)}/>')
    def dot(s,c,r,rad=0.7,op=None):
        return s.add(f'<circle cx="{s.X(c):.2f}" cy="{s.Y(r):.2f}" r="{rad}" fill="currentColor"{s._op(op)}/>')
    def me(s,c,r): return s.add(f'<circle cx="{s.X(c):.2f}" cy="{s.Y(r):.2f}" r="2.3" fill="currentColor"/>')
    def other(s,c,r): return s.add(f'<circle cx="{s.X(c):.2f}" cy="{s.Y(r):.2f}" r="2.0" fill="none" stroke="currentColor" stroke-width="{SW}"/>')
    def tri(s,c,r,k=1.0,op=None):
        x,y=s.X(c),s.Y(r); a=2.6*k
        return s.add(f'<polygon points="{x:.2f},{y-a:.2f} {x+a*1.1:.2f},{y+a*0.9:.2f} {x-a*1.1:.2f},{y+a*0.9:.2f}" fill="currentColor"{s._op(op)}/>')
    def circ(s,c,r,k=1.0,op=None):
        return s.add(f'<circle cx="{s.X(c):.2f}" cy="{s.Y(r):.2f}" r="{2.3*k:.2f}" fill="currentColor"{s._op(op)}/>')
    def line(s,x1,y1,x2,y2,w=SW,dash=False):
        d=' stroke-dasharray="0.9 0.7"' if dash else ''
        return s.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="currentColor" stroke-width="{w}" stroke-linecap="butt"{d}/>')
    def h(s,c0,c1,r,dash=False): return s.line(s.X(c0),s.Y(r),s.X(c1),s.Y(r),dash=dash)
    def v(s,c,r0,r1,dash=False): return s.line(s.X(c),s.Y(r0),s.X(c),s.Y(r1),dash=dash)
    def dbl(s,c0,c1,r,dy=0.0):
        y=s.Y(r)+dy; x0=6*c0; x1=6*(c1+1)
        s.line(x0,y-0.9,x1,y-0.9); return s.line(x0,y+0.9,x1,y+0.9)
    def arr(s,c,r,d='d'):
        x,y=s.X(c),s.Y(r)
        if d=='d': s.line(x,y-3,x,y+2.4); return s.add(f'<polygon points="{x:.2f},{y+3.6:.2f} {x-1.2:.2f},{y+1.52:.2f} {x+1.2:.2f},{y+1.52:.2f}" fill="currentColor"/>')
        if d=='u': s.line(x,y+3,x,y-2.4); return s.add(f'<polygon points="{x:.2f},{y-3.6:.2f} {x-1.2:.2f},{y-1.52:.2f} {x+1.2:.2f},{y-1.52:.2f}" fill="currentColor"/>')
    def harr(s,c0,c1,r,d='r'):
        y=s.Y(r)
        if d=='r':
            x0,x1=s.X(c0),s.X(c1); s.line(x0,y,x1-1.6,y); return s.add(f'<polygon points="{x1:.2f},{y:.2f} {x1-2.08:.2f},{y-1.2:.2f} {x1-2.08:.2f},{y+1.2:.2f}" fill="currentColor"/>')
        x0,x1=s.X(c0),s.X(c1); s.line(x0,y,x1+1.6,y); return s.add(f'<polygon points="{x1:.2f},{y:.2f} {x1+2.08:.2f},{y-1.2:.2f} {x1+2.08:.2f},{y+1.2:.2f}" fill="currentColor"/>')
    def cross(s,c,r,k=1.0):
        x,y=s.X(c),s.Y(r); a=2*k
        s.line(x-a,y-a,x+a,y+a,0.8); return s.line(x-a,y+a,x+a,y-a,0.8)
    def txt(s,c,r,t,size=7.6):
        return s.add(f'<text x="{s.X(c):.2f}" y="{s.Y(r)+size*0.35:.2f}" font-size="{size}" text-anchor="middle" font-family="Sym, monospace" fill="currentColor">{t}</text>')
    def rule(s,c,r,n=3,w=1.6):
        x0=s.X(c)-3*w; x1=s.X(c)+3*w; y0=s.Y(r)-(n-1)*0.9
        for i in range(n): s.line(x0,y0+i*1.8,x1,y0+i*1.8)
        return s
    def svg(s):
        W=6*s.cols; H=10*s.rows
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {W+2:.1f} {H+2:.1f}">'+''.join(s.el)+'</svg>'
