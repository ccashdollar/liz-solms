from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np, sys
def lin(c):
    c=c/255.0
    return np.where(c<=0.03928,c/12.92,((c+0.055)/1.055)**2.4)
def L(a):
    a=a.astype(float); return 0.2126*lin(a[...,0])+0.7152*lin(a[...,1])+0.0722*lin(a[...,2])
HIDE='*{color:transparent!important;text-decoration-color:transparent!important;}'
SEL='.bio p,.work__list li,.events__list li,.contact p,.section-heading,.wordmark,.purchase span,.work__title,.work__outlet'
# Measure the TEXT's own line boxes, not the element box. A block element's box
# spans the full column even when its ink is a short heading, which reported
# false failures against art sitting harmlessly beside it.
RECTS = """(sel)=>{
  const out=[];
  for (const el of document.querySelectorAll(sel)) {
    // Skip anything not actually painted. A closed <details> still reports
    // layout rects for its contents in Chromium (hidden via
    // content-visibility, not display), which read as text sitting on art.
    if (el.checkVisibility && !el.checkVisibility({contentVisibilityAuto:true, opacityProperty:true, visibilityProperty:true})) continue;
    const w=document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n=w.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const r=document.createRange(); r.selectNodeContents(n);
      for (const b of r.getClientRects()) {
        if (b.width<4 || b.height<4) continue;
        out.push({txt:n.nodeValue.trim().slice(0,26), x:b.x+scrollX, y:b.y+scrollY, w:b.width, h:b.height});
      }
    }
  }
  return out;
}"""
OPEN_DETAILS = '--open' in sys.argv
widths=[int(x) for x in sys.argv[1:] if x.isdigit()] or [2560,1920,1600,1400,1366,1200,1100,1000,900,899,768,600,480,390,320]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in widths:
        pg=b.new_page(viewport={'width':w,'height':900}); pg.goto('file:///home/claude/preview/index.html'); pg.wait_for_timeout(2000)
        sx=pg.evaluate('()=>{window.scrollTo(9999,0);window.scrollTo(0,0);return window.scrollX;}')
        unl=pg.evaluate('[...document.querySelectorAll(".deco__item")].filter(e=>getComputedStyle(e).zIndex==="auto").length')
        rects=pg.evaluate(RECTS, SEL)
        pg.screenshot(path=f'/home/claude/preview/v-{w}.png', full_page=True)
        pg.add_style_tag(content=HIDE); pg.wait_for_timeout(400)
        pg.screenshot(path='/tmp/bg.png', full_page=True); pg.close()
        bg=np.asarray(Image.open('/tmp/bg.png').convert('RGB'))
        worst=[]
        for r in rects:
            x,y,ww,hh=[int(v) for v in (r['x'],r['y'],r['w'],r['h'])]
            patch=bg[max(0,y):y+hh, max(0,x):x+ww]
            if patch.size==0: continue
            worst.append((round(float((np.percentile(L(patch),2)+0.05)/0.05),2), r['txt']))
        worst.sort()
        f=[t for t in worst if t[0]<4.5]
        flag='' if not f else '  <-- '+', '.join(f'{a:.2f}:1 "{t}"' for a,t in f[:3])
        print(f'  {w:5d}px  scroll {sx}  unlayered {unl}  worst {worst[0][0]:6.2f}:1 "{worst[0][1][:24]}"  fails {len(f)}{flag}')
    b.close()
