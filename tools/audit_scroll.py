"""Contrast audit that steps through scroll positions.

The original audit measured one static full-page render. That was correct
until the collage started drifting: art now moves up to 20px relative to the
text as the page scrolls, so a passing reading at scroll 0 no longer proves
the same text passes at scroll 1200. This walks each width down the page and
measures every text line against the art actually behind it at that moment.
"""
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np, io, sys

URL='file:///root/preview/index.html'
def lin(c):
    c=c/255.0
    return np.where(c<=0.03928,c/12.92,((c+0.055)/1.055)**2.4)
def L(a):
    a=a.astype(float); return 0.2126*lin(a[...,0])+0.7152*lin(a[...,1])+0.0722*lin(a[...,2])

HIDE='*{color:transparent!important;text-decoration-color:transparent!important;}'
SEL='.bio p,.work__list li,.events__list li,.contact p,.section-heading,.wordmark,.purchase span,.work__title,.work__outlet,.colophon'

RECTS="""(sel)=>{const out=[];
  for (const el of document.querySelectorAll(sel)) {
    if (el.checkVisibility && !el.checkVisibility({contentVisibilityAuto:true,opacityProperty:true,visibilityProperty:true})) continue;
    const w=document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
    while ((n=w.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const r=document.createRange(); r.selectNodeContents(n);
      for (const b of r.getClientRects()) {           // viewport-relative
        if (b.width<4||b.height<4) continue;
        if (b.bottom<0||b.top>innerHeight) continue;  // off screen right now
        out.push({txt:n.nodeValue.trim().slice(0,26),x:b.x,y:b.y,w:b.width,h:b.height});
      }
    }
  } return out;}"""

widths=[int(x) for x in sys.argv[1:] if x.isdigit()] or [1920,1366,1100,900,768,566,390,320]
worst_overall=(99,'','',0)
fails=0
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in widths:
        ctx=b.new_context(viewport={'width':w,'height':900})
        pg=ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(1200)
        H=pg.evaluate('()=>document.documentElement.scrollHeight')
        stops=list(range(0,max(1,H-900+1),300))+[H-900]
        wrow=(99,'')
        n=0
        for y in stops:
            if y<0: continue
            pg.evaluate(f'window.scrollTo(0,{y})'); pg.wait_for_timeout(260)
            rects=pg.evaluate(RECTS,SEL)
            if not rects: continue
            pg.add_style_tag(content=HIDE); pg.wait_for_timeout(220)
            shot=pg.screenshot()              # viewport only, current scroll
            pg.evaluate("()=>{const s=[...document.querySelectorAll('style')].pop(); if(s) s.remove();}")
            pg.wait_for_timeout(120)
            bg=np.asarray(Image.open(io.BytesIO(shot)).convert('RGB'))
            for r in rects:
                x,yy,ww,hh=[int(v) for v in (r['x'],r['y'],r['w'],r['h'])]
                patch=bg[max(0,yy):yy+hh, max(0,x):x+ww]
                if patch.size==0: continue
                ratio=round(float((np.percentile(L(patch),2)+0.05)/0.05),2)
                n+=1
                if ratio<wrow[0]: wrow=(ratio,r['txt'])
                if ratio<4.5: fails+=1
                if ratio<worst_overall[0]: worst_overall=(ratio,r['txt'],f'{w}px',y)
        mark='' if wrow[0]>=4.5 else '   <-- FAIL'
        print(f'  {w:5d}px  {len(stops):2d} scroll stops  {n:4d} lines measured   worst {wrow[0]:6.2f}:1  "{wrow[1][:26]}"{mark}')
        ctx.close()
    b.close()
print(f'\nWorst anywhere: {worst_overall[0]}:1  "{worst_overall[1]}"  at {worst_overall[2]} scrollY={worst_overall[3]}')
print('RESULT:', 'PASS — no text below 4.5:1 at any scroll position' if fails==0 else f'{fails} FAILING LINE-POSITIONS')
