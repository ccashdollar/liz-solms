"""Motion regression suite for the Liz Solms site.

Proves two properties:

  1. NOTHING IS EVER STRANDED. No combination of JavaScript availability,
     reduced-motion setting, viewport or scroll position can leave text
     below full opacity once it has been reached.

  2. NO FADE RAMP. Text that is comfortably on screen, with scrolling
     stopped, is never sitting at partial opacity. This is the regression
     test for the artefact that scroll-LINKED reveals produce: every item in
     a list sits at a different scroll progress at once, so a list renders
     as a permanent gradient from solid to nearly invisible. Reveals are
     scroll-TRIGGERED and time-based specifically to make this impossible.

    python3 motion_test.py            # all checks
    python3 motion_test.py --quick    # two viewports only
"""
from playwright.sync_api import sync_playwright
import sys

URL = 'file:///root/preview/index.html'
JUMP = "(y)=>{document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,y);}"
SEL = ('.work .section-heading,.events .section-heading,.bio,.work__list > li,'
       '.events__item,.events__empty,.events__past,.contact,.colophon,.purchase,.wordmark')

# Opacity ALONE is not enough. A prose block reveals with a mask, and masked
# text still reports opacity 1 — a mask stuck part-way through would hide half
# a paragraph and pass an opacity check silently. So both are asserted.
STRANDED = """(sel)=>{const o=[];
  for(const e of document.querySelectorAll(sel)){
    if(e.checkVisibility && !e.checkVisibility({contentVisibilityAuto:true,visibilityProperty:true})) continue;
    const cs=getComputedStyle(e);
    const op=+cs.opacity;
    if(op<0.99) o.push(['opacity '+op.toFixed(2),(e.textContent||'').trim().slice(0,24)]);
    if(cs.maskImage && cs.maskImage!=='none'){
      // Axis matters: the wordmark sweeps HORIZONTALLY and is vertically
      // centred, so its resting mask-position is "0% center" — reading the
      // y component there gives 50% and looks like a failure. Prose blocks
      // wipe DOWNWARD and rest at y = 0.
      const parts=(cs.maskPosition||'').split(' ');
      const horiz=e.matches('.wordmark');
      const v=parseFloat(horiz?parts[0]:parts[1]);
      if(!isNaN(v)&&Math.abs(v)>0.5)
        o.push(['mask '+(horiz?'x':'y')+' '+v.toFixed(1),(e.textContent||'').trim().slice(0,24)]);}}
  return o;}"""

RAMP = """(sel)=>{const o=[];
  for(const e of document.querySelectorAll(sel)){
    const r=e.getBoundingClientRect();
    if(r.bottom<40||r.top>innerHeight-40) continue;     // not comfortably on screen
    const op=+getComputedStyle(e).opacity;
    if(op>0.02&&op<0.98) o.push([+op.toFixed(2),(e.textContent||'').trim().slice(0,24)]);}
  return o;}"""

QUICK = '--quick' in sys.argv
SIZES = [(1366, 900), (390, 844)] if QUICK else [(1920,1080),(1366,900),(900,900),(768,1024),(390,844),(320,700)]
fails = 0

with sync_playwright() as p:
    b = p.chromium.launch()

    print("1. NOTHING STRANDED")
    for label, block, reduced in (("normal",0,0), ("JS blocked",1,0), ("reduced motion",0,1)):
        for w,h in SIZES:
            ctx = b.new_context(viewport={'width':w,'height':h},
                                reduced_motion='reduce' if reduced else 'no-preference')
            if block: ctx.route("**/motion.js", lambda r: r.abort())
            pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(3200)
            H = pg.evaluate("()=>document.documentElement.scrollHeight")
            for y in range(0, H, int(h*0.6)):
                pg.evaluate(JUMP, y); pg.wait_for_timeout(60)
            pg.evaluate(JUMP, H); pg.wait_for_timeout(3200)
            pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
            pg.wait_for_timeout(2600)
            bad = pg.evaluate(STRANDED, SEL)
            if bad: fails += len(bad); print(f"   !! {label} {w}x{h}: {bad}")
            ctx.close()
        print(f"   {label}: clean")

    print("\n2. NO FADE RAMP  (text at rest, on screen, part-faded)")
    for w,h in SIZES:
        pg = b.new_page(viewport={'width':w,'height':h}); pg.goto(URL); pg.wait_for_timeout(3200)
        H = pg.evaluate("()=>document.documentElement.scrollHeight"); n = 0
        step = 260 if QUICK else 160
        for y in range(0, H, step):
            pg.evaluate(JUMP, y); pg.wait_for_timeout(3000)      # longer than --dur-wipe-load + lead
            bad = pg.evaluate(RAMP, SEL)
            if bad: n += len(bad); print(f"   !! {w}px scrollY={y}: {bad}")
        print(f"   {w}x{h}: {H//step} resting positions, {n} part-faded")
        fails += n; pg.close()

    b.close()

print("\nRESULT:", "PASS" if fails == 0 else f"{fails} FAILURES")
sys.exit(0 if fails == 0 else 1)
