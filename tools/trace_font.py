"""Trace Black-Paint's sbix bitmaps into a real outline font (CFF -> WOFF2)."""
import sys, os, subprocess, io, tempfile
sys.path.insert(0, '/home/claude/fontlab')
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from PIL import Image
from svgelements import SVG, Path, Move, Line, Close, CubicBezier, QuadraticBezier

SRC = '/mnt/user-data/uploads/Liz Solm/Black Paint Font/OTF Font/Black-Paint.otf'

def trace_glyph(bitmap, turd, alphamax, opttol, tmpd):
    a = bitmap.getchannel('A')
    bw = a.point(lambda v: 0 if v >= 110 else 255).convert('1')   # ink = black for potrace
    pbm = os.path.join(tmpd, 'g.pbm'); svg = os.path.join(tmpd, 'g.svg')
    bw.save(pbm)
    subprocess.run(['potrace','-s','-t',str(turd),'-a',str(alphamax),
                    '-O',str(opttol),'-o',svg,pbm], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    doc = SVG.parse(svg)
    # svgelements converts potrace's 'pt' viewport to px at 96/72.
    # Undo that so 1 SVG unit == 1 bitmap pixel again.
    corr = bitmap.size[0] / float(doc.width)
    return doc, bitmap.size, corr

def build(turd=2, alphamax=1.0, opttol=0.2, out='traced.woff2', flavor='woff2'):
    src = TTFont(SRC)
    cmap = src.getBestCmap(); hmtx = src['hmtx']
    upem = src['head'].unitsPerEm
    strike = list(src['sbix'].strikes.values())[0]
    k = upem / strike.ppem          # px -> font units

    order = ['.notdef'] + [g for g in src.getGlyphOrder() if g != '.notdef']
    charstrings = {}; metrics = {}
    tmpd = tempfile.mkdtemp()
    nodes = 0

    for g in order:
        adv = hmtx[g][0] if g in hmtx.metrics else 500
        sb = strike.glyphs.get(g)
        pen = T2CharStringPen(adv, None)
        if sb and sb.imageData:
            bm = Image.open(io.BytesIO(sb.imageData)).convert('RGBA')
            doc, (pw, ph), corr = trace_glyph(bm, turd, alphamax, opttol, tmpd)
            k2 = k * corr
            for el in doc.elements():
                if not isinstance(el, Path):
                    continue
                started = False
                for seg in el:
                    if isinstance(seg, Move):
                        if started: pen.closePath()
                        pen.moveTo((seg.end.x*k2, (ph-seg.end.y*corr)*k)); started = True; nodes += 1
                    elif isinstance(seg, Line):
                        pen.lineTo((seg.end.x*k2, (ph-seg.end.y*corr)*k)); nodes += 1
                    elif isinstance(seg, CubicBezier):
                        pen.curveTo((seg.control1.x*k2, (ph-seg.control1.y*corr)*k),
                                    (seg.control2.x*k2, (ph-seg.control2.y*corr)*k),
                                    (seg.end.x*k2,      (ph-seg.end.y*corr)*k)); nodes += 3
                    elif isinstance(seg, QuadraticBezier):
                        pen.qCurveTo((seg.control.x*k2, (ph-seg.control.y*corr)*k),
                                     (seg.end.x*k2, (ph-seg.end.y*corr)*k)); nodes += 2
                    elif isinstance(seg, Close):
                        pass
                if started: pen.closePath()
        charstrings[g] = pen.getCharString()
        metrics[g] = (adv, hmtx[g][1] if g in hmtx.metrics else 0)

    fb = FontBuilder(upem, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({c: n for c, n in cmap.items()})
    fb.setupCFF('BlackPaintWeb', {'FullName':'Black Paint Web','Weight':'Regular'},
                charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=src['hhea'].ascender, descent=src['hhea'].descender)
    fb.setupNameTable({'familyName':'Black Paint Web','styleName':'Regular',
                       'psName':'BlackPaintWeb-Regular'})
    fb.setupOS2(sTypoAscender=src['hhea'].ascender, sTypoDescender=src['hhea'].descender,
                usWinAscent=src['hhea'].ascender, usWinDescent=abs(src['hhea'].descender))
    fb.setupPost()
    fb.font.flavor = flavor if flavor != 'otf' else None
    fb.save(out)
    return os.path.getsize(out), nodes

if __name__ == '__main__':
    import json
    presets = {
      'faithful':  dict(turd=2,  alphamax=1.0, opttol=0.15),
      'balanced':  dict(turd=8,  alphamax=1.0, opttol=0.3),
      'clean':     dict(turd=40, alphamax=1.0, opttol=0.8),
    }
    for name, p in presets.items():
        sz, nd = build(out=f'/home/claude/fontlab/bp-{name}.woff2', **p)
        build(out=f'/home/claude/fontlab/bp-{name}.otf', flavor='otf', **p)
        print(f'{name:10s} turd={p["turd"]:3d} O={p["opttol"]:<4} -> {sz/1024:7.1f} KB woff2   {nd} nodes')
