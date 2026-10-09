/* node tools/shot.js <url> <width> <out.png>  - full-page screenshot over CDP */
const http = require("http");
const fs = require("fs");

const [url, width, out] = process.argv.slice(2);

function httpGet(u) {
  return new Promise((res, rej) => {
    http.get(u, r => { let d = ""; r.on("data", c => d += c); r.on("end", () => res(JSON.parse(d))); }).on("error", rej);
  });
}

async function main() {
  const v = await httpGet("http://127.0.0.1:9333/json/version");
  const ws = new WebSocket(v.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener("open", r));
  let id = 0; const pending = new Map();
  ws.addEventListener("message", ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
  const send = (method, params, sessionId) => new Promise(res => { const mid = ++id; pending.set(mid, res); ws.send(JSON.stringify({ id: mid, method, params: params || {}, sessionId })); });

  const t = await send("Target.createTarget", { url: "about:blank" });
  const a = await send("Target.attachToTarget", { targetId: t.result.targetId, flatten: true });
  const sid = a.result.sessionId;
  await send("Page.enable", {}, sid);
  await send("Emulation.setDeviceMetricsOverride", { width: Number(width), height: 900, deviceScaleFactor: 1, mobile: Number(width) < 768 }, sid);
  await send("Page.navigate", { url }, sid);
  await new Promise(r => setTimeout(r, 7000));
  const h = await send("Runtime.evaluate", { expression: "document.documentElement.scrollHeight", returnByValue: true }, sid);
  const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: Number(width), height: h.result.result.value, scale: 0.5 } }, sid);
  fs.writeFileSync(out, Buffer.from(shot.result.data, "base64"));
  console.log(out, fs.statSync(out).size, "bytes, page height", h.result.result.value);
  ws.close();
}
main().catch(e => { console.error("ERR", e.message); process.exit(1); });
