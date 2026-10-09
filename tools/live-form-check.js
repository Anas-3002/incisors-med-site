/* End-to-end check on the DEPLOYED site: the booking form, the portal form and the mobile
   menu are driven for real and the WhatsApp URL each one produces is read back.
   node tools/live-form-check.js <base-url>                                                  */
const http = require("http");

const BASE = (process.argv[2] || "https://darkcyan-falcon-706043.hostingersite.com").replace(/\/$/, "");

const SCRIPT = `(async () => {
  const R = {};
  const calls = [];
  window.open = function (u) { calls.push(u); return { closed: false }; };

  // booking form
  const form = document.getElementById('booking-form');
  form.querySelector('[name="full_name"]').value = 'Live Test Patient';
  form.querySelector('[name="phone"]').value = '+92 300 0000000';
  form.querySelector('[name="clinic"]').value = 'West End';
  form.querySelector('[name="reason"]').value = 'Cosmetic Veneers';
  form.querySelector('input[value="sleep"]').checked = true;
  form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  R.booking = calls[calls.length - 1] || null;
  R.bookingSuccessVisible = !document.getElementById('booking-success').classList.contains('hidden');

  // clinic selector
  const cards = document.querySelectorAll('.clinic-card');
  cards[2].click();
  R.clinicSelected = document.getElementById('selected-clinic-name').textContent;
  R.clinicInForm = document.getElementById('form-clinic-select').value;

  // insurance checker
  document.getElementById('insurance-carrier').value = 'Aetna PPO';
  document.querySelector('button[onclick="verifyCoverage()"]').click();
  R.insuranceVisible = !document.getElementById('insurance-status').classList.contains('hidden');

  // mobile menu
  const t = document.getElementById('mobile-menu-toggle');
  const m = document.getElementById('mobile-menu');
  t.click();
  R.menuOpens = !m.classList.contains('hidden');
  R.menuAria = t.getAttribute('aria-expanded');
  R.menuIcon = document.getElementById('mobile-menu-icon').textContent;
  t.click();
  R.menuCloses = m.classList.contains('hidden');

  // digest
  document.getElementById('digest-email').value = 'live-test@example.com';
  document.getElementById('digest-submit').click();
  R.digest = calls[calls.length - 1] || null;

  // portal page is checked separately

  // anchors resolve to real elements
  const anchors = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1));
  R.badAnchors = anchors.filter(id => !document.getElementById(id));
  return JSON.stringify(R);
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
  let id = 0; const pending = new Map();
  ws.addEventListener("message", ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
  const send = (method, params, sessionId) => new Promise(res => { const mid = ++id; pending.set(mid, res); ws.send(JSON.stringify({ id: mid, method, params: params || {}, sessionId })); });

  const out = {};
  for (const page of ["", "patient-portal.html"]) {
    const t = await send("Target.createTarget", { url: "about:blank" });
    const a = await send("Target.attachToTarget", { targetId: t.result.targetId, flatten: true });
    const sid = a.result.sessionId;
    await send("Page.enable", {}, sid);
    await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false }, sid);
    await send("Page.navigate", { url: BASE + "/" + page }, sid);
    await new Promise(r => setTimeout(r, 4000));
    if (page === "patient-portal.html") {
      const expr = `(async () => { const calls=[]; window.open=u=>{calls.push(u);return{closed:false};};
        const f=document.getElementById('portal-form');
        f.querySelector('[name="full_name"]').value='Live Portal Tester';
        f.querySelector('[name="phone"]').value='+92 300 1111111';
        f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
        return JSON.stringify({url:calls[calls.length-1]||null, success:!document.getElementById('portal-success').classList.contains('hidden')}); })()`;
      const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sid);
      out.portal = JSON.parse(r.result.result.value);
    } else {
      const r = await send("Runtime.evaluate", { expression: SCRIPT, returnByValue: true, awaitPromise: true }, sid);
      out.home = JSON.parse(r.result.result.value);
    }
    await send("Target.closeTarget", { targetId: t.result.targetId });
  }
  console.log(JSON.stringify(out, null, 1));
  ws.close();
}
main().catch(e => { console.error("ERR", e.message); process.exit(1); });
