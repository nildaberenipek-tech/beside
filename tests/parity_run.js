// Feeds a 25 Hz signal (JSON file) through app/detector.js and prints every window as JSON.
const fs = require("fs");
const { Detector } = require("../app/detector.js");
const [sigPath, modelPath] = process.argv.slice(2);
const sig = JSON.parse(fs.readFileSync(sigPath, "utf8"));
const model = JSON.parse(fs.readFileSync(modelPath, "utf8"));
const rows = [];
const d = new Detector(model, { onWindow: w => rows.push({ t: w.t, p: w.p, ...w.features, ...Object.fromEntries(Object.entries(w.base).map(([k, v]) => ["b_" + k, v])), alarm: w.alarm }) });
for (let i = 0; i < sig.x.length; i++) d.pushSample(sig.x[i], sig.y[i], sig.z[i]);
fs.writeFileSync(sigPath.replace(".json", "_js.json"), JSON.stringify(rows));
console.log(rows.length, "windows");
