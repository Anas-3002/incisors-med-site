"""Static audit of the built site: link integrity, anchors, structure, class parity."""
import json
import os
import re
import sys

ROOT = r"C:\Users\Usman\Downloads\incisors-med-site"
BS = chr(92)          # one backslash, built at runtime to avoid escape/octal mistakes
CSS = os.path.join(ROOT, "assets", "css", "tailwind.css")
css = open(CSS, encoding="utf-8").read()

pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
problems = []
summary = []


def ids_of(html, tag="section"):
    return re.findall(r'<%s[^>]*\bid="([^"]+)"' % tag, html)


def all_ids(html):
    return set(re.findall(r'\bid="([^"]+)"', html))


def escape_cls(c):
    out = []
    for ch in c:
        if ch in ("[", "]", "/", ".", ":", "%", "#", "(", ")", ",", "!", "*", "+", ">", "@", "'", "=", "&", "$"):
            out.append(BS + ch)
        else:
            out.append(ch)
    return "".join(out)


class_cache = {}
for f in pages:
    html = open(os.path.join(ROOT, f), encoding="utf-8").read()
    # ---- structure
    h1 = len(re.findall(r"<h1\b", html))
    secs = re.findall(r"<section", html)
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)"/>', html, re.S).group(1)
    canonical = re.search(r'<link rel="canonical" href="(.*?)"/>', html).group(1)
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
    local_imgs = [i for i in imgs if not i.startswith("http")]
    missing_imgs = [i for i in local_imgs if not os.path.exists(os.path.join(ROOT, i.replace("/", os.sep)))]
    no_alt = len(re.findall(r"<img(?![^>]*\balt=)", html))
    ids = ids_of(html)
    dup_ids = [i for i in set(ids) if ids.count(i) > 1]
    # ---- links
    hrefs = re.findall(r'<a[^>]*href="([^"]*)"', html)
    empty = [h for h in hrefs if h in ("", "#")]
    internal = [h for h in hrefs if not re.match(r"^(https?:|mailto:|tel:|#)", h)]
    missing_pages = [h for h in internal if not os.path.exists(os.path.join(ROOT, h.split("#")[0]))]
    # ---- class parity against the compiled stylesheet
    NON_TAILWIND = {"material-symbols-outlined", "clinic-card", "js"}
    classes = set()
    for m in re.finditer(r'class="([^"]*)"', html):
        for c in m.group(1).split():
            classes.add(c)
    unknown = []
    for c in classes:
        if c in NON_TAILWIND:
            continue
        if c in class_cache:
            hit = class_cache[c]
        else:
            esc = escape_cls(c)
            norm = esc.replace(BS + ",", BS + "2c ")
            hit = ("." + esc) in css or ("." + norm) in css
            class_cache[c] = hit
        if not hit:
            unknown.append(c)
    summary.append(dict(page=f, title=title[:60], desc_len=len(desc), canonical=canonical,
                        h1=h1, sections=len(secs), ids=len(set(ids)), imgs=len(imgs),
                        no_alt=no_alt, links=len(hrefs), empty=len(empty),
                        internal=len(internal), missing_pages=missing_pages,
                        missing_imgs=missing_imgs, dup_ids=dup_ids,
                        unknown_classes=unknown))
    if empty:
        problems.append((f, "empty hrefs", empty[:5]))
    if missing_pages:
        problems.append((f, "missing target pages", missing_pages[:5]))
    if missing_imgs:
        problems.append((f, "missing images", missing_imgs[:5]))
    if dup_ids:
        problems.append((f, "duplicate ids", dup_ids[:5]))
    if no_alt:
        problems.append((f, "img without alt", no_alt))
    if unknown:
        problems.append((f, "classes not in compiled css", unknown[:12]))
    if h1 != 1:
        problems.append((f, "h1 count", h1))

# ---- every in-page anchor target must exist on the page that owns it
for f in pages:
    html = open(os.path.join(ROOT, f), encoding="utf-8").read()
    ids = all_ids(html)
    for m in re.finditer(r'href="(?:%s)?#([A-Za-z0-9_-]+)"' % re.escape(f), html):
        if m.group(1) not in ids:
            problems.append((f, "anchor target missing on same page", m.group(1)))
    for m in re.finditer(r'href="([a-z0-9-]+\.html)#([A-Za-z0-9_-]+)"', html):
        target, aid = m.group(1), m.group(2)
        if not os.path.exists(os.path.join(ROOT, target)):
            problems.append((f, "anchor target page missing", target))
            continue
        th = open(os.path.join(ROOT, target), encoding="utf-8").read()
        if aid not in all_ids(th):
            problems.append((f, "anchor id missing on %s" % target, aid))

print(json.dumps(summary, indent=1))
print("\n==== PROBLEMS ====")
for p in problems:
    print(" ", p)
print("total problems:", len(problems))
