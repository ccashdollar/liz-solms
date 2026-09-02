# Handoff — Liz Solms

A static, dependency-free one-page site, built to be dropped into a CMS.
No build step, no framework, no package manager. Open `index.html` and it
runs.

This note covers the four things that are not obvious from reading the code:
**what you must swap**, **what the server has to do**, **what the CMS must
render**, and **what to check once it is live**. Everything else is explained
in comments at the point where it matters — the CSS is heavily annotated on
purpose, and it compresses away to nothing (127 KB of source becomes 42 KB
gzipped).

---

## 1. What you must swap

### `{{SITE_URL}}` — 18 occurrences, 3 files

One find-and-replace with the live origin, **no trailing slash**:

| file | count |
|---|---|
| `index.html` | 15 |
| `robots.txt` | 2 |
| `sitemap.xml` | 1 |

`https://lizsolms.com`, not `https://lizsolms.com/`. The token is always
followed by an explicit `/` where a path is needed, so a trailing slash
produces `//` in the canonical, the Open Graph URL, and every JSON-LD `@id`.

Also set `<lastmod>` in `sitemap.xml` to the launch date.

### 15 placeholder `href="#"` links

Search `index.html` for `href="#"`. Each sits under a `TODO` comment saying
what it needs:

- **2 in the bio** — "agricultural activist" and "creative director". Liz to
  confirm destinations.
- **1 on the purchase CTA** — the bookseller or publisher page for
  *Small Hot Rooms*.
- **7 in the published-work list** — the live URL for each piece.
- **5 in the events list** — an event page each, where one exists.

An event with no page is **not** a broken link: replace the `<a>` with a
`<span class="events__name">` and it renders identically minus the link
colour. The past-appearances list already does this — copy that pattern.

### 2 JSON-LD fields left out on purpose

Both are in an HTML comment directly above the `<script type="application/ld+json">`
block, ready to paste. They were omitted rather than stubbed because an
invalid ISBN or a fake URL is a *structured-data error*, which is worse than
an absent field:

- **`isbn`** on the `Book` node — once Serving House Press supplies it.
- **`sameAs`** on the `Person` node — Liz's real profiles elsewhere. This one
  earns its keep: `sameAs` is what tells search engines and answer engines
  that this page and her other profiles are the same person, and it does more
  for entity confidence than anything else in the file.

### Before you ship

Delete `demo/` — a hover-state comparison page, `noindex`ed but not part of
the site. `docs/` and `tools/` are working evidence and build scripts; keep
or drop as you prefer, they are not referenced by the page.

---

## 2. What the server has to do

Nothing exotic. In rough order of how much it matters:

**Compression.** Serve `.css`, `.js`, `.html`, `.xml` and `.svg` gzipped or
brotlied. The CSS is verbosely commented by design; 127 KB of source is 42 KB
gzipped. Do not strip the comments to save bytes — compression already does
it, and the comments are the documentation.

**Cache headers.** Fingerprint or long-cache the immutable assets and keep
the HTML short:

```
/assets/fonts/*     Cache-Control: public, max-age=31536000, immutable
/assets/images/*    Cache-Control: public, max-age=31536000, immutable
/css/*  /js/*       Cache-Control: public, max-age=31536000, immutable  (fingerprint these, or drop to ~1h)
/index.html         Cache-Control: public, max-age=300, must-revalidate
```

`.woff2` must be served as `font/woff2`. If the fonts ever move to a
different origin, they need CORS — same-origin as now, they do not.

**HTTPS**, HSTS, and one canonical host. Pick www or apex and 301 the other
to it. The `<link rel="canonical">` must agree with whichever you pick, or
you will split ranking signals between two URLs.

**404 rule.** `404.html` is built. Point the server's not-found handler at
it and make sure it returns a real **`404` status**, not a `200` — a "soft
404" that answers 200 gets the missing URL indexed as a real page.

Two things about that file specifically:

- **It has a `<base href="/">`, and that is load-bearing.** A 404 is served
  for *any* missing path, including deep ones like `/readings/2027/spring`.
  A browser resolves relative URLs against the *requested* path, so without
  the base tag its CSS would be looked for at `/readings/2027/css/…` and the
  page would arrive unstyled. If the site is ever served from a
  subdirectory, change that **one attribute** (e.g. `href="/liz-solms/"`)
  and every path in the file follows. This is also why the 404 looks
  unstyled on a GitHub Pages *project* URL — that is the base tag doing
  exactly what it should, not a bug.
- It loads `tokens.css`, `style.css` and `motion.css` but **not**
  `layout.css`, which positions the collage inside the main page's three
  content bands. The two decorative pieces here are placed by a small
  `<style>` block in the file.

**`robots.txt` and `sitemap.xml`** must be served from the origin root.

**No trailing-slash surprises.** `/` should serve `index.html` directly.

---

## 3. What the CMS must render

The page is one document with four editable regions. Nothing here needs a
component library — it needs the CMS to emit this exact markup.

### Bio — `.bio`

Three `<p>` elements of prose. Inline `<a>` and `<cite>` are expected and
styled. **Do not wrap paragraphs in extra divs**: the reveal animation puts a
single mask over the whole `.bio` block so the text wipes in line by line
across the paragraph gaps. An extra wrapper breaks that into pieces.

### Published work — `.work__list`

```html
<li>
  <span class="work__title">Last Day on Earth</span> &ndash;
  <a class="work__outlet" href="…">Reed Magazine</a>
</li>
```

Title is a `<span>`, outlet is the link. Keep them in that order; the en dash
is content, not CSS.

### Events — `.events__list`

```html
<li class="events__item">
  <time class="events__date" datetime="2026-11-12">12 November 2026</time>
  <a class="events__name" href="…">Small Hot Rooms launch reading</a>
  <span class="events__venue">Serving House Press &middot; Philadelphia</span>
</li>
```

Three rules that matter:

1. **`<time datetime>` is required** — it is the machine-readable value to
   sort on and the one search engines read. The human text beside it can be
   formatted however Liz likes.
2. **The link goes on the event NAME, never the whole row.** The name is the
   phrase that describes the destination, and it is what a screen reader
   reads out of a link list. "12 November 2026 Small Hot Rooms launch reading
   Serving House Press · Philadelphia" as one link is unusable.
3. **No page? Use `<span class="events__name">`** instead of the `<a>`. Same
   element, same size, just no link colour.

**Three states, all three already built, and the switch is one class.**
Both the list and the empty state ship in the file so you can see both. The
CSS decides which is visible:

| state | what the CMS does |
|---|---|
| upcoming events | nothing — this is the default |
| nothing scheduled | add `class="events events--empty"` to the `<section>`. `.events__list` hides, `.events__empty` shows. |
| past appearances | leave `.events__past` in place; omit the whole `<details>` if there is no history yet |

So the empty state needs no template branch — one class on the section, and
the two rules in `style.css` do the rest. Past appearances survive both
states, which is the point: the page still has substance between engagements.

The empty state is not an apology, it points at the zine. Keep that.

`.events__past` is a real `<details>` — keyboard accessible, announced
correctly by screen readers, no JavaScript. **Do not replace it with a
scripted accordion.**

### Contact — `.contact`

Prose plus the email link. Same "no extra wrappers" rule as the bio, for the
same reason.

**One decision for Liz, not for you:** her email address currently sits in
plain HTML in a `mailto:`, which scrapers harvest. If she would rather not,
the options are a contact form (needs a backend) or obfuscation (degrades for
some assistive tech). Ask her before changing it.

---

## 4. Things that will look like bugs and are not

**Firefox shows no collage parallax.** The layered art drifts on scroll in
Chrome, Edge and Safari 26+ via CSS scroll-driven animation
(`animation-timeline: view()`), which Firefox has not shipped. There is a
`@supports` guard: Firefox gets a static collage. Nothing is hidden by the
animation, so there is nothing to fall back to. **The text reveals run
identically in every browser** — those are IntersectionObserver, not scroll
timelines.

**Nothing floats when the page is idle.** Deliberate, and reverted from an
earlier build. The collage moves only while the reader scrolls.

**Underlines are backgrounds, not `text-decoration`.** A repeating CSS
gradient shifted by exactly one pitch on a loop, parked at rest, running on
hover. Five `--rule-*` tokens in `tokens.css` control it. `--rule-pitch` is
used **twice** — as the `background-size` and as the keyframe distance — and
if they ever disagree the dashes visibly jump once per cycle. Change the
token, not the two places.

**`.events__item` is block flow, not grid, on purpose.** Grid blockifies its
children, which made the event-title link stretch to the full column and drag
its underline with it. Do not "tidy" it back into a grid.

**JavaScript is progressive enhancement only.** `js/motion.js` adds
`html.js-motion` after checking the browser can do the reveals and the reader
has not asked for reduced motion. Script blocked, failed, or stripped → the
page renders complete and static. Nothing is ever hidden by a rule outside a
`@keyframes` block. Please keep that invariant if you touch the motion.

**`prefers-reduced-motion` is handled explicitly**, not just by collapsing
animation durations — that does nothing to a scroll-driven animation and
parks an infinite one at a random phase.

**Fonts are self-hosted and the page makes zero external requests.** Both
faces are in `assets/fonts/`. `EB-Garamond-OFL.txt` is the SIL Open Font
License — the licence requires it to travel with the font, so **do not delete
it**. The display face is a traced webfont built by `tools/trace_font.py`
from a licensed bitmap OTF; the licence is Creative Market's web font licence,
which permits self-hosting. Check whether it carries a pageview cap before a
big launch.

---

## 5. After deploy

In order:

1. **Confirm zero external requests.** Open DevTools → Network, filter by
   domain. Everything should be same-origin. If something third-party
   appears, it was added after handoff.
2. **Validate the structured data** at `validator.schema.org` and Google's
   Rich Results Test. Expect `Person`, `Book` and `WebSite`, linked by `@id`.
   If you added the ISBN or `sameAs`, this is where a typo shows up.
3. **Force a share-card re-scrape.** Facebook Sharing Debugger, LinkedIn Post
   Inspector, X Card Validator. **Do this before anyone shares the link** —
   scrapers cache the first fetch hard, and a card fetched while the OG image
   was still 404ing can persist for days. The image is `1200×630`, RGB JPEG.
   Known and accepted: Liz's face falls outside the centre-safe square, so
   apps that crop square lose her.
4. **Lighthouse on the real host**, not locally. The numbers that will move
   are all server-side: compression, cache headers, and TLS.
5. **Check the favicon in a real tab strip.** `/favicon.ico` is multi-res
   (16 + 32 + 48). At 16px the LS monogram reads as a book silhouette rather
   than two letters — that is the intended and verified result.
6. **Test on a real phone**, not just a narrow window. Touch has no hover, so
   the link rule sits still — correct, and the resting dashes are the link
   affordance.

### Current weight

| | requests | transferred |
|---|---|---|
| desktop 1366 | 24 | ~906 KB |
| phone 390 | 22 | ~574 KB |

Images dominate (631 KB / 299 KB); the phone number is lower because the
`srcset` ladder is doing its job. Fonts are 150 KB, of which 102 KB is the
display face. CSS and HTML are 116 KB raw and 41 KB gzipped — enable
compression and they stop mattering.

---

## 6. Verification tooling

`tools/` holds the scripts used to check this build. They need Playwright and
Pillow, and they expect the site served over http (not `file://`, which
blocks font loading):

- `audit_scroll.py` — measures text contrast against the art actually behind
  it, at every scroll position and eight widths. Necessary because the
  collage moves: passing at scroll 0 does not prove passing at scroll 1200.
  Current worst case is 5.47:1 against a 4.5:1 requirement.
- `motion_test.py` — proves nothing is ever stranded mid-animation, in any
  combination of JS availability, reduced motion, viewport and scroll state.

Both are worth re-running if you change layout or colour.

---

## Open items not in your scope

**Liz owes:** the AI-crawler decision (`robots.txt` currently allows them by
omission, with a commented block to reverse it — her call, not a default),
whether to run analytics, whether her email stays in plain HTML, a proofread
of her own bio, the `sameAs` URLs, and the book's ISBN.

**Still unbuilt:** nothing.

Design questions go to Chris. Anything about why something is the way it is
is probably answered in a comment at that line — the CSS explains its own
reasoning, including the things that were tried and abandoned.
