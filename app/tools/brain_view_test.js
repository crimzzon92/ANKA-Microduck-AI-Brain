// Checks the brain view's logic without a browser (node tools/brain_view_test.js): demo mode and live mode levels.
const fs = require("fs"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "viz", "index.html"), "utf8");
const js = html.split("<script>")[1].split("</script>")[0];
const el = () => ({ style: {}, classList: { toggle() {} }, appendChild() {}, set innerHTML(v) {}, set textContent(v) {},
                    clientWidth: 900, clientHeight: 500, getContext: () => new Proxy({}, { get: (t, k) =>
                      k === "createRadialGradient" ? () => ({ addColorStop() {} }) : () => {} }) });
global.document = { getElementById: el, createElement: el };
global.window = { addEventListener() {}, devicePixelRatio: 1 };
global.location = { search: process.argv[2] === "demo" ? "?demo" : "", pathname: "/" };
global.history = { replaceState() {} };
global.requestAnimationFrame = () => {};
global.fetch = async () => ({ ok: true, json: async () => JSON.parse(fs.readFileSync(path.join(__dirname, "..", "viz", "activity.json"))) });
global.setTimeout = () => {};
eval(js + `
const now = Date.now() / 1000;
if (demo) {
  const at3 = demoLevels(Math.floor(now / 10) * 10 + 3);
  console.log("DEMO at 3 s:", Object.fromEntries(Object.entries(at3).map(([k, v]) => [k, +v.toFixed(2)])));
} else {
  poll().then(() => setImmediate(() => {
    const L = liveLevels(Date.now() / 1000);
    console.log("LIVE:", Object.fromEntries(Object.entries(L).map(([k, v]) => [k, +v.toFixed(2)])), "| sleep", live.sleep, "| text:", live.text);
  }));
}`);
