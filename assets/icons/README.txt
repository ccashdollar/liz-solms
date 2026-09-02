ICONS — all generated, nothing outstanding.

Source of truth: icon.svg (vector, exported from Figma).
Everything else was derived from the 512px raster at LANCZOS.

  /favicon.ico              at the SITE ROOT, not here. Multi-resolution:
                            16, 32 and 48px in one file, so each client
                            picks its own. Browsers and crawlers request
                            /favicon.ico blind, without reading the HTML.

  icon.svg                  primary icon on modern browsers, any size
  apple-touch-icon.png      180x180, opaque (iOS composites alpha to black)
  icon-192.png              web manifest
  icon-512.png              web manifest

The mark is a full-bleed opaque square with no transparency, which is
correct: iOS and Android apply their own corner masks, so the artwork
should not round its own corners.

To regenerate the rasters after editing icon.svg, export a 512x512 PNG
and resize down with LANCZOS. Do not scale up from a small size.
