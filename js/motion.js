/* ==========================================================================
   motion.js — the reveal engine
   ==========================================================================

   WHY THIS IS JAVASCRIPT AND THE PARALLAX IS NOT

   The collage parallax in css/motion.css is scroll-LINKED: its progress is
   the scroll position, which is exactly right, because a parallax layer is
   supposed to track the scroll continuously.

   Text reveals are the opposite. They want to be scroll-TRIGGERED: the
   element comes into view, and then a short animation plays on its own
   clock. Driving them from scroll position instead produces a specific and
   very visible artefact — every item in a list sits at a different scroll
   progress at the same moment, so a seven-item list renders as a permanent
   ramp from black at the top to nearly invisible at the bottom. It looks
   like broken text, not like an animation, and no amount of tuning the
   range fixes it, because it is what scroll-linking means.

   CSS has no widely-supported way to say "trigger on view, then play on
   time" — `animation-trigger` is too new to rely on. So the reveals use
   IntersectionObserver in every browser, and the CSS animations they start
   are ordinary time-based ones. As a side effect the Chrome/Firefox split
   disappears for reveals: every browser now gets the identical reveal, and
   only the decorative parallax differs.

   THE ONE RULE
   This script may only ever ADD motion. It must never be the thing that
   makes content visible, because then a script error becomes a blank page.
   Nothing in motion.css hides anything until .js-motion is set, and
   .js-motion is set only after every check below has passed. So:

     script blocked, fails, or never loads  ->  page renders complete, static
     script runs                            ->  page renders complete, animated

   IT IS SAFE TO DELETE THIS FILE. Removing it and its <script> tag costs
   every browser the text reveals, leaves the collage parallax running, and
   changes nothing else.
   ========================================================================== */

(function () {
  'use strict';

  // ---- Gate 1: has the reader asked for less motion? ---------------------
  // motion.css honours this too, but checking here means we never build the
  // observer at all. Cheaper, and one less thing to go wrong.
  var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (calm && calm.matches) return;

  // ---- Gate 2: the API this needs ----------------------------------------
  if (!('IntersectionObserver' in window)) return;

  // Mirrors the selector list in css/motion.css section 4.
  // KEEP THESE TWO LISTS IN STEP. A selector here with no rule there does
  // nothing; a rule there with no selector here would leave an element
  // paused at frame zero, which is the one way this file could hide content.
  // Prose blocks are targeted as WHOLE BLOCKS (.bio, .contact) rather than
  // paragraph by paragraph. One mask travelling down a block is a genuine
  // waterfall; three staggered paragraph masks are not, because at any
  // sensible duration they all animate at once.
  //
  // The contact heading is inside .contact and so is covered by that block —
  // which is why the heading selectors here are scoped to .work and .events
  // rather than being a bare .section-heading.
  var SELECTOR = [
    '.work .section-heading',
    '.events .section-heading',
    '.bio',
    '.work__list > li',
    '.events__item',
    '.events__empty',
    '.events__past',
    '.contact',
    '.colophon',
    '.purchase'
  ].join(',');

  var targets = document.querySelectorAll(SELECTOR);
  if (!targets.length) return;

  // Only now, with everything confirmed, do we let the CSS hold elements at
  // frame zero. Every early return above leaves the page fully visible.
  document.documentElement.classList.add('js-motion');

  // ---- The cascade -------------------------------------------------------
  // When you scroll at reading pace, items cross the trigger line one at a
  // time and the stagger comes free from the scrolling itself — no delay
  // needed, and adding one would only make each item feel late.
  //
  // But when a whole group arrives at once — a fast flick, a jump to an
  // anchor, or simply a list that is already on screen when the page loads —
  // every item fires in the same tick and the group pops as one block. That
  // reads as a flash rather than a reveal.
  //
  // So: items entering within GAP of each other are treated as one batch and
  // given an increasing delay; anything after a quiet gap starts fresh at
  // zero. Slow scrolling gets no delay, fast scrolling gets a cascade, and
  // neither case needs to know which it is.
  //
  // THE FIRST SCREEN IS ITS OWN CASE, and it is the one that has to be
  // handled separately rather than tuned. Everything above the fold arrives
  // in the same tick with no scrolling to space it out, so the ordinary
  // batch stagger runs the whole opening screen in about a second: measured
  // on the original values, all three bio paragraphs finished within 1100ms,
  // only 55ms apart, while the wordmark was still at 55% opacity. The
  // background story assembled itself before the name did.
  //
  // Anything revealed inside LOAD_WINDOW of the script starting is therefore
  // treated as the page's arrival rather than as a reveal: held back behind
  // the wordmark's opening stroke, spaced roughly three times further apart,
  // and marked .is-load so the CSS can give it longer durations too.
  var STEP = 70;        // ms between items in an ordinary batch
  var GAP  = 90;        // ms of quiet that ends a batch
  var MAX  = 8;         // cap, so a long list never delays its tail absurdly

  var LOAD_WINDOW = 500;   // ms after start that still counts as "on load"
  var LOAD_LEAD   = 420;   // ms to let the wordmark get under way first
  var LOAD_STEP   = 210;   // ms between blocks on the first screen
  var LOAD_MAX    = 5;

  var t0   = performance.now();
  var last = -1e9;
  var n    = 0;
  var loadN = -1;

  function reveal(el) {
    var now = performance.now();

    if (now - t0 < LOAD_WINDOW) {
      loadN += 1;
      el.classList.add('is-load');
      el.style.animationDelay = (LOAD_LEAD + Math.min(loadN, LOAD_MAX) * LOAD_STEP) + 'ms';
    } else {
      n = (now - last < GAP) ? Math.min(n + 1, MAX) : 0;
      if (n) el.style.animationDelay = (n * STEP) + 'ms';
    }

    last = now;
    el.classList.add('is-in');
  }

  var observer = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (!entries[i].isIntersecting) continue;
      reveal(entries[i].target);
      // Reveals happen once. Unobserving as we go keeps the callback short
      // and means scrolling back up does not replay anything.
      observer.unobserve(entries[i].target);
    }
  }, {
    // rootMargin and threshold are deliberately zero.
    //
    // The tempting setting is a negative bottom margin — '0px 0px -12% 0px'
    // — so the reveal starts a little after the element crosses the edge.
    // It also silently strands the last thing on the page: the colophon sits
    // inside that excluded band at the bottom of the document and can never
    // scroll out of it, so it never intersects and stays hidden for good.
    //
    // A non-zero threshold has the mirror problem: an element taller than
    // the viewport may never reach it.
    //
    // Zero and zero has no such edge case. Any pixel entering counts.
    rootMargin: '0px',
    threshold: 0
  });

  for (var i = 0; i < targets.length; i++) observer.observe(targets[i]);

  // ---- Closed <details> --------------------------------------------------
  // Past appearances live inside a closed <details>. Its contents are not
  // rendered, so IntersectionObserver never fires for them — the disclosure
  // would open onto a list of invisible events with nothing left to trigger
  // them. Opening it is the trigger.
  var discs = document.querySelectorAll('details');
  for (var d = 0; d < discs.length; d++) {
    discs[d].addEventListener('toggle', function () {
      if (!this.open) return;
      var inner = this.querySelectorAll(SELECTOR);
      for (var k = 0; k < inner.length; k++) {
        reveal(inner[k]);
        observer.unobserve(inner[k]);
      }
    });
  }
})();
