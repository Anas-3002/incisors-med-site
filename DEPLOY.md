# Deploying the Incisors Med site to Hostinger

The site is plain static files; Hostinger's **Git deploy** copies the repository into a
website's document root and the site is live - there is no build step on the host.
The compiled stylesheet (`assets/css/tailwind.css`) and the local images are committed.

## Live URL

| | |
|---|---|
| Website | `darkcyan-falcon-706043.hostingersite.com` (temporary Hostinger domain) |
| Repository | `https://github.com/Anas-3002/incisors-med-site` |
| Deploy path | website root (`public_html`) |
| Cache-busting | `assets/css/tailwind.css?v=<hash>` / `assets/js/site.js?v=<hash>` |

## 1. Re-deploy after a change

```bash
npm run build          # html + tailwind css + hashes
python tools/audit.py  # must print "total problems: 0"
git add -A && git commit -m "..." && git push
```

Then pull it on the server (hPanel -> Advanced -> Git -> the site -> *Deploy*, or the
`hosting_git_deploy-website-repository` operation with `username`, `domain`,
`repository_url`, `branch: main`) and clear the cache
(`hosting_cache_clear-website`).

Verified with a real browser after deploy:

- `curl -sI https://<domain>/` returns 200 and serves this repo's `index.html`
- `/assets/css/tailwind.css` contains the design's own utilities (`bg-\[\#0B2546\]`,
  the cyan gradients) - a Tailwind build error would show as an unstyled page
- every internal link and asset returns 200; no `__SITE_URL__` token remains

## 2. Domain stamping

`canonical`, `og:url`, `og:image`, `robots.txt` and `sitemap.xml` carry the token
`__SITE_URL__`. Stamp the real domain once:

```bash
python tools/set-domain.py https://darkcyan-falcon-706043.hostingersite.com
```

The current value is remembered in `SITE-DOMAIN.txt`, so the command is idempotent and
safe to re-run after moving to the client's own domain.

## 3. If something breaks

| Symptom | Cause | Fix |
|---|---|---|
| Unstyled page | `assets/css/tailwind.css` missing or 404 | re-run `npm run build`, re-deploy |
| 500 error | `.htaccess` directive the host rejects | rename it to `.htaccess.off` (site keeps working) |
| Old page still served | Hostinger server-side cache | `hosting_cache_clear-website`, then hard-reload |
| Stale CSS after a deploy | browser cache | impossible by design - the CSS URL carries a content hash |

## 4. Things the owner should decide

- **Hotline numbers.** The design's own copy (`+1 800-INCISORS`, `tel:18004624767`) was
  kept byte-for-byte. To point calls at a real number, run
  `python tools/set-domain.py`-style replacement over `1 800-INCISORS` / `18004624767`
  in the `*.html` files and rebuild.
- **Form delivery.** All three forms hand the composed message to WhatsApp for
  **+92 341 0704151**; the constant lives in `assets/js/site.js` (`WA_NUMBER`).
  Nothing is stored on the server, which is also why no patient data can leak from it.
- **Legal pages.** `privacy-policy.html`, `hipaa-and-patient-rights.html` and
  `ada-accessibility.html` are written from the design's own claims and are a starting
  point - have them reviewed before launch.
