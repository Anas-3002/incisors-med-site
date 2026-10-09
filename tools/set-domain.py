#!/usr/bin/env python3
"""Stamp the live domain into every file that carries an absolute URL.

Usage:  python tools/set-domain.py https://darkcyan-falcon-706043.hostingersite.com

Every occurrence of the __SITE_URL__ token (canonical links, og:/twitter: tags,
robots.txt, sitemap.xml) is rewritten. Idempotent: the current value is kept in
SITE-DOMAIN.txt, so re-running with the same domain changes nothing.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "__SITE_URL__"
STAMP = os.path.join(ROOT, "SITE-DOMAIN.txt")
FILES = [f for f in os.listdir(ROOT) if f.endswith((".html", ".txt", ".xml"))]
FILES += [os.path.join("tools", "sitemap-pages.json")]

if len(sys.argv) != 2 or not re.match(r"^https?://[^/\s]+$", sys.argv[1]):
    sys.exit("usage: python tools/set-domain.py https://your-domain.tld")

domain = sys.argv[1].rstrip("/")
previous = open(STAMP).read().strip() if os.path.exists(STAMP) else TOKEN
changed = []
for rel in FILES:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding="utf-8").read()
    if previous not in text:
        continue
    open(path, "w", encoding="utf-8", newline="\n").write(text.replace(previous, domain))
    changed.append(rel)

open(STAMP, "w", encoding="utf-8", newline="\n").write(domain + "\n")
print("domain:", domain)
print("files updated:", len(changed))
for c in changed:
    print("  ", c)
leftover = [f for f in FILES if os.path.exists(os.path.join(ROOT, f))
            and TOKEN in open(os.path.join(ROOT, f), encoding="utf-8").read()]
print("files still holding the token:", leftover)
