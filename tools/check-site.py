#!/usr/bin/env python3
"""check-site.py — IT1_Bok struktursjekk (R-13).

Forebygger regresjonene som denne gjennomgangen fant:
  1. døde interne lenker          (jf. slettet js/addeventlistener.html, F1)
  2. manglende script.js          (jf. html/tagger.html, F2)
  3. feil is-active/aria-current  (aktivt element skal matche URL-en)
  4. manglende favicon            (jf. konsoll-404, F9)

Kjøring:
    python3 tools/check-site.py

Returnerer exit-kode 0 når alt er i orden, 1 ved feil. Kan brukes i CI.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = []
for dirpath, _dirs, files in os.walk(ROOT):
    reldir = os.path.relpath(dirpath, ROOT)
    parts = reldir.split(os.sep)
    if (reldir != "." and any(p.startswith(".") for p in parts)) or "tools" in parts:
        continue
    for fn in files:
        if fn.endswith(".html"):
            PAGES.append(os.path.join(dirpath, fn))

errors = []
warnings = []

for path in sorted(PAGES):
    rel = os.path.relpath(path, ROOT)
    src = open(path, encoding="utf-8").read()

    # 1) interne href-er
    for href in re.findall(r'href="([^"]+)"', src):
        if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(path), href))
        if href.startswith("/"):
            # roterelativ bane (kun i kodeeksempler — varsel, ikke feil)
            warnings.append(f"{rel}: roterelativ href {href!r} (kodeeksempel?)")
            continue
        if target == path:
            continue
        if not os.path.exists(target):
            errors.append(f"{rel}: død lenke -> {href!r} ({os.path.relpath(target, ROOT)})")

    # 2) script.js skal være med på alle sider
    if 'src="' not in src or re.search(r'<script[^>]+src="([^"]*script\.js)"', src) is None:
        errors.append(f"{rel}: mangler script.js")

    # 3) aktiv navigasjonslenke skal matche siden selv
    page_id = os.path.basename(path)
    for m in re.finditer(r'<a class="nav-link is-active"([^>]*)href="([^"]+)"', src):
        active_href = m.group(2).replace("../", "").replace("./", "")
        if not path.endswith(active_href) and not (rel == "index.html" and active_href == "index.html"):
            errors.append(
                f"{rel}: is-active peker på {active_href!r}, ikke denne siden"
            )
            break
    if 'aria-current="page"' not in src:
        errors.append(f"{rel}: mangler aria-current=\"page\"")

    # 4) favicon
    if 'rel="icon"' not in src:
        warnings.append(f"{rel}: mangler favicon-lenke")

print(f"IT1_Bok struktursjekk — {len(PAGES)} sider")
if warnings:
    for w in warnings:
        print("  var  ", w)
if errors:
    for e in errors:
        print("  FEIL ", e)
    print(f"\n{len(errors)} feil funnet.")
    sys.exit(1)
print("Alt i orden.")
sys.exit(0)
