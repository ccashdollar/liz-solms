#!/usr/bin/env python3
"""
compose_heading.py — render a heading in Black-Paint as a WebP image.

WHY THIS EXISTS
---------------
Black-Paint is a bitmap colour font: its letterforms live in the OpenType
`sbix` table as embedded PNGs, and its vector outlines are empty. Chrome and
Edge cannot render it at all, so it can't be used as a webfont.

This script pulls the bitmaps straight out of the font and composites them
using the font's OWN metrics (advance widths from `hmtx`), so spacing matches
what you'd get from real typesetting. Laying the loose PNG letterforms side by
side does NOT work — each one sits on an identical 2480x2713 canvas with no
advance-width information, so narrow letters float in a sea of whitespace.

USAGE
-----
    python3 compose_heading.py "SMALL HOT ROOMS" --size 30 --out ../assets/images/headings/h-small-hot-rooms.webp

    --size      display size in CSS px (the script renders at 2x for retina)
    --tracking  letter-spacing in em (default 0.05)
    --colour    hex fill, e.g. "#000000" (default: keep original brush colour)

Requires:  pip install fonttools pillow
"""

import argparse, io, math, os, sys
from fontTools.ttLib import TTFont
from PIL import Image

FONT = os.path.join(os.path.dirname(__file__),
                    "..", "..", "Black Paint Font", "OTF Font", "Black-Paint.otf")


class BlackPaint:
    def __init__(self, path=FONT):
        self.f = TTFont(path)
        self.cmap = self.f.getBestCmap()
        self.hmtx = self.f["hmtx"]
        self.upem = self.f["head"].unitsPerEm
        self.strike = list(self.f["sbix"].strikes.values())[0]
        self.scale = self.strike.ppem / self.upem
        self._cache = {}

    def bitmap(self, glyph):
        if glyph not in self._cache:
            g = self.strike.glyphs.get(glyph)
            self._cache[glyph] = (
                Image.open(io.BytesIO(g.imageData)).convert("RGBA")
                if g and g.imageData else None
            )
        return self._cache[glyph]

    def render(self, text, size, tracking=0.05, pad=6, colour=None):
        k = size / self.upem
        width = 0.0
        height = 0.0
        for ch in text:
            g = self.cmap.get(ord(ch))
            if not g:
                sys.stderr.write(f"warning: no glyph for {ch!r}\n")
                continue
            width += self.hmtx[g][0] * k + tracking * size
            bm = self.bitmap(g)
            if bm:
                height = max(height, bm.size[1] / self.scale * k)

        img = Image.new("RGBA",
                        (math.ceil(width) + pad * 2, math.ceil(height) + pad * 2),
                        (0, 0, 0, 0))
        pen = float(pad)
        baseline = pad + height

        for ch in text:
            g = self.cmap.get(ord(ch))
            if not g:
                continue
            bm = self.bitmap(g)
            if bm:
                w = max(1, round(bm.size[0] / self.scale * k))
                h = max(1, round(bm.size[1] / self.scale * k))
                glyph = self.strike.glyphs[g]
                ox = glyph.originOffsetX / self.scale * k
                oy = glyph.originOffsetY / self.scale * k
                tile = bm.resize((w, h), Image.LANCZOS)
                if colour:
                    solid = Image.new("RGBA", tile.size, colour)
                    solid.putalpha(tile.getchannel("A"))
                    tile = solid
                img.alpha_composite(tile, (round(pen + ox), round(baseline - h - oy)))
            pen += self.hmtx[g][0] * k + tracking * size

        return img


def main():
    ap = argparse.ArgumentParser(description="Render a Black-Paint heading to WebP.")
    ap.add_argument("text")
    ap.add_argument("--size", type=float, default=24, help="display size in CSS px")
    ap.add_argument("--tracking", type=float, default=0.05, help="letter-spacing in em")
    ap.add_argument("--colour", default=None, help="hex fill, e.g. #000000")
    ap.add_argument("--scale", type=int, default=2, help="pixel density (default 2 = retina)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    img = BlackPaint().render(a.text, a.size * a.scale,
                              tracking=a.tracking, colour=a.colour)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    img.save(a.out, "WEBP", quality=88, method=6)
    print(f"{a.out}  {img.size[0]}x{img.size[1]}  "
          f"{os.path.getsize(a.out)/1024:.1f}K   (displays at {a.size}px)")


if __name__ == "__main__":
    main()
