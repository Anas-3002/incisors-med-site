# Incisors Med - static site (Hostinger)

Static marketing site built 1:1 from the Google Stitch export
(`stitch_incisors_med_dental_website/code.html`), served as plain HTML/CSS/JS.
No WordPress, no PHP, no build step on the host.

## Pages

| File | Header nav entry | Content |
|---|---|---|
| `index.html` | Home | the export, all 8 sections, verbatim |
| `treatments-and-services.html` | Treatments & Services | treatments catalogue + booking |
| `doctors-and-technology.html` | Doctors & Technology | AI / robotics spotlight + booking |
| `patient-stories.html` | Patient Stories | before/after cases + emergency banner |
| `contact-and-locations.html` | Locations | clinic selector + booking |
| `faq.html` | FAQ | FAQ / oral-health knowledge base + booking |
| `book-appointment.html` | (Book Appointment CTA) | booking form + clinic selector |
| `patient-portal.html` | (Patient Portal link) | portal access request |
| `privacy-policy.html` | footer | privacy policy |
| `hipaa-and-patient-rights.html` | footer | patient rights |
| `ada-accessibility.html` | footer | accessibility statement |
| `404.html` | - | not-found page |

Every page reuses the export's own header, sections and footer - no design was redrawn.

## Patient forms -> WhatsApp

There is no server, so all three forms compose a message and hand it to WhatsApp for
**+92 341 0704151** (`assets/js/site.js`, constant `WA_NUMBER`):

- booking form (`#booking-form`) - name, phone, clinic, reason, sedation preference
- portal access request (`#portal-form`)
- footer digest sign-up (`#digest-email` / `#digest-submit`)

Change the number in one place: `assets/js/site.js` (`WA_NUMBER`, assembled from two
string parts so nothing can mangle it).

## Build

```bash
npm install
npm run build          # regenerate HTML from tools/build_site.py, then compile Tailwind
node tools/serve.js    # or: python -m http.server 8899 --bind 127.0.0.1
python tools/audit.py  # link/anchor/class/h1/meta audit - must print "total problems: 0"
```

- `tools/build_site.py` slices the Stitch export into header / 8 sections / footer and
  composes each page from them, rewrites every `data-path="#..."` link to a real page and
  keeps in-page anchors working. It is the single source of truth for the markup.
- `tailwind.config.js` is the export's own inline config plus the plugins the export's
  Play-CDN tag requested (`forms`, `container-queries`). The compiled CSS is committed so
  the host needs no build.
- `assets/img/*` are the export's CDN images downloaded locally (the Google Aida URLs are
  ephemeral).

## Deploy

See `DEPLOY.md`. In short: push to GitHub and let Hostinger deploy the repo into
`public_html` (Advanced -> Git), or upload the repo contents by FTP/File Manager.
