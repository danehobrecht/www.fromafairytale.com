#!/usr/bin/env python3
"""Regenerate responsive image variants for the site.

Sources live in _originals/ (GitHub Pages' default Jekyll build skips
underscore-prefixed folders, so they are not published). Output goes to
assets/images/:  <name>.webp (largest, max 1600w) and <name>-<w>w.webp.
Also writes og-image.jpg (1200x630) from hero-image.

Usage: python3 scripts/optimize-images.py      (requires Pillow)
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "_originals", ROOT / "assets" / "images"
NAMES = ["hero-image", "our-story", "gallery-002", "gallery-003", "gallery-004", "gallery-005"]
WIDTHS, MAX_W, QUALITY = [480, 800, 1200, 1600], 1600, 80

def save(img, path, **kw):
    img.save(path, **kw)
    print(f"{path.relative_to(ROOT)}  {img.width}x{img.height}  {path.stat().st_size // 1024} KB")

for name in NAMES:
    im = ImageOps.exif_transpose(Image.open(SRC / f"{name}.webp")).convert("RGB")
    widths = sorted({w for w in WIDTHS if w < im.width} | {min(im.width, MAX_W)})
    for w in widths:
        h = round(im.height * w / im.width)
        resized = im.resize((w, h), Image.LANCZOS)
        save(resized, OUT / f"{name}-{w}w.webp", quality=QUALITY, method=6)
        if w == widths[-1]:
            save(resized, OUT / f"{name}.webp", quality=QUALITY, method=6)

hero = ImageOps.exif_transpose(Image.open(SRC / "hero-image.webp")).convert("RGB")
fit = ImageOps.fit(hero, (1200, 630), Image.LANCZOS, centering=(0.5, 0.4))
save(fit, OUT / "og-image.jpg", quality=82, optimize=True, progressive=True)
