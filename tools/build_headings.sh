#!/usr/bin/env bash
# Regenerate every Black-Paint heading image.
# Run from site/tools/ after changing any heading text.
set -euo pipefail
cd "$(dirname "$0")"
OUT=../assets/images/headings
P="python3 compose_heading.py"

$P "LIZ"                                 --size 48 --out $OUT/wordmark-liz.webp
$P "SOLMS"                               --size 48 --out $OUT/wordmark-solms.webp
$P "PURCHASE"                            --size 17 --out $OUT/h-purchase.webp
$P "SMALL HOT ROOMS"                     --size 30 --out $OUT/h-small-hot-rooms.webp
$P "HERE"                                --size 15 --out $OUT/h-here.webp
$P "SELECTED PUBLISHED WORK AND REVIEWS" --size 22 --out $OUT/h-selected-work.webp
$P "EVENTS +APPEARANCES"                 --size 22 --out $OUT/h-events.webp
$P "CONTACT"                             --size 20 --out $OUT/h-contact.webp

echo
echo "Total: $(du -ch $OUT/*.webp | tail -1 | cut -f1)"
