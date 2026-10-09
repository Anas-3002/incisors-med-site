/* Live design-fidelity gate: measures computed styles on the deployed site and on the
   original Stitch export, and prints both for comparison.
   node tools/live-check.js <live-url> <reference-url>                                     */
const http = require("http");

const LIVE = process.argv[2];
const REF = process.argv[3];

const MEASURE = `(() => {
  const doc = document, out = {};
  const secs = [...doc.querySelectorAll('main section')];
  out.sections = secs.length;
  out.sectionBg = secs.map(s => getComputedStyle(s).backgroundColor + '|' + getComputedStyle(s).backgroundImage.slice(0,50));
  const b = getComputedStyle(doc.body);
  out.body = [b.fontFamily, b.fontSize, b.fontWeight, b.color, b.backgroundColor, b.lineHeight].join(' ; ');
  const h1 = doc.querySelector('h1');
  if (h1) { const c = getComputedStyle(h1); out.h1 = [c.fontFamily, c.fontSize, c.fontWeight, c.lineHeight, c.letterSpacing, c.color].join(' ; '); }
  const p = doc.querySelector('main p');
  if (p) { const c = getComputedStyle(p); out.p = [c.fontSize, c.lineHeight, c.color].join(' ; '); }
  const top = doc.querySelector('header > div');
  out.topbar = top ? getComputedStyle(top).backgroundColor : null;
  const cta = doc.querySelector('header a[data-path="book-appointment"], header a[href*="book-appointment"]');
  if (cta) { const c = getComputedStyle(cta); out.cta = [c.backgroundImage.slice(0,70), c.borderRadius, c.color, c.fontWeight, c.fontSize].join(' ; '); }
  const card = doc.querySelector('.clinic-card');
  if (card) { const c = getComputedStyle(card); out.clinicCard = [c.borderRadius, c.borderTopWidth, c.borderTopColor, c.padding].join(' ; '); }
  const svc = doc.querySelector('main section:nth-of-type(3) .grid > div');
  if (svc) { const c = getComputedStyle(svc); out.serviceCard = [c.borderRadius, c.borderTopColor, c.backgroundColor].join(' ; '); }
  const icon = doc.querySelector('.material-symbols-outlined');
  if (icon) { const c = getComputedStyle(icon); out.icon = [c.fontSize, c.lineHeight].join(' ; '); }
  out.headerH = Math.round(doc.querySelector('header').getBoundingClientRect().height);
  out.docW = doc.documentElement.scrollWidth;
  out.title = doc.title.slice(0, 50);
  out.broken = [...doc.querySelectorAll('img')].filter(i => !i.complete || i.naturalWidth === 0).length;
  out.imgCount = doc.querySelectorAll('img').length;
  out.emptyLinks = [...doc.querySelectorAll('a[href]')].filter(a => ['#',''].includes(a.getAttribute('href'))).length;
  out.cssSheets = [...doc.styleSheets].map(s => (s.href||'inline').split('/').slice(-1)[0]).join(',');
  return JSON.stringify(out);
})()`;

function httpGet(url) {
  return new Promise((res, rej) => {
    http.get(url, r => { let d = ""; r.on("data", c => d += c); r.on("end", () => res(JSON.parse(d))); }).on("error", rej);
  });
}

async function main() {
  const v = await httpGet("http://127.0.0.1:9333/json/version");
  const ws = new WebSocket(v.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener("open", r));
  let id = 0;
  const pending = new Map();
  const events = [];
  ws.addEventListener("message", ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else events.push(m);
  });
  const send = (method, params, sessionId) => new Promise(res => {
    const mid = ++id;
    pending.set(mid, res);
    ws.send(JSON.stringify({ id: mid, method, params: params || {}, sessionId }));
  });

  const out = {};
  for (const [label, url] of [["live", LIVE], ["reference", REF]]) {
    out[label] = {};
    const t = await send("Target.createTarget", { url: "about:blank" });
    const targetId = t.result.targetId;
    const a = await send("Target.attachToTarget", { targetId, flatten: true });
    const sid = a.result.sessionId;
    await send("Page.enable", {}, sid);
    for (const w of [390, 768, 1440]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: 900, deviceScaleFactor: 1, mobile: w < 768 }, sid);
      await send("Page.navigate", { url }, sid);
      await new Promise(r => setTimeout(r, w === 390 ? 6000 : 3500));
      const r = await send("Runtime.evaluate", { expression: MEASURE, returnByValue: true, awaitPromise: false }, sid);
      out[label][w] = r.result && r.result.result ? JSON.parse(r.result.result.value) : r;
    }
    await send("Target.closeTarget", { targetId });
  }
  console.log(JSON.stringify(out, null, 1));
  ws.close();
}
main().catch(e => { console.error("ERR", e.message); process.exit(1); });
