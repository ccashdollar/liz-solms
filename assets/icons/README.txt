ICON EXPORTS NEEDED
===================

Design the mark first and judge it at 16px, not on the artboard. A brush
letterform can silt into an unreadable blob at favicon size.

Files, and where each is referenced:

  /favicon.ico                        32x32.  Stays at the SITE ROOT, not
                                      here — browsers and crawlers request
                                      /favicon.ico blind, without reading
                                      the HTML.

  assets/icons/icon.svg               Primary icon on modern browsers.
                                      Scales to any size.

  assets/icons/apple-touch-icon.png   180x180, on an OPAQUE background.
                                      iOS composites transparency to black.

  assets/icons/icon-192.png           192x192, for site.webmanifest
  assets/icons/icon-512.png           512x512, for site.webmanifest

Optional polish: a 512x512 "maskable" version with the mark inside the
middle 80%, since Android crops icons to circles, squircles and rounded
squares depending on the launcher.

Until these exist the browser console will show 404s for them. That is
expected, and deliberately not papered over with placeholders — a
placeholder icon is exactly the kind of thing that ships by accident.
