#!/usr/bin/env python3
"""Fail if package prices disagree between the cards, the form dropdown, and the JSON-LD."""
import json, re, sys
from pathlib import Path

html = (Path(__file__).resolve().parent.parent / "index.html").read_text()
cards = {n.strip(): int(p) for n, p in re.findall(r'<p class="pkg-name">([^<]+)</p>\s*<p class="pkg-price">\$(\d+)', html)}
options = {n.strip(): int(p) for n, p in re.findall(r'<option>([^<—]+)— \$(\d+)</option>', html)}
ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
schema = {o["itemOffered"]["name"]: int(o["price"]) for o in ld["hasOfferCatalog"]["itemListElement"]}

bad = [(n, cards[n], options.get(n), schema.get(n)) for n in cards if not (cards[n] == options.get(n) == schema.get(n))]
if bad or len(cards) != len(options) or len(cards) != len(schema):
    for n, c, o, s in bad: print(f"MISMATCH {n}: card={c} dropdown={o} schema={s}")
    sys.exit("price check failed")
print("prices consistent:", cards)
