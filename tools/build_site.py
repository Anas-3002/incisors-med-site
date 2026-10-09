"""Build the Incisors Med static site from the Google Stitch export.

The export (code.html) is a single screen.  Every page here is composed from the
export's *own* header/footer/sections verbatim - no markup is retyped - so the
design is reproduced exactly; the multi-page structure only re-distributes the
sections the export already contains.
"""
import json
import os
import re

SRC = r"C:\Users\Usman\Downloads\stitch_incisors_med_dental_website\code.html"
OUT = r"C:\Users\Usman\Downloads\incisors-med-site"

WA_NUMBER = "923410" + "704151"          # +92 341 0704151
SITE_URL_TOKEN = "__SITE_URL__"

raw = open(SRC, encoding="utf-8").read()

# ---------------------------------------------------------------- export parts
head = raw[raw.index("<head>") + 6: raw.index("</head>")]
body = raw[raw.index(">", raw.index("<body")) + 1: raw.index("</body>")]

header = body[body.index("<header"): body.index("</header>") + len("</header>")]
main = body[body.index("<main"): body.index("</main>") + len("</main>")]
footer = body[body.index("<footer"): body.index("</footer>") + len("</footer>")]
tail = body[body.index("</footer>") + len("</footer>"):]

sections = []
_pos = 0
while True:
    i = main.find("<section", _pos)
    if i < 0:
        break
    j = main.index("</section>", i) + len("</section>")
    sections.append(main[i:j])
    _pos = j
assert len(sections) == 8, len(sections)

# section ids, in export order
SEC_ID = ["hero", "geo-selector", "treatments-catalog", "tech-section",
          "cases-section", "quick-booking", "faq-section", "emergency"]
SEC_LABEL = ["Hero", "Locations", "Treatments", "Technology", "Stories",
             "Booking", "FAQ", "Emergency"]

inline_style = re.search(r"<style id=\"base-layer\">(.*?)</style>", head, re.S)
if inline_style is None:                       # export ships it unlabelled
    inline_style = re.search(r"<style>(.*?)</style>", head, re.S)
BASE_CSS = inline_style.group(1)

# local image paths
IMG = json.load(open(os.path.join(OUT, "tools", "image-map.json")))
for _u, _p in IMG.items():
    header = header.replace(_u, _p)
    footer = footer.replace(_u, _p)
    sections = [s.replace(_u, _p) for s in sections]

# ------------------------------------------------------------- link inventory
PAGES = {
    "home": "index.html",
    "treatments-and-services": "treatments-and-services.html",
    "doctors-and-technology": "doctors-and-technology.html",
    "patient-stories": "patient-stories.html",
    "contact-and-locations": "contact-and-locations.html",
    "faq": "faq.html",
    "blog-and-oral-health": "faq.html",          # knowledge base == FAQ screen
    "book-appointment": "book-appointment.html",
    "patient-portal": "patient-portal.html",
    "privacy-policy": "privacy-policy.html",
    "hipaa-and-patient-rights": "hipaa-and-patient-rights.html",
    "ada-accessibility": "ada-accessibility.html",
}
ANCHOR_PAGE = {
    "treatments-catalog": "treatments-and-services.html",
    "tech-section": "doctors-and-technology.html",
    "cases-section": "patient-stories.html",
    "geo-selector": "contact-and-locations.html",
    "faq-section": "faq.html",
    "quick-booking": "book-appointment.html",
}

NAV = [("home", "Home"),
       ("treatments-and-services", "Treatments &amp; Services"),
       ("doctors-and-technology", "Doctors &amp; Technology"),
       ("patient-stories", "Patient Stories"),
       ("contact-and-locations", "Locations"),
       ("faq", "FAQ")]
NAV_TARGET = ["index.html", "treatments-and-services.html",
              "doctors-and-technology.html", "patient-stories.html",
              "contact-and-locations.html", "faq.html"]
NAV_REST = 'px-3.5 py-1.5 rounded-full hover:bg-slate-100 hover:text-cyan-700 transition-colors'
NAV_ACTIVE = 'px-3.5 py-1.5 rounded-full bg-cyan-50 text-cyan-700 font-bold transition-colors'


def nav_html(active):
    out = []
    for i, (key, label) in enumerate(NAV):
        cls = NAV_ACTIVE if key == active else NAV_REST
        cur = ' aria-current="page"' if key == active else ""
        out.append('<a%s class="%s" data-path="%s" href="%s">%s</a>'
                   % (cur, cls, key, NAV_TARGET[i], label))
    return "\n".join(out)


# replace the export's nav list with the page-aware one
nav_re = re.compile(r'<nav class="hidden xl:flex.*?</nav>', re.S)
assert len(nav_re.findall(header)) == 1
NAV_OPEN = ('<nav class="hidden xl:flex items-center gap-1.5 text-sm font-semibold '
            'text-slate-600">\n@@NAV@@\n</nav>')
HEADER_TMPL = nav_re.sub(NAV_OPEN.replace("\\", "\\\\"), header)

# make the export's (inert) hamburger actually open a panel - mobile users have no
# other route to navigation since the nav is xl:hidden.
_BTN_OLD = '''<button aria-label="Toggle Navigation" class="xl:hidden p-2 rounded-lg text-slate-600 hover:text-cyan-600 hover:bg-cyan-50 transition-colors" type="button">
<span class="material-symbols-outlined text-[26px]">menu</span>
</button>'''
_BTN_NEW = '''<button aria-controls="mobile-menu" aria-expanded="false" aria-label="Toggle Navigation" class="xl:hidden p-2 rounded-lg text-slate-600 hover:text-cyan-600 hover:bg-cyan-50 transition-colors" id="mobile-menu-toggle" type="button">
<span aria-hidden="true" class="material-symbols-outlined text-[26px]" id="mobile-menu-icon">menu</span>
</button>'''
assert HEADER_TMPL.count(_BTN_OLD) == 1
HEADER_TMPL = HEADER_TMPL.replace(_BTN_OLD, _BTN_NEW)

MOBILE_LINK = ('<a class="px-4 py-3 rounded-xl hover:bg-cyan-50 hover:text-cyan-700 transition-colors%s" '
               'data-path="%s" href="%s">%s</a>')
MOBILE_MENU = '''<div class="hidden xl:hidden bg-white/95 backdrop-blur-md border-t border-slate-200/80 px-4 lg:px-12 pb-5 pt-3 shadow-lg" id="mobile-menu">
<nav class="max-w-[1360px] mx-auto flex flex-col gap-1 text-sm font-semibold text-slate-600">@@MOBILE_NAV@@</nav>
<a class="mt-3 flex items-center justify-center gap-2 px-5 py-3 rounded-full text-white font-bold text-sm bg-gradient-to-r from-cyan-600 via-teal-500 to-cyan-500 shadow-[0_4px_16px_rgba(6,182,212,0.35)] transition-all" data-path="book-appointment" href="#quick-booking">
<span aria-hidden="true" class="material-symbols-outlined text-[19px]">calendar_month</span><span>Book Appointment</span></a>
</div>'''
HEADER_TMPL = HEADER_TMPL.replace("</header>", MOBILE_MENU + "\n</header>")


def mobile_nav_html(active):
    out = []
    for i, (key, label) in enumerate(NAV):
        extra = " bg-cyan-50 text-cyan-700 font-bold" if key == active else ""
        out.append(MOBILE_LINK % (extra, key, NAV_TARGET[i], label))
    return "\n".join(out)


# --------------------------------------------------- footer: ids for the form
assert footer.count('placeholder="physician-or-patient@email.com"') == 1
footer = footer.replace(
    '<input class="w-full px-3.5 py-2.5 bg-white/10 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400" placeholder="physician-or-patient@email.com" type="email"/>',
    '<input class="w-full px-3.5 py-2.5 bg-white/10 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400" id="digest-email" placeholder="physician-or-patient@email.com" type="email"/>')
assert footer.count('>Subscribe Digest</button>') == 1
footer = footer.replace('type="button">Subscribe Digest</button>',
                        'id="digest-submit" type="button">Subscribe Digest</button>')

# ------------------------------------------------------ booking form: name attrs
def patch_booking(sec):
    if 'id="quick-booking"' not in sec:
        return sec
    reps = [
        ('placeholder="e.g. Rachel Sterling" required="" type="text"',
         'name="full_name" placeholder="e.g. Rachel Sterling" required="" type="text"'),
        ('placeholder="(555) 019-2834" required="" type="tel"',
         'name="phone" placeholder="(555) 019-2834" required="" type="tel"'),
        ('id="form-clinic-select">', 'id="form-clinic-select" name="clinic">'),
        ('<select class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500">\n<option value="Implant Consultation">',
         '<select class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" name="reason">\n<option value="Implant Consultation">'),
        ('<form class="space-y-4" onsubmit="handleBookingSubmit(event)">',
         '<form class="space-y-4" id="booking-form" onsubmit="handleBookingSubmit(event)">'),
    ]
    for a, b in reps:
        assert sec.count(a) == 1, (a[:60], sec.count(a))
        sec = sec.replace(a, b)
    return sec


sections = [patch_booking(s) for s in sections]

# --------------------------------------------------------------- page catalog
LEGAL = {
    "privacy-policy.html": dict(
        eyebrow="Legal &amp; Compliance",
        title="Privacy Policy",
        lead="How Incisors Med collects, uses, safeguards, and disposes of patient information across our three surgical pavilions and digital services.",
        blocks=[
            ("Information We Collect",
             "We collect only the information required to deliver clinical care and to operate this website: your name, contact number, e-mail address, preferred clinic location, treatment interest, and any details you choose to share when you request an appointment or contact our team. Clinical records created during treatment are maintained separately inside our HIPAA-aligned practice management system."),
            ("How Your Information Is Used",
             "Appointment requests submitted through this website are transmitted directly to our patient concierge team so that a coordinator can confirm your slot. Records are used for treatment planning, insurance verification, billing, quality assurance, and legally required clinical documentation. We do not sell, rent, or trade patient or visitor information."),
            ("Sharing And Disclosure",
             "Information is shared only with clinicians involved in your care, laboratories or specialists you have approved, your dental insurance carrier for claim processing, and government bodies where disclosure is required by law. Business associates operate under written confidentiality agreements."),
            ("Retention And Your Choices",
             "Clinical records are retained for the period required by applicable healthcare and tax regulation, after which they are securely destroyed. You may request a copy of your record, ask for corrections, or withdraw marketing consent at any time by contacting the practice; we respond to verified requests within 30 days."),
            ("Website Data &amp; Cookies",
             "This website is served as static content and stores your clinic selection only in your browser. We use no advertising trackers. Aggregate, non-identifying analytics may be collected to understand which treatments visitors look for."),
            ("Contacting Us",
             "Privacy questions, access requests, and complaints can be raised through the WhatsApp channel in the booking section of this site or by telephone using the hotline published in the site header."),
        ]),
    "hipaa-and-patient-rights.html": dict(
        eyebrow="Patient Rights",
        title="HIPAA &amp; Patient Rights",
        lead="A plain-language statement of the privacy, access, and safety rights every patient of Incisors Med holds.",
        blocks=[
            ("Notice Of Privacy Practices",
             "This statement describes how protected health information may be used and disclosed and how you can obtain access to your own information. It applies to every clinician, employee, and contractor working within our practice."),
            ("Your Right To Access",
             "You may inspect and obtain a copy of your dental record, radiographs, and treatment notes. Requests are acknowledged within a reasonable period and fulfilled electronically where you prefer that format."),
            ("Your Right To Amend And Restrict",
             "You may request that we correct inaccurate entries, restrict certain disclosures, or direct confidential communications to a particular telephone number or e-mail address."),
            ("Your Right To An Accounting Of Disclosures",
             "You may ask for a list of disclosures of your health information made outside treatment, payment, and healthcare operations, and we will provide it for the statutory look-back period."),
            ("Safeguards We Maintain",
             "Administrative, technical, and physical safeguards protect records: role-based system access, encrypted backups, audit logging, staff training, and locked clinical areas. Security incidents are investigated and reported as regulations require."),
            ("Filing A Complaint",
             "You may raise a concern with our privacy officer without fear of retaliation, and you retain the right to complain to the relevant government oversight body regarding our privacy practices."),
        ]),
    "ada-accessibility.html": dict(
        eyebrow="Inclusion",
        title="ADA Accessibility Statement",
        lead="Our commitment to a clinic and a website that patients with disabilities can use independently.",
        blocks=[
            ("Physical Accessibility",
             "Our surgical pavilions provide step-free entry, accessible washrooms, and transfer-friendly operatories. The North Lake Family Center is certified for strollers and wheelchairs. Patients with mobility, hearing, or vision support needs can request assistance when scheduling."),
            ("Website Accessibility",
             "This website is built with semantic headings, keyboard-operable navigation, visible focus states, descriptive alternative text for imagery, and colour contrast chosen to remain legible for low-vision visitors. Content reflows to a single column on small screens instead of forcing horizontal scrolling."),
            ("Assistive Technology",
             "Pages have been checked with keyboard-only navigation and screen-reader landmarks. If a control does not operate with your assistive technology, we will arrange an alternative way to complete the same task."),
            ("Communicating With Us",
             "We can arrange interpretation, large-print documents, or a telephone appointment conducted with a support person present. Ask the concierge team when confirming your visit."),
            ("Ongoing Review",
             "Accessibility findings are reviewed whenever the site changes. Reports of a barrier are logged and prioritised, and we will tell you what was changed and when."),
            ("Feedback",
             "Share an accessibility issue through the contact channels on this site. Please include the page and the assistive technology you used so we can reproduce the problem."),
        ]),
}

PAGE_DEFS = [
    dict(file="index.html", nav="home", sections=[0, 1, 2, 3, 4, 5, 6, 7],
         title="Incisors Med | Advanced Surgical Dentistry, Implants &amp; Cosmetic Care",
         desc="Precision dentistry meets gentle care: AI-guided diagnostics, same-day ceramic crowns, sedation dentistry and implant surgery across three metro surgical pavilions."),
    dict(h1=True, file="treatments-and-services.html", nav="treatments-and-services", sections=[2, 5],
         title="Treatments &amp; Services | Incisors Med Surgical Dentistry",
         desc="Cosmetic veneers, clear aligners, dental implants and All-on-4, 3D-guided root canals, laser gum therapy and pediatric dentistry with digital micro-precision."),
    dict(h1=True, file="doctors-and-technology.html", nav="doctors-and-technology", sections=[3, 5],
         title="Doctors &amp; Technology | Incisors Med",
         desc="Ultra-low dose 3D CBCT imaging, goop-free intraoral scanning, same-day CEREC ceramic milling and board-certified surgical specialists."),
    dict(h1=True, file="patient-stories.html", nav="patient-stories", sections=[4, 7],
         title="Patient Stories &amp; Smile Transformations | Incisors Med",
         desc="Real before-and-after clinical reconstructions: porcelain veneers, All-on-4 full-arch implants and clear-aligner orthodontics reviewed by our patients."),
    dict(h1=True, file="contact-and-locations.html", nav="contact-and-locations", sections=[1, 5],
         title="Locations &amp; Contact | Incisors Med Surgical Centers",
         desc="Three metro surgical pavilions with live operatory availability, parking, specialties and instant digital record transfer. Select a clinic and lock your slot."),
    dict(h1=True, file="faq.html", nav="faq", sections=[6, 5],
         title="FAQ &amp; Oral Health Knowledge Base | Incisors Med",
         desc="Evidence-based answers on pain-free surgery, implant costs and financing, same-day crowns, emergency triage, and veneers versus composite bonding."),
    dict(h1=True, file="book-appointment.html", nav="book-appointment", sections=[5, 1],
         title="Book an Appointment | Incisors Med",
         desc="Request a dental appointment in under 60 seconds: choose your treatment, pick a surgical pavilion and confirm instantly through WhatsApp."),
]

# ------------------------------------------------------------------ utilities
def asset_url(rel):
    """Relative asset URL with a content hash, so a deploy can never be masked by a
    cache holding the previous stylesheet or script."""
    full = os.path.join(OUT, rel.replace("/", os.sep))
    if os.path.exists(full):
        import hashlib
        h = hashlib.sha1(open(full, "rb").read()).hexdigest()[:8]
        return rel + "?v=" + h
    return rel


HEAD_LINKS = ('<meta charset="utf-8"/>\n'
              '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>\n'
              '<meta content="web_standard" name="shell-type"/>\n'
              '<meta name="theme-color" content="#0A2540"/>\n'
              '<link rel="preconnect" href="https://fonts.googleapis.com"/>\n'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>\n'
              '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:'
              'wght@400;500;600;700;800&amp;family=Material+Symbols+Outlined:'
              'opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&amp;display=swap" '
              'rel="stylesheet"/>\n'
              '<link href="' + asset_url("assets/css/tailwind.css") + '" rel="stylesheet"/>\n'
              '<script>document.documentElement.classList.add("js");</script>')


def meta_block(pd):
    t = pd["title"]
    d = pd["desc"]
    url = SITE_URL_TOKEN + "/" + ("" if pd["file"] == "index.html" else pd["file"])
    img = SITE_URL_TOKEN + "/assets/img/hero-operatory.jpg"
    return f"""<title>{t}</title>
<meta name="description" content="{d}"/>
<link rel="canonical" href="{url}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="Incisors Med"/>
<meta property="og:title" content="{t}"/>
<meta property="og:description" content="{d}"/>
<meta property="og:url" content="{url}"/>
<meta property="og:image" content="{img}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{t}"/>
<meta name="twitter:description" content="{d}"/>
<meta name="twitter:image" content="{img}"/>"""


def rewrite_links(html, page_anchors, active_nav):
    """data-path -> real page, and anchors -> in-page or index.html anchors."""
    def dp(m):
        key = m.group("key")
        return m.group(0).replace('href="%s"' % m.group("href"), 'href="%s"' % PAGES[key])

    html = re.sub(r'data-path="(?P<key>[a-z-]+)" href="(?P<href>[^"]*)"', dp, html)

    def anchor(m):
        aid = m.group(1)
        if aid in page_anchors:
            return m.group(0)
        return 'href="%s"' % (ANCHOR_PAGE.get(aid, "index.html#" + aid))

    html = re.sub(r'href="#([a-zA-Z0-9_-]+)"', anchor, html)
    return html


def page_html(pd):
    secs = [sections[i] for i in pd["sections"]]
    if pd.get("h1") and secs:
        # one h1 per page: the design's first section heading becomes it (tailwind
        # preflight makes h1/h2 render identically, so nothing moves visually)
        first = secs[0]
        i = first.find("<h2")
        j = first.find("</h2>", i)
        assert i > 0 and j > i
        secs[0] = first[:i] + "<h1" + first[i + 3:j] + "</h1>" + first[j + 5:]
    anchors = {SEC_ID[i] for i in pd["sections"]}
    anchors.update(["quick-booking"])
    inner = "\n".join(secs)
    body_mode = "bg-slate-50 font-sans text-slate-800 antialiased selection:bg-cyan-500 selection:text-white"
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_LINKS}
{meta_block(pd)}
<style>{BASE_CSS}</style>
</head>
<body class="{body_mode}">
{HEADER_TMPL.replace("@@NAV@@", nav_html(pd.get("nav"))).replace("@@MOBILE_NAV@@", mobile_nav_html(pd.get("nav")))}
<main class="w-full pt-28"><div class="flex flex-col w-full">
{inner if inner else "<!--@@BODY@@-->"}
</div></main>
{footer}
{tail}
<script src="{asset_url('assets/js/site.js')}" defer></script>
</body>
</html>
"""
    return rewrite_links(doc, anchors, pd.get("nav"))


def legal_section(eyebrow, title, lead, blocks, h1=True):
    cards = "\n".join(
        f"""<div class="bg-gradient-to-b from-white to-sky-50/40 border border-slate-200/80 p-6 rounded-2xl shadow-sm space-y-2">
<h2 class="text-lg font-bold text-slate-900 flex items-start gap-2.5"><span aria-hidden="true" class="material-symbols-outlined text-cyan-600 text-[24px] mt-0.5">verified_user</span>{t}</h2>
<p class="text-sm text-slate-600 leading-relaxed pl-8">{b}</p>
</div>""" for t, b in blocks)
    tag = "h1" if h1 else "h2"
    return f"""<section class="py-16 lg:py-20 bg-white">
<div class="max-w-[1360px] mx-auto px-4 lg:px-12 space-y-8">
<div class="max-w-3xl space-y-2">
<span class="text-xs font-extrabold uppercase tracking-widest text-cyan-600">{eyebrow}</span>
<{tag} class="text-3xl lg:text-4xl font-extrabold text-slate-900">{title}</{tag}>
<p class="text-slate-600 text-base">{lead}</p>
<span class="block text-xs font-bold text-slate-500 uppercase tracking-wider">Last reviewed: January 2025</span>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">{cards}</div>
<div class="p-4 md:p-5 bg-gradient-to-r from-sky-50 via-cyan-50 to-teal-50 border border-cyan-200 rounded-2xl shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
<div class="flex items-center gap-3.5">
<div class="p-3 bg-cyan-600 text-white rounded-xl shadow-sm"><span aria-hidden="true" class="material-symbols-outlined text-[24px]">support_agent</span></div>
<div>
<span class="block text-sm font-extrabold text-slate-900">Questions about this statement?</span>
<span class="block text-xs font-semibold text-cyan-800">Our patient concierge team replies on WhatsApp during clinic hours.</span>
</div>
</div>
<a class="px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white rounded-full text-xs font-bold shadow-md shadow-cyan-600/20 transition-all" href="book-appointment.html">Contact the Practice &rarr;</a>
</div>
</div>
</section>"""


PORTAL_SECTION = """<section class="py-16 lg:py-20 bg-slate-50" id="patient-portal">
<div class="max-w-[1360px] mx-auto px-4 lg:px-12">
<div class="bg-gradient-to-br from-[#0B2546] via-[#0E3560] to-[#0A2242] text-white rounded-3xl p-8 lg:p-12 shadow-2xl relative overflow-hidden border border-cyan-500/30">
<div class="absolute -right-20 -bottom-20 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none"></div>
<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center relative z-10">
<div class="lg:col-span-5 space-y-6">
<span class="inline-block px-3 py-1 bg-cyan-400/20 text-cyan-300 border border-cyan-400/30 rounded-full text-xs font-bold uppercase tracking-wider">Secure Patient Area</span>
<h1 class="text-3xl lg:text-4xl font-extrabold text-white leading-tight">Your Records, <span class="text-cyan-300">One Message Away</span></h1>
<p class="text-slate-300 text-sm leading-relaxed">Portal credentials are issued to registered patients after their first clinical visit. Request access and our team will verify your identity, then send your secure sign-in details by WhatsApp.</p>
<div class="p-4 bg-white/5 border border-cyan-400/30 rounded-2xl flex items-start gap-3.5">
<div class="p-2.5 rounded-lg bg-cyan-500/20 text-cyan-300"><span aria-hidden="true" class="material-symbols-outlined text-[22px]">lock</span></div>
<div><strong class="block text-sm font-bold text-white">What you can do online</strong><span class="text-xs text-slate-300">Review treatment plans, download radiographs, confirm appointments and settle balances.</span></div>
</div>
</div>
<div class="lg:col-span-7 bg-white text-slate-900 p-8 rounded-2xl shadow-xl">
<form class="space-y-4" id="portal-form" onsubmit="handlePortalSubmit(event)">
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-name">Full Name</label>
<input class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-name" name="full_name" placeholder="e.g. Rachel Sterling" required="" type="text"/>
</div>
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-phone">Phone Number</label>
<input class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-phone" name="phone" placeholder="(555) 019-2834" required="" type="tel"/>
</div>
</div>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-dob">Date of Birth</label>
<input class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-dob" name="dob" type="date"/>
</div>
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-clinic">Home Clinic</label>
<select class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-clinic" name="clinic">
<option value="Downtown Medical Pavilion">Downtown Medical Pavilion</option>
<option value="West End Smile Lounge">West End Smile Lounge</option>
<option value="North Lake Family Center">North Lake Family Center</option>
</select>
</div>
</div>
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-reason">Reason for Access</label>
<select class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-reason" name="reason">
<option value="First-time portal access">First-time portal access</option>
<option value="Lost portal credentials">Lost portal credentials</option>
<option value="Copy of clinical records">Copy of my clinical records</option>
<option value="Billing & insurance question">Billing &amp; insurance question</option>
</select>
</div>
<div>
<label class="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5" for="portal-notes">Notes for the concierge team</label>
<textarea class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500" id="portal-notes" name="notes" placeholder="Anything that helps us verify your identity" rows="3"></textarea>
</div>
<button class="w-full py-4 bg-gradient-to-r from-cyan-600 via-teal-500 to-cyan-500 hover:from-cyan-500 hover:to-teal-600 text-white rounded-xl text-sm font-extrabold shadow-lg shadow-cyan-600/30 transition-all flex items-center justify-center gap-2" type="submit">
<span aria-hidden="true" class="material-symbols-outlined text-[20px]">login</span>
<span>Request Portal Access</span>
</button>
<p class="text-center text-xs text-slate-400 font-medium">🔒 Encrypted transmission. Identity is verified against your clinical record before credentials are issued.</p>
</form>
<div class="hidden mt-4 p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-bold" id="portal-success">
              ✅ Request sent. Our concierge team will verify your record and reply on WhatsApp within one working day.
            </div>
</div>
</div>
</div>
</div>
</section>"""

NOT_FOUND_SECTION = """<section class="py-20 lg:py-24 bg-gradient-to-b from-sky-50/80 via-cyan-50/40 to-white">
<div class="max-w-[1360px] mx-auto px-4 lg:px-12">
<div class="max-w-2xl mx-auto text-center space-y-5">
<span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/90 border border-cyan-200 shadow-sm text-xs font-bold uppercase tracking-wider text-cyan-800">
<span class="flex h-2.5 w-2.5 rounded-full bg-cyan-500 animate-pulse"></span>Page 404</span>
<h1 class="text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight">This Page Has Moved On</h1>
<p class="text-lg text-slate-600 leading-relaxed">The link you followed no longer exists. Everything else still does — jump straight to the treatment you are looking for, or let our concierge book you in.</p>
<div class="flex flex-wrap items-center justify-center gap-4 pt-2">
<a class="inline-flex items-center gap-2.5 px-7 py-4 rounded-full text-white font-bold text-base bg-gradient-to-r from-cyan-600 via-teal-500 to-sky-600 hover:from-cyan-500 hover:to-teal-500 shadow-[0_8px_24px_rgba(6,182,212,0.4)] transition-all" href="book-appointment.html">
<span aria-hidden="true" class="material-symbols-outlined text-[20px] text-cyan-100">calendar_check</span><span>Book Instant Consultation</span></a>
<a class="inline-flex items-center gap-2 px-6 py-4 rounded-full text-slate-800 font-bold text-base bg-white hover:bg-slate-50 border-2 border-cyan-200 hover:border-cyan-400 shadow-sm transition-all" href="index.html"><span>Back to Home</span></a>
</div>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8 text-left">
<a class="bg-white border border-slate-200/80 hover:border-cyan-400 p-5 rounded-2xl shadow-sm hover:shadow-lg transition-all" href="treatments-and-services.html"><span class="material-symbols-outlined text-cyan-600 text-[24px]">auto_awesome</span><span class="block text-base font-bold text-slate-900 mt-1">Treatments &amp; Services</span></a>
<a class="bg-white border border-slate-200/80 hover:border-cyan-400 p-5 rounded-2xl shadow-sm hover:shadow-lg transition-all" href="contact-and-locations.html"><span class="material-symbols-outlined text-cyan-600 text-[24px]">pin_drop</span><span class="block text-base font-bold text-slate-900 mt-1">Locations</span></a>
<a class="bg-white border border-slate-200/80 hover:border-cyan-400 p-5 rounded-2xl shadow-sm hover:shadow-lg transition-all" href="faq.html"><span class="material-symbols-outlined text-cyan-600 text-[24px]">help</span><span class="block text-base font-bold text-slate-900 mt-1">FAQ</span></a>
</div>
</div>
</div>
</section>"""

# --------------------------------------------------------------------- write
written = []
os.makedirs(OUT, exist_ok=True)
for pd in PAGE_DEFS:
    html = page_html(pd)
    open(os.path.join(OUT, pd["file"]), "w", encoding="utf-8", newline="\n").write(html)
    written.append((pd["file"], len(html)))

for fn, spec in LEGAL.items():
    pd = dict(file=fn, nav=None, sections=[],
              title=spec["title"] + " | Incisors Med",
              desc=re.sub(r"<[^>]+>", "", spec["lead"])[:170])
    html = page_html(pd)
    body_new = legal_section(spec["eyebrow"], spec["title"], spec["lead"], spec["blocks"])
    html = html.replace("<!--@@BODY@@-->", body_new)
    assert body_new in html, fn
    open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(html)
    written.append((fn, len(html)))

# patient portal
pd = dict(file="patient-portal.html", nav=None, sections=[],
          title="Patient Portal | Incisors Med",
          desc="Request secure patient portal access to review treatment plans, download radiographs, confirm appointments and settle balances with Incisors Med.")
html = page_html(pd)
html = html.replace("<!--@@BODY@@-->", PORTAL_SECTION)
assert PORTAL_SECTION in html
open(os.path.join(OUT, "patient-portal.html"), "w", encoding="utf-8", newline="\n").write(html)
written.append(("patient-portal.html", len(html)))

# 404
pd = dict(file="404.html", nav=None, sections=[],
          title="Page Not Found | Incisors Med",
          desc="The page you requested could not be found. Continue to treatments, locations or book an appointment with Incisors Med.")
html = page_html(pd)
html = html.replace("<!--@@BODY@@-->", NOT_FOUND_SECTION)
assert NOT_FOUND_SECTION in html
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8", newline="\n").write(html)
written.append(("404.html", len(html)))

for f, n in written:
    print(f"{f:34s} {n:7d}")
print("WA number parts:", len(WA_NUMBER), WA_NUMBER[:4], WA_NUMBER[4:])
