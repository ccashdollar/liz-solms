# Liz Solms — one-page site

Static front-end for handoff to a development partner (CMS TBD).
Design source: `../Archive/Liz Solms Page.pdf` (artboard 1366 × 3325).

## Structure

```
site/
├── index.html          semantic content + per-band decorative layers
├── css/
│   ├── tokens.css      design tokens — colour, type scale, spacing
│   ├── style.css       typography, components, legibility
│   └── layout.css      page bands, grid, collage placement
├── docs/               evidence + measured comp coordinates
├── tools/              font + heading build scripts
└── assets/
    ├── images/         WebP + responsive size ladder
    │   └── 2x/         original PNG exports (archive, not shipped)
    └── fonts/          traced Black Paint webfont
```

## Responsive collage

The comp is a fixed 1366 x 3325 artboard. Positioning every element at an
absolute page coordinate breaks as soon as the events list grows — the art
would stay put while the text moved. Instead the page is split into three
BANDS, each holding content plus its own `.deco` layer positioned relative
to that band, so art travels with the content it belongs to.

Each element has a role that decides its behaviour as space runs out:

| role | behaviour | examples |
|---|---|---|
| EDGE-BLEED | anchored to an edge, runs off it — crops rather than shrinks | strips, frond |
| BACKDROP | sits behind text, stretches with its band | torn paper panels |
| ACCENT | scales down, may drop below 600px | paint marks |
| CONTENT | real images in the flow | portrait, diving photo |

Sizes are `clamp(min, %, max)`: the % keeps the comp's proportions, the min
stops art becoming confetti on a phone, the max stops it overrunning the
artboard on a wide monitor. Positions are % of the band.

### Depth — how layers respond to a window wider than the design

The comp is a 1366 artboard, and **an artboard is a viewport, not a canvas.**
Art drawn to or past its edge was meant to be cropped by the edge of the
screen. Position it inside the 1366 content column and it detaches the moment
the window is wider — measured on an earlier build, the frond bled 14px past
the right edge at 1366 and then floated **583px inside it at 2560**.

Rather than a hard split between "in the column" and "on the window", every
decorative element carries a `--depth` from 0 to 1, and shifts outward by
`depth x --overflow`, where `--overflow` is how far the window extends past
the design width on each side.

| token | value | applied to |
|---|---|---|
| `--depth-flat` | 0 | the writing |
| `--depth-near` | 0.25 | the paper column behind the lists |
| `--depth-mid` | 0.5 | portrait, teal splatter |
| `--depth-far` | 1 | all edge art — strips, frond, paint smear, torn paper |

Measured travel per 640px of extra window width:

| layer | moves |
|---|---|
| paper column | +240px (drifts outward the other way) |
| the text | +320px (the centred column) |
| portrait + splatter | +480px |
| frond + paint smear | +640px — edge gap stays constant |

At 1366 and below `--overflow` is 0, depth does nothing, and the comp renders
exactly as drawn. Above it the layers separate at different rates, so the
collage reads as having depth instead of one flat plane stretching. It is
parallax across viewport *width*, not scroll — static for any given window,
so nothing moves under the reader.

The paint smear is `--depth-far` and right-anchored specifically so it travels
with the frond: in the comp the frond's torn edge cuts across it, and that
relationship has to survive a wide window.

Art is sized `clamp(min, Xvw, MAX)` where MAX is its size in the comp, so past
1366 it stops growing and simply travels. Edge offsets are in `rem`, not `%`,
so the gap to the edge is fixed rather than scaling.

**Known limit:** the composition holds well to about 1920. Beyond that the
collage separates far enough from the text that the middle of the page reads
sparse. If that becomes a problem, cap the drift for the mid and near layers
(a `min()` on their shift) while leaving `--depth-far` uncapped so edge art
stays welded.

### Layering

The collage is not one plane behind the content. `tokens.css` defines an
ordered stacking scale read off the comp **material by material** — the order
the collage was physically assembled in:

| token | value | holds |
|---|---|---|
| `--z-paper` | 1 | torn paper panels — the base |
| `--z-paint` | 2 | painted marks laid onto the paper (smear, pink/gold) |
| `--z-strip` | 3 | coloured strips, over the papers |
| `--z-photo-back` | 4 | the frond photograph |
| `--z-splatter` | 5 | wet paint flicked over the photographs |
| `--z-content` | 20 | text, and images that ARE content |
| `--z-art-front` | 30 | reserved — nothing uses it |
| `--z-ui` | 50 | skip link, focus affordances |

**The teal splatter sits BELOW the portrait**, not above. In the comp the
splatters stop dead at Liz's silhouette — the blob by her waist ends exactly
at her edge, and the one near her hip is on the frond behind her. It goes
above the photographs and below the content.

Its scale was also badly under-set: the comp runs the asset at **~1328px
against a 1366 artboard**, essentially full page width, threading from the
portrait down past the purchase blob. It was capped at 42rem (672px) — less
than half — which made it read as a few stray flecks instead of one gesture
across the page.

**Every decorative element declares its layer explicitly.** They were
previously all on one `--z-backdrop`, which meant DOM order decided the
stacking by accident: the cream paper sat in a later band than the blue
strip, so it painted over it and washed it out. The comp has the strip
clearly on top.

The `.deco` wrapper deliberately carries **no** `z-index`. Setting one
creates a stacking context that traps every child inside it, so no piece of
art could rise above the writing however high its own z-index. `.band`
carries none for the same reason. `pointer-events: none` stays on the whole
layer, so front-layer art never blocks selecting the text beneath it.

*Regression check:* count `.deco__item` elements whose computed `z-index` is
`auto`. It must be 0. A malformed comment in `tokens.css` once ate the
`--z-paper` declaration through CSS error recovery, and four elements
silently lost their layer while everything still rendered plausibly.

## Type scale — measured, not estimated

Max sizes are read off the comp at 1366px by scanning the rendered PDF for
text rows and measuring ink height and line spacing:

| role | comp | token |
|---|---|---|
| wordmark | ~58px / 65px leading | `--step-4` |
| bio prose | ~27px / 43px (1.57) | `--step-1` |
| work + events lists | ~22px / 37px (1.64) | `--step-0` |
| contact block | ~34px / 45px (1.28) | `--step-2` |

This is large for web body copy, and it is the whole reason the comp
breathes — fewer words per line, and room above the text for the paint. The
contact block is set larger AND tighter than the bio: a deliberate change of
voice at the foot of the page. Minimums in each `clamp()` are set for a
390px phone, where 27px prose would leave about six words per line.

## The paint smear

The exported `Paint-Multicolor` asset holds **two** paint masses stacked
vertically. The comp uses only the lower one — and they touch, so no
negative offset separates them cleanly; the artwork must be clipped in the
.ai file. The asset is therefore cropped to the lower mass and shipped as
`paint-smear.webp` (1659 × 578), then simply placed — no transform, no
guessing. Side effect: the variant set dropped from 487 KB to 233 KB.

## The purchase CTA

Its background is the painted blob asset (`paint-green-blob.webp`), not a CSS
ellipse — the comp's shape has brush edges a `border-radius` can only
approximate. The box carries the comp's 545 x 261 aspect ratio so the artwork
fills it exactly, and it is centred on the viewport at every width.

**Gotcha worth knowing:** the inset was originally `padding: 0 12%`, which
resolved to **150px a side, not 65** — percentage padding resolves against the
PARENT's inline size (the 1254px band), never the element's own. That left
242px for a title needing 264, so it wrapped and collided with "HERE". Use
`rem`/`vw` for padding on a sized element.

## The portrait below 900px

Full length, the portrait ate most of a small screen before a word of the
writing appeared. Wherever it sits **above** the copy rather than beside it,
it is cropped to head-and-mid-torso (`aspect-ratio: 0.8` +
`object-position: 50% 0%`), with the blue bar pulled up underneath. The bar
lands on the crop line and masks the hard cut, so it reads as a deliberate
collage edge rather than a truncated photo — then does the work of separating
portrait from copy.

**Keep these two breakpoints in sync.** The crop is keyed to the LAYOUT MODE,
not a device size: `max-width: 899px` must match the `min-width: 900px`
two-column rule on `.band--intro`. They were 599 and 900 for a while, and the
300px gap between them was the worst of both worlds — a single-column page
carrying a full-length portrait. The first line of copy started at **y747 on
a 768px screen, lower than the y555 on a 560px phone.** Wider screen, worse
result.

**Portrait and bar are centred throughout this range**, reading as one
stacked unit above the copy rather than pinned to an edge. Capped at 18rem so
it grows a little with a tablet's extra room without pushing the copy down.

Copy-start position across the range — note it now rises smoothly with width
and resets only at the 900px column change, with no snap at 599/600:

| viewport | 320 | 480 | 560 | 599 | 600 | 768 | 899 | 900 | 1366 |
|---|---|---|---|---|---|---|---|---|---|
| first line of copy | y404 | y567 | y631 | y637 | y637 | y661 | y680 | y181 | y238 |

## The frond sits INSIDE the edge

It does not bleed. Measured off the comp at 1366: the photo sits **19px from
the top and 24–29px from the right** — an even margin on both sides. One
token (`--frond-inset`) drives both so they stay equal at every width.

The `transform: translate(5.06%, -4.4%)` compensates for transparent padding
in the asset: the solid photo starts 4.4% down and stops 5.06% short of the
right edge, so without it the margin you set is the margin to the FILE's box,
not to the photograph.

**Measure that padding at a high alpha threshold.** A faint-edge reading gave
2.8% on the right and left the margin 10px too wide — the artwork has a soft
antialiased fringe well outside the visible photo.

Below 600px the frond and smear are sized to come **just short of the
portrait** — 8px clear at 390, 11px at 566 — with `42vw` / `70vw`. That pair
was found by sweeping, not guessed:

| frond / smear | gap to portrait @390 | wordmark backdrop |
|---|---|---|
| 30 / 58vw | 58px | 18.5:1 |
| 40 / 68vw | 15px | 18.5:1 |
| **42 / 70vw** | **8px** | **18.4:1** |
| 43 / 71vw | 5px | 10.8:1 — smear creeping under the wordmark |

Below **380px** they shrink again (`38vw` / `55vw`, pushed further off the
right). The wordmark bottoms out at its clamp minimum around 390, so at 320
it still runs to x186 while the viewport has lost 70px — the graphics have to
give that width back. Without this the smear sat under the wordmark at
**1.94:1**. Sweeping only 390 and 566 missed it; 320 must be in the test set.

## The smear / frond join

They must always read as one continuous mass — no bare ground between them,
and nothing above the smear at the top of the page. Three things make that
hold:

- **`top: 0` on the smear.** Any inset leaves a band of ground above it.
- **`right: 12%`, not 21%.** The box edges lie about where the two meet.
  The frond's left edge is a torn diagonal — its ink starts 6.9% into its box
  near the top but 13.8% in at 20% down, which is exactly the height the
  smear sits at. The smear's own ink ends at 84% of ITS box. Between them
  that opened a real 33px gap at ~878px while the bounding boxes still
  reported 62px of overlap.
- **`translateY(-4.5%)` on the frond.** The asset carries transparent
  padding: its ink starts 4.3% down its own height. At `top: 0.5rem` that
  left ~36px of bare ground across the top-right at 1366 — a band the smear
  could not reach into, which is what actually read as "the gap". The
  percentage resolves against the element's own height, so it holds at any
  size.

Verified by rendering each element in isolation and comparing per-row ink
extents, not by bounding box. Note that a naive ink test misreads this
artwork: the painting contains near-white passages that a "not the ground
colour" check counts as empty.

## The paint smear on small screens

The wordmark owns the top-left, leaving a fixed ~240px window on the right.
Widening the smear there just scales it up and crops more of it away — so to
show *more of the artwork* it goes smaller with far less bleed. Was 92vw
hanging 40% off the edge (≈47% of the painting visible); now 64vw hanging 6%
off (≈91% visible).

**64vw is a hard ceiling, not a taste call.** At 72vw the smear reaches back
under the wordmark and its backdrop contrast collapses to **1.92:1** on a
320px screen. At 64vw it holds 7.86:1.

The bar exists twice: `.portrait__strip` inside the figure for these
treatments, and `.d-strip-blue` in the collage layer above 900 where it bleeds
off the right instead. Only one is ever displayed; same `src`, one download.

## The two middle sections are NOT one column

Measured at 1366 in the comp:

| block | left edge | % of page |
|---|---|---|
| SELECTED PUBLISHED WORK | x358 | 26% |
| EVENTS + APPEARANCES | x85 | 6% |

That indent is what makes Events read as its own section rather than a
continuation of the work list, with the diving photo to its right. Both were
at 16% — one column. Split above 900px; below that they share a left edge,
where there is no width to spend on the distinction.

`--gutter` also went from 3.5rem to 4.5rem: the comp's left margin is x72–90
and the page was running 16px tight against it.

## The pink/gold collage is anchored to the block it decorates

`.d-paint-left` lives inside `.works-block` (purchase + published work) with
`height: 100%; object-fit: cover`, not in the band's deco layer at its
natural aspect ratio.

Anchored to the band, its bottom landed wherever the band happened to end —
and because the comp's work list is longer than ours, the same artwork that
brackets it there **overshot and cut through the EVENTS heading between
roughly 1200 and 1600px** (1.87:1 behind the heading, 1.46:1 behind the list).
Anchoring it to the block means it ends with the work list and stretches when
the CMS adds items.

Below 900 it is pushed off the left edge (`-7rem`): the work list runs to the
left margin there and sat straight over it at 1.79:1.

## A CSS trap that bit twice

Both times I edited `tokens.css` with a comment that closed early, CSS error
recovery swallowed the declaration that followed, and the page **still
rendered plausibly** — no error, no warning. Once it silently unlayered four
collage elements; once it wiped the entire type scale back to 16px browser
default.

Two cheap guards, both worth keeping in any build step:

- Assert `/*` and `*/` counts match in every stylesheet.
- Assert no `.deco__item` has a computed `z-index` of `auto`.

## Letter-spacing is per-role, and was solved not guessed

Tracking and size can be separated because **cap height is unaffected by
tracking**: pin the size from cap height, then fit the spacing to the
rendered string width.

| | comp | was |
|---|---|---|
| `--tracking-wordmark` | **0.37em** | 0.05em |
| `--tracking-display` (section headings) | 0.03em | 0.06em |
| `--tracking-cta` | 0.05em | 0.06em |

The wordmark was the outlier by a long way. "LIZ" fitted 0.367em and
"SOLMS" 0.373em *independently*, which is the check that the fit is real.
That wide spacing IS the wordmark — at 0.05em it read as a heading rather
than a name. Rendered ink now measures 138.5 and 276.5px against the comp's
138 and 278.

Section headings went the other way and needed *less*.

*Measuring note:* CSS adds letter-spacing after the last character too, so
`getClientRects()` overstates a tracked line by one full letter-space —
21px on the wordmark. Subtract it before comparing to ink measured off a
render.

## The top-left yellow strip

Comp: 477px wide, ~58px deep at the left edge. It was rendering 381 x 38
because the **`clamp()` maximum was the binding term, not the `vw`** — the
preferred value wanted 628px and the 30rem cap held it to 480. Raised to
36rem, and the vertical crop eased from -52% to -45%. Now 477 x 54.

Worth checking whenever a clamped element looks small: which of the three
terms is actually winning.

## Display sizes were all under-set

Section headings and the CTA title were at 22px and 27px. Solved from the
comp two independent ways that agree — the rendered width of the string
against Black Paint's real metrics, and cap height against its 0.74em cap
ratio:

| | measured in comp | was | now |
|---|---|---|---|
| SELECTED PUBLISHED WORK | 840px wide → 39px | 22px | `--step-3` (40px) |
| EVENTS + APPEARANCES | 479px wide, 27px cap → 38px | 22px | `--step-3` |
| SMALL HOT ROOMS (CTA) | 385px wide → 38px | 27px | `0.95 x --step-3` |

The CTA title is 0.95 x rather than a clean step because at a full 40px it
is 396px against a 384px content box and wraps; the comp keeps it on one
line. `.purchase` also carries `text-align: center` — `justify-items` centres
each span as a box but not the text inside one, so a wrapped title set
ragged against its left edge.

## The diving photo and the collage are viewport-anchored

Both behave like the rest of the collage rather than sitting in the text
flow.

- **Diving photo** — above 900 it leaves the flow and anchors to the window
  edge (`--depth-far`), holding 132px from the right at 1366 and 1920
  (comp: 133). In the flow it also squeezed the event list into a half-width
  column; out of it the list keeps its measure.
- **Pink/gold collage** — scaled to the works-block height with its aspect
  ratio **intact** (`height: 100%; width: auto`). The first attempt used
  `object-fit: cover`, which sliced a hard horizontal edge across artwork
  whose whole character is its torn edges. Never crop a torn edge; scale it.

**Watch the containing block when moving decoration between layers.** The
collage sits inside `.works-block`, which is in the band's *content* box, so
an offset there starts one gutter (72px) further in than the same offset on
a band-level layer. It rendered at x96 against the comp's x25 until the
gutter was subtracted.

## Contrast harness: measure text, not element boxes

The audit measures each text node's own line rects via `Range.getClientRects()`.
Measuring element boxes reported false failures: a block heading's box spans
the full column even when its ink is a short string, so it "collided" with
art sitting harmlessly beside it — the Events heading read 1.71:1 against the
diving photo when its text ends at x564 and the photo starts at x578. The
same flaw made the CTA's readings pessimistic by sampling its rounded corners.

## Events — three states

The section is built for all three, so the CMS never has to invent one:

| state | markup |
|---|---|
| **Upcoming events** | `.events__list` — the default |
| **None upcoming** | add `events--empty` to the `<section>`; the list hides, `.events__empty` shows |
| **Past appearances** | `.events__past`, a native `<details>` — present in both states |

Every date carries `<time datetime>` so the CMS has a machine-readable value
to sort on. Worth upgrading to schema.org/Event later — that is what puts
readings into Google's event results.

**The empty state points somewhere.** "No readings on the calendar just now"
plus a link to subscribe to *Ongoing*. An empty state that only apologises
wastes the one moment a reader is looking for a reason to stay.

**Past appearances are collapsed, not hidden.** A `<details>` is keyboard
accessible and announced correctly by screen readers with no JavaScript.
Collapsed so a long history never buries what is coming next; present so the
page still has substance between engagements. Same type sizes as upcoming
events — the collapse already establishes the hierarchy, and shrinking the
type too would say it twice while making the archive harder to read.

**Upcoming event names are the link.** Not the whole row: the name is the
phrase that describes the destination, which is what a screen reader reads
out of a link list ("Small Hot Rooms launch reading", not "12 November
2026"). An event with no page renders the same element as a `<span>` rather
than an `<a>` — same class, same styling, just no link, so the CMS never has
to emit an empty `href`. Past appearances are unlinked.

Content in `index.html` is placeholder and marked as such.

## Auditing: two ways the harness lied

Both produced confident false failures, and both are worth knowing about:

1. **Element boxes are not text.** A block heading's box spans the full
   column even when its ink is a short string, so it "collided" with art
   beside it — the Events heading read 1.71:1 against the diving photo when
   its text ends at x564 and the photo starts at x578. Measure each text
   node's own rects via `Range.getClientRects()`.

2. **Unpainted content still reports layout.** A *closed* `<details>` returns
   real `getBoundingClientRect()` values for its contents in Chromium — it is
   hidden via `content-visibility`, not `display` — so collapsed past events
   registered as text sitting on the diving photo at 1.24:1. Filter with
   `Element.checkVisibility({contentVisibilityAuto: true})`.

`tools/audit_contrast.py` does both. Pass `--open` to expand every
`<details>` and test the disclosed state too.

## Responsive images

Large assets ship a size ladder via `srcset`/`sizes`:

| viewport | collage payload |
|---|---|
| desktop @2x | 1.73 MB |
| tablet @2x | 1.43 MB |
| phone @2x | **0.39 MB** |

Previously every viewport downloaded 1.82 MB.

## The diving photo below 900px

In the flow it was the worst of both worlds: a full-width block that landed
left-aligned UNDER the events list, left a dead area to the right of the
short event entries, and then wedged 517px of itself between the events
section and the contact band — blocking the overlap the comp works hard to
create.

Out of the flow and pinned to the window edge, it does below 900 what the
rest of the collage does at every other width: sits in the open space beside
the text and runs off the edge of the screen.

**Two things scale, in opposite directions.** The photo's width shrinks with
the viewport (`clamp(11rem, 40vw, 22rem)`) while the amount hanging past the
right edge GROWS as the viewport narrows (`clamp(0rem, 9rem - 12vw, 6rem)`).
Together the visible portion falls from ~35% of the screen at 899px to ~20%
at 390px:

| viewport | photo width | bleed | visible | % of screen |
|---|---|---|---|---|
| 899 | 352 | 36 | 316 | 35% |
| 768 | 307 | 52 | 255 | 33% |
| 640 | 256 | 67 | 189 | 30% |
| 566 | 226 | 76 | 150 | 27% |
| 480 | 208 | 102 | 106 | 22% |
| 390 | 176 | 96 | 80 | 21% |

On a tablet it is a picture beside a list; on a phone it is a sliver of
collage at the edge. The text gets more of the screen exactly when it needs
more.

**It is positioned against `.events__body`, not `.events`,** and that choice
does real work: `.events__body` starts BELOW the heading, so `top: 0` puts
the photo alongside the entries rather than alongside "EVENTS +
APPEARANCES". Anchored to `.events` instead, the heading ran into the
photo's left edge at 360 and 390 — the two widths where the heading is still
nearly full width but the photo has come in furthest. The right edge is
unaffected by the switch, because padding sits inside the border box, so
`.events__body`'s padding-box edge is still the section's edge.

`min-height` on `.events__body` reserves the photo's height (its own 1.244
aspect ratio) so the "no upcoming events" state — two lines of copy — cannot
let the photo hang out of the section and over the contact band.

Verified at sixteen widths: no horizontal scroll despite the bleed (`html`
has `overflow-x: clip`), and the heading never touches the photo.

## The contact band, measured off the comp

Everything below was measured on the PDF rendered at 200dpi and converted to
artboard units (1366 wide), then compared against the build at 1366. Numbers
are comp -> build-before -> build-now.

### The block is ONE dense unit, not three paragraphs

Every line in the contact block — the CONTACT heading included — sits on the
same **45px rhythm with no paragraph separation anywhere**. Comp line tops:
2903, 2947, 2992, 3036, 3082, 3127, 3172, evenly spaced to within a pixel.
The email address runs straight into "Please note" with nothing between them.

The build had `margin-bottom: var(--space-m)` on the heading and
`margin-top: var(--space-m)` between paragraphs — 24px each, breaking the
block into three pieces and losing the dense typed-note quality. Both are
zeroed in `style.css`, and `--leading-contact` went 1.30 -> 1.36 so the
leading carries the block on its own (43px -> 45px at the comp's setting).

### The diving photo runs DOWN INTO the sage panel

Comp: the photo's bottom edge sits **41px below the panel's top edge** — they
overlap, and the eye reads them as one stack. This is why the panel is on
`--z-paper` and the photo on `--z-photo-back`.

Build before: the panel sat **143px below** the photo instead, opening a bare
strip across the full width of the page exactly where the comp is densest.
That gap was 96px of `.band--middle` bottom padding plus 36px of `.events`
min-height slack past the photo. Both trimmed, above 900px only — below that
the photo is back in the normal flow and that padding is the only thing
separating the two sections.

Now: 30px overlap at 1366, 45px at 1920. Below 900 the list outgrows the
photo and a normal 32–60px stacked gap takes over. Verified at eleven widths
that no width leaves a void.

### Positions corrected

| | comp | before | now |
|---|---|---|---|
| photo bottom below panel top | +41 | −143 | +30 |
| panel top above heading top | 153 | 134 | 154 |
| pink strip below panel top | 28 | 74 | 27 |
| pink scrap top above last line | 115 | 80 | 103 |
| contact copy left edge | 92 | 72 | 90 |
| line rhythm | 45.0 | 42.8 + 24px gaps | 44.8 |

The panel and strip nudges are `transform: translateY()` in **percent of the
element's own height**, never `top` in percent — a percentage in `top`
resolves against BAND height, which changes with the events list, and that is
how art hanging off a band's top edge ended up off-screen once already.

The contact copy is inset ~18px further than body copy (comp: body sets to
x74, contact to x92), which stops it hugging the torn left edge of the panel.

### One thing deliberately not matched

The comp's line breaks. The comp sets `"Ongoing"` in straight quotes; the
build uses `<cite>` italics, and the real EB Garamond metrics differ from the
comp's Garamond. Break points will land where they land — the measure is
right, which is what matters.

## Motion

Files: `css/motion.css`, `js/motion.js`. Both optional — delete the two tags
in `<head>` and the site ships static with nothing else changed.

### Two kinds of motion, driven two different ways

This split is the whole design of the file, and getting it wrong the first
time produced the one genuinely ugly bug in the build.

**Scroll-LINKED** — the collage parallax. Progress *is* the scroll position,
which is right, because a parallax layer is supposed to track scroll
continuously. Pure CSS scroll-driven animation, no JavaScript, compositor.
Chrome/Edge 115+, Safari 26+; Firefox gets the idle float without parallax.

**Scroll-TRIGGERED** — every text reveal. The element comes into view, then a
short animation plays on its own clock. IntersectionObserver, identically in
every browser.

Reveals were scroll-linked in the first pass, and the result is worth
understanding because it looks like a rendering fault rather than an
animation: every item in a list sits at a *different scroll progress at the
same instant*, so a seven-item list renders as a permanent ramp — solid black
at the top, nearly invisible at the bottom. No tuning of the range fixes it.
That IS what scroll-linking means. Text has to arrive at its own pace once
seen.

CSS has no widely-supported way to say "trigger on view, then play on time"
(`animation-trigger` is too new). Hence the observer. A useful side effect:
the Chrome/Firefox split disappears for reveals — every browser gets the
identical reveal, and only the decorative parallax differs.

### What moves

| Element | Motion | Trigger |
|---|---|---|
| `.wordmark` | brushed on left to right, 2.4s | page load, once |
| headings, list items, events, colophon | fade + 9px rise, 620ms | entering view |
| `.bio` / `.contact` blocks | line-by-line wipe, 1900ms | entering view |
| `.purchase` | scale + rotate settle, 800ms | entering view |
| `.deco__item`, `.events__photo` | parallax + idle float | scroll, and continuous |

Durations stay brisk on purpose: a drawn-out fade on a text block means the
reader is waiting to read something already in front of them. The easing is a
gentle S rather than a pure ease-out — an ease-out starts at full speed,
which on a fade reads as a snap followed by a long tail.

### The first screen is its own case

Everything above the fold arrives in the same tick, with no scrolling to
space it out, so the ordinary batch stagger runs the whole opening screen in
about a second. Measured on the first version: all three bio paragraphs
finished within 1100ms and were only 55ms apart, so they moved in near
lockstep — and the entire background story assembled itself while the
wordmark was still at 55% opacity. The name arrived last, which is backwards.

Anything revealed within 500ms of the script starting is therefore treated as
the page's *arrival* rather than as a reveal: held 420ms behind the
wordmark's opening stroke, spaced 210ms apart instead of 70ms, and marked
`.is-load` so the CSS gives it longer durations (`--dur-line-load`,
`--dur-wipe-load`). Now the paragraphs resolve at 1800 / 2100 / 2220ms and
the wordmark completes last at ~2400ms. On the first screen the page composes
itself; after that it gets out of the way.

### The wipe targets the BLOCK, not each paragraph

`.bio` and `.contact` each carry one mask, not one per `<p>`.

This is what makes the reveal an actual waterfall, and it was not the first
attempt. Masking each paragraph and staggering them does not work: with a
1500ms wipe and a 210ms stagger, all three bio paragraphs are mid-reveal at
the same moment, so what should read as a sequence reads as a single event
with soft edges. Widening the stagger enough to separate them would push the
opening screen past three seconds.

One mask over the whole block means one edge, travelling continuously from
the first line to the last and straight across the paragraph gaps. Nothing
overlaps because only one thing is ever animating. The stagger problem
disappears instead of being tuned.

Consequence worth knowing: the contact heading is deliberately absent from
the per-item reveal list, because it sits inside `.contact` and is covered by
that block's wipe — animating both parent and child would fade it twice. That
is why the heading selectors are `.work .section-heading` and
`.events .section-heading` rather than a bare `.section-heading`.

### Line-by-line without splitting the text

The wipe is a soft horizontal edge travelling down the block — a mask, not
per-line `<span>`s.

Splitting into spans is the usual technique and it is a bad trade here: line
boxes have to be recomputed on every resize and font swap, the wrappers land
in the middle of `<a>` and `<cite>` runs, and the DOM the screen reader gets
stops matching the DOM the author wrote. The mask changes no markup at all,
so selection, links, find-in-page and assistive technology behave exactly as
they would without it.

The mask is two element-heights tall, opaque across its top half; sliding it
from `0 100%` to `0 0` walks the edge down. **The feather is set in em, not
%** — about a line and a half deep whatever the element's height. A
percentage feather makes a short paragraph fade as one soft block and a long
one reveal in visible steps.

### The cascade is not a hardcoded delay

Scrolling at reading pace, items cross the trigger line one at a time and the
stagger comes free — adding a delay would only make each item feel late. But
a fast flick, an anchor jump, or a list already on screen at load fires
everything in one tick and the group pops as a block.

So `js/motion.js` treats items entering within 90ms of each other as one
batch and gives them an increasing delay; anything after a quiet gap starts
fresh at zero. Slow scrolling gets no delay, fast scrolling gets a cascade,
and neither case needs to know which it is.

### Scroll depth is a SEPARATE axis from window depth

`--depth` says how far a piece pulls toward the window edge as the window
widens. `--depth-y` says how much it moves on scroll. They started as one
token — "one idea, two axes" — and that was the reason the parallax read as
nothing at all.

The two are not asking the same question. "Is this welded to the edge of the
screen?" and "how deep in the stack is this?" have different answers, and
because nearly all the collage is edge-anchored, **twelve of the thirteen
pieces came out at `--depth-far`**. They all moved by exactly the same
amount. Parallax is only ever perceived as the DIFFERENCE between layers, so
a collage where everything moves identically reads as one flat plane
sliding — which is to say, as nothing.

`--depth-y` is set per piece by where it sits in the stack, and defaults to
`--depth` so a new piece still behaves sensibly if nobody sets one.

| piece | --depth-y | px per screen |
|---|---|---|
| frond, paint smear | 1.0 | 108 |
| paper-right | 0.85 | 101 |
| teal splatter | 0.8 | 86 |
| yellow strips | 0.7 | 76 |
| pink scrap | 0.9 | 66 |
| paper-left, paint-left | 0.5 | 60 |
| blue strip | 0.45 | 49 |
| **diving photo, sage panel, pink strip** | **0** | **0** |

### Two joins that must not come apart, and how they are held

**Same band — free.** Two pieces on the same band timeline with the same
`--depth-y` are locked to the pixel (measured swing: 0px). That is how the
frond and the paint smear stay welded, and the pink strip stays fixed to the
sage panel.

**Across a band boundary — pin both to zero.** The diving photo overlaps the
sage panel by design, but they sit in different bands and so run on different
timelines. At `--depth-far` the overlap swung from +30 at rest to −24…−45
under scroll: **the join came undone as you scrolled past it**, which is how
a designed overlap turns into a gap that cannot be reproduced standing still.
Matching their amplitudes is not enough — two `view()` timelines are at
different progress at the same scroll position, so equal travel still lands
on different offsets (measured: 51px of swing at matched 0.25). The only
stable answer for a relationship crossing a band boundary is for neither
piece to move. Backdrops that hold text are the right things to hold still
anyway.

`--depth-y: 0` for the photo is declared on the base rule, not inside the
`>=900` block: the first attempt scoped it to wide screens and below 900 the
photo quietly fell back to full depth and swung 242px against the panel.

### Rate is normalised per band

Art on a band timeline covers its whole travel across the band's PASS — the
band's height plus one viewport. A tall band spreads the same movement over
more scrolling and reads as slower. Measured at 1366: intro pass 1875, middle
2627, contact 1451, giving 48 / 35 / 45px per screen for identical settings —
the middle third of the page visibly lagging for no reason a reader could
name. `--drift-scale` per band divides that out, so a given `--depth-y` means
the same speed everywhere.

### All art in a band shares ONE timeline

`.band { view-timeline-name: --band }`, referenced by every layer inside.

A plain `view()` gives each element a timeline keyed to its own height and
position, so two pieces of art at the same `--depth` progress at different
rates: measured, the frond and the paint smear — same depth, touching in the
comp — drifted **52px apart**, reopening exactly the gap that took several
passes to design out. With a shared band timeline, relative movement comes
only from the `--depth` ratio, and same-depth art is locked (measured 0.1px).

The cost is that a tall band spreads the same travel over more scroll, which
is why `--drift-max` is as high as it is: at 3.25rem the far layers move 40px
per screen in the intro band, 67px in the taller middle band.

### Parallax and float share one property

Both write to `translate`, summed with `animation-composition: add`. Without
that keyword the float silently overwrites the parallax and the scroll effect
disappears with no error. `translate` rather than `transform` because
`.d-frond` and `.d-strip-yellow-top` carry tuned `transform` offsets that must
survive; same reason `.purchase` uses `scale`/`rotate`, since it already uses
`transform` on hover.

Each layer floats on a different period with a negative phase — unison reads
as a throb rather than as things hanging in air. Period and phase are custom
properties, not literal `animation-delay` values, because the two paths
declare different numbers of animations and a literal list would land on the
wrong animation.

### The safety rule

Nothing is hidden by a static rule. Every hidden state lives inside a
`@keyframes` block, and the reveal keyframes only run under `html.js-motion`,
which the script sets last, after every check has passed. Script blocked,
failed, or stripped by a proxy → the page renders complete and static. Do not
add `opacity: 0` outside a keyframe.

### Bugs found by testing

Most are the same shape — *an animation that starts but can never finish* —
and none throws an error anywhere.

1. **Scroll-linked text reveals render a list as a permanent fade ramp** (see
   above). The fix was architectural, not a tuning change.
2. **`animation-range: entry X% cover Y%` cannot complete for the last
   elements on the page** — the page stops scrolling first. The colophon sat
   at 0.29 opacity permanently, at every width. Moot now that reveals are
   triggered rather than linked, but it is why the foot padding briefly grew
   to 160px; that has been reverted.
3. **An asymmetric easing curve made a 1.1s animation read as a 300ms flash.**
   Fast-out/slow-settle spends most of its duration creeping through the last
   sliver: at 350ms it was already 86% done. Display sweeps want a
   near-linear middle — `--ease-brush`.
4. **A mask clips to the element box, and `text-box: trim-both` shrinks that
   box to cap height.** Measured on a heading: box 27.8px, glyph ink 33px
   starting 5.2px *above* it. The mask guillotined the tops off every letter.
   Size mask headroom in em, not %.
5. **`.js-motion .work__list > li` outranks `.js-motion .is-in`** — two
   classes plus an element beats two classes — so `paused` beat `running` and
   most of the page stayed invisible. Everything with a plain one-class
   selector worked, which is what let it look fine at a glance. `:where()`
   zeroes the specificity.
6. **A negative bottom `rootMargin` strands the last element on the page**
   (it can never leave the excluded band), and **items inside a closed
   `<details>` never fire an observer** — past appearances would have opened
   to an invisible list. `rootMargin: '0px'`, plus a `toggle` listener.

And two that are not bugs but look like them:

**`--drift-max` was 20px in the first pass**, then 52px in the second. Across
a 3300px page the first is imperceptible; the second measured at a plausible
35–48px per screen and still read as nothing, because every piece was moving
by the same amount. Amplitude was never the problem — differential was.
Tests prove motion runs, not that it reads.

### Reduced motion

The blanket rule in `style.css` is not sufficient. A scroll-driven animation
takes progress from scroll position, so `animation-duration: 0.01ms` does
nothing to it; and the idle float is infinite, so collapsing its duration
just parks it wherever it was. `motion.css` removes the timeline and the
animation outright, and `js/motion.js` exits before setting `.js-motion` so
the reveal rules never match either.

### Contrast had to be re-audited

The original harness measured one static render, which stopped being
sufficient once art started travelling up to 100px relative to the text.
`tools/audit_scroll.py` walks each width down the page and measures every
text line against the art actually behind it at that scroll position.

### The reveal test has to check masks, not just opacity

`tools/motion_test.py` originally asserted on opacity alone. Masked text still
reports opacity 1, so a wipe stuck part-way would have hidden half a paragraph
and passed silently. It now asserts on mask-position too — and axis-aware,
because the wordmark sweeps horizontally and rests at `0% center`, so reading
its y component returns 50% and looks like a failure.

## Verified

Re-run after any layout or motion change:

```
python3 tools/audit_scroll.py      # contrast, at every scroll position
python3 tools/motion_test.py       # no text can be stranded invisible
```

- No horizontal scroll at 320 / 390 / 566 / 768 / 900 / 1100 / 1366 / 1600 / 1920 / 2560,
  at every scroll position, with parallax running.
- Zero unlayered `.deco__item` (an unlayered item means a swallowed
  declaration — see "A CSS trap that bit twice").
- Worst text-on-art contrast **5.72:1**, measured with the collage in motion
  at every scroll position, against WCAG AA's 4.5:1.
- No text ever rests part-faded: every reveal resolves to full opacity, and
  no text on screen sits at partial opacity once scrolling stops. This is the
  regression test for the fade-ramp artefact — see "Motion".
- Motion suite passes on both delivery paths, with JavaScript blocked, with
  reduced motion on, and with the past-appearances disclosure open and
  closed. Nothing is left below full opacity in any combination.

## Images

All 15 collage elements converted PNG → WebP at q82.
**13.28 MB → 1.78 MB (87% smaller)**, transparency preserved.
Exported at 2× and displayed at 1×, so they stay sharp on retina screens.
Ship `assets/images/*.webp`; keep `2x/` as archival source.

Every collage image sits in a single `aria-hidden` container with empty
`alt` attributes — it is decoration, and screen readers should skip it.
`width`/`height` are set on each so the browser reserves space and the
page doesn't jump as images load.

## Typography — two open issues

**1. Black-Paint (display face) — RESOLVED, using a traced webfont.**
The supplied 40 MB OTF is a *bitmap* colour font: letterforms live in the
`sbix` and `SVG ` tables as embedded PNGs, and the `glyf` outlines are empty.
Chrome and Edge support neither table, so it cannot be used as a webfont even
with a web licence in hand.

`tools/trace_font.py` extracts those bitmaps, traces them with potrace, and
rebuilds a CFF outline font that keeps the original advance widths. Output:

| file | size | notes |
|---|---|---|
| `black-paint-web.woff2` | **105 KB** | in use — faithful trace |
| `black-paint-web-balanced.woff2` | 78 KB | smoother contours, alternate |

Optical weight matches the source bitmaps within **1.5%** (measured as ink
area at matched size). What tracing loses is the grey brush grain — but the
comp never sets this face above 48px, and at 48px and below the grain is not
visible. See `docs/original-vs-traced-real-sizes.png`.

Because it's a real font, every heading in `index.html` is live text:
selectable, searchable, screen-reader native, CMS-editable, and resolution
independent at any size. No heading images, no `@2x` variants, no rebuild
step when copy changes.

*Note:* `trace_font.py` needs `potrace`, `fonttools`, `pillow` and
`svgelements`. It's a one-off build tool — the WOFF2 is the deliverable.

*Superseded:* `assets/images/headings/` and `tools/build_headings.sh` render
headings as images instead. Kept as a fallback in case the traced outlines
are ever judged too far from the artwork; not referenced by the site.

Licence flag: the web licence is purchased, but deriving a new font file from
the supplied OTF may be restricted by Handmadefont's EULA. **Ask them for a
web-format file first** — and if they have none, confirm in writing that
generating one is permitted.

**2. Apple Garamond (body face) cannot be licensed for web use.**
It is Apple proprietary. `tokens.css` currently substitutes **EB Garamond**
(SIL Open Font License, free), loaded from Google Fonts as a placeholder.
Swap in a licensed Garamond if the client buys one — it is a one-line
change in `--font-body`.

## Accessibility notes

Contrast measured against the `#F2F1E7` ground:

| Combination                    | Comp     | Result           |
|--------------------------------|----------|------------------|
| Body text, black on ground     | 18.5:1   | passes AA        |
| Links, `#FF00FF` on ground     | 2.76:1   | **fails AA**     |
| "HERE" `#FF00FF` on green blob | 1.72:1   | **fails AA**     |

`--c-link` is set to `#C100C1` — same hue, darkened to **4.58:1**, which
passes AA. The original comp value is preserved as `--c-link-comp` for
reference. The "HERE" label is set in black (11.5:1) since no magenta dark
enough to pass would still read as magenta on that green.

Also in place: skip link, visible focus rings, `prefers-reduced-motion`
support, landmark regions, and a single `h1` with `h2` section headings.

## Open items

- [ ] Destination URLs for all 7 published-work links
- [ ] Destination URLs for "agricultural activist" / "creative director"
- [ ] Purchase link for *Small Hot Rooms*
- [ ] Real content for Events + Appearances (comp shows 8 empty bullets)
- [ ] Confirm Black-Paint web licence
- [ ] Decide body typeface (EB Garamond substitute vs. licensed Garamond)
- [ ] Destination URLs for the 5 upcoming event titles
- [ ] Verify the last 2 eyeballed collage coordinates (`strip-yellow-top`,
      `frond-right`) against the .ai file
- [ ] Decide whether to cap mid/near depth drift past ~1920 — the collage
      thins out on very wide monitors
