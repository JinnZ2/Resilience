import { useState, useCallback, useMemo, useEffect, useRef } from “react”;

// ─── MODEL CORE ───────────────────────────────────────────────
const DEFAULT_PARAMS = {
Ymax: 1.0,
k: 0.15,
alpha0: 0.8,
tauF: 2,
tauAlphaPlus: 8,
tauAlphaMinus: 1.5,
degradeThreshold: 0.65,
reserveInit: 0.30,
consumption: 0.85,
lossBase: 0.05,
ensoAmplitude: 0.6,
ensoPeriod: 7,
hormuzShockSeason: -1,
hormuzDepth: 0.4,
hormuzDuration: 4,
warShockSeason: -1,
warDepth: 0.3,
warDuration: 6,
seasons: 40,
transportCostMult: 0.3,
};

function f_nutrient(F, k) {
return F / (F + k);
}

function g_weather(W, alpha) {
return Math.exp(-alpha * W * W);
}

function ensoForcing(t, amplitude, period) {
return amplitude * Math.sin((2 * Math.PI * t) / period);
}

function fertilizerForcing(t, params) {
let F = 1.0;
if (params.hormuzShockSeason >= 0) {
const dt = t - params.hormuzShockSeason;
if (dt >= 0 && dt < params.hormuzDuration) {
const ramp = 0.5 * (1 - Math.cos((Math.PI * dt) / params.hormuzDuration));
F *= 1 - params.hormuzDepth * (1 - ramp);
}
}
if (params.warShockSeason >= 0) {
const dt = t - params.warShockSeason;
if (dt >= 0 && dt < params.warDuration) {
const ramp = 0.5 * (1 - Math.cos((Math.PI * dt) / params.warDuration));
F *= 1 - params.warDepth * (1 - ramp);
}
}
return F;
}

function simulate(params) {
const N = params.seasons;
const out = {
t: [], Y: [], F: [], W: [], alpha: [], S: [], P: [],
fVal: [], gVal: [], regime: [],
};

let F = 1.0;
let alpha = params.alpha0;
let S = params.reserveInit;

for (let t = 0; t < N; t++) {
const W = ensoForcing(t, params.ensoAmplitude, params.ensoPeriod);
const Fext = fertilizerForcing(t, params);

```
// D_t: desired fertilizer — supply constrained
const D = Math.min(Fext, 1.0);

// relaxation toward D
F = F + (1 / params.tauF) * (D - F);
F = Math.max(0.01, Math.min(1.0, F));

const fv = f_nutrient(F, params.k);
const gv = g_weather(W, alpha);
const Y = params.Ymax * fv * gv;

// transport losses rise when energy costs rise (low Fext proxy)
const L = params.lossBase + params.transportCostMult * (1 - Fext);

// reserves
S = S + Y - params.consumption * Y - L;
S = Math.max(0.0, S);

// price signal (hyperbolic on reserves)
const P = 1 / (S + 0.05);

// asymmetric alpha adaptation
if (Y < params.degradeThreshold) {
  // fast degradation
  alpha = alpha + (1 / params.tauAlphaMinus) * (params.alpha0 * 1.3 - alpha) * (params.degradeThreshold - Y);
} else {
  // slow recovery
  alpha = alpha - (1 / params.tauAlphaPlus) * (alpha - params.alpha0 * 0.7) * (Y - params.degradeThreshold);
}
alpha = Math.max(0.1, Math.min(3.0, alpha));

// regime classification
let regime = "stable";
if (F < 0.55 && Math.abs(W) > 0.3) regime = "bifurcation";
if (F < 0.35 || Y < 0.3) regime = "degraded";

out.t.push(t);
out.Y.push(Y);
out.F.push(F);
out.W.push(W);
out.alpha.push(alpha);
out.S.push(S);
out.P.push(Math.min(P, 20));
out.fVal.push(fv);
out.gVal.push(gv);
out.regime.push(regime);
```

}
return out;
}

// ─── CANVAS RENDERERS ─────────────────────────────────────────

function drawTimeSeries(canvas, data, params) {
if (!canvas) return;
const ctx = canvas.getContext(“2d”);
const W = canvas.width;
const H = canvas.height;
const dpr = window.devicePixelRatio || 1;
canvas.width = W * dpr;
canvas.height = H * dpr;
canvas.style.width = W + “px”;
canvas.style.height = H + “px”;
ctx.scale(dpr, dpr);

ctx.fillStyle = “#0a0e14”;
ctx.fillRect(0, 0, W, H);

const pad = { l: 48, r: 16, t: 24, b: 32 };
const pw = W - pad.l - pad.r;
const ph = H - pad.t - pad.b;
const N = data.t.length;

function tx(i) { return pad.l + (i / (N - 1)) * pw; }
function ty(v, lo, hi) { return pad.t + ph - ((v - lo) / (hi - lo)) * ph; }

// grid
ctx.strokeStyle = “#1a2030”;
ctx.lineWidth = 0.5;
for (let i = 0; i <= 4; i++) {
const y = pad.t + (i / 4) * ph;
ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
}

// regime bands
for (let i = 0; i < N - 1; i++) {
const r = data.regime[i];
if (r === “bifurcation”) ctx.fillStyle = “rgba(255,180,0,0.08)”;
else if (r === “degraded”) ctx.fillStyle = “rgba(255,50,50,0.1)”;
else continue;
ctx.fillRect(tx(i), pad.t, tx(i + 1) - tx(i), ph);
}

// shock markers
ctx.font = “10px monospace”;
ctx.textAlign = “center”;
if (params.hormuzShockSeason >= 0 && params.hormuzShockSeason < N) {
const x = tx(params.hormuzShockSeason);
ctx.strokeStyle = “#ff6b35”;
ctx.lineWidth = 1;
ctx.setLineDash([3, 3]);
ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, pad.t + ph); ctx.stroke();
ctx.setLineDash([]);
ctx.fillStyle = “#ff6b35”;
ctx.fillText(“HORMUZ”, x, pad.t - 4);
}
if (params.warShockSeason >= 0 && params.warShockSeason < N) {
const x = tx(params.warShockSeason);
ctx.strokeStyle = “#e84393”;
ctx.lineWidth = 1;
ctx.setLineDash([3, 3]);
ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, pad.t + ph); ctx.stroke();
ctx.setLineDash([]);
ctx.fillStyle = “#e84393”;
ctx.fillText(“WAR”, x, pad.t - 4);
}

const series = [
{ key: “Y”, color: “#00ff88”, label: “Yield” },
{ key: “F”, color: “#4ecdc4”, label: “Fert” },
{ key: “S”, color: “#ffe66d”, label: “Reserves” },
{ key: “alpha”, color: “#ff6b6b”, label: “α (vuln)” },
];

// normalize each to [0,1] range for display
series.forEach(s => {
const vals = data[s.key];
const lo = Math.min(…vals);
const hi = Math.max(…vals);
ctx.strokeStyle = s.color;
ctx.lineWidth = 1.8;
ctx.beginPath();
for (let i = 0; i < N; i++) {
const x = tx(i);
const y = ty(vals[i], lo - 0.05, hi + 0.05);
if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
}
ctx.stroke();
});

// W as filled area
const Wvals = data.W;
const Wmax = Math.max(…Wvals.map(Math.abs)) + 0.1;
const midY = pad.t + ph / 2;
ctx.fillStyle = “rgba(108,92,231,0.15)”;
ctx.beginPath();
ctx.moveTo(tx(0), midY);
for (let i = 0; i < N; i++) {
ctx.lineTo(tx(i), midY - (Wvals[i] / Wmax) * (ph * 0.3));
}
ctx.lineTo(tx(N - 1), midY);
ctx.closePath();
ctx.fill();
ctx.strokeStyle = “rgba(108,92,231,0.5)”;
ctx.lineWidth = 1;
ctx.beginPath();
for (let i = 0; i < N; i++) {
const x = tx(i);
const y = midY - (Wvals[i] / Wmax) * (ph * 0.3);
if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
}
ctx.stroke();

// legend
ctx.font = “11px monospace”;
ctx.textAlign = “left”;
const lx = pad.l + 8;
series.forEach((s, i) => {
ctx.fillStyle = s.color;
ctx.fillRect(lx, pad.t + 6 + i * 16, 12, 3);
ctx.fillText(s.label, lx + 18, pad.t + 12 + i * 16);
});
ctx.fillStyle = “rgba(108,92,231,0.6)”;
ctx.fillRect(lx, pad.t + 6 + series.length * 16, 12, 3);
ctx.fillText(“ENSO (W)”, lx + 18, pad.t + 12 + series.length * 16);

// axes labels
ctx.fillStyle = “#556677”;
ctx.font = “10px monospace”;
ctx.textAlign = “center”;
for (let i = 0; i < N; i += 5) {
ctx.fillText(i.toString(), tx(i), H - 6);
}
ctx.save();
ctx.translate(12, pad.t + ph / 2);
ctx.rotate(-Math.PI / 2);
ctx.fillText(“normalized”, 0, 0);
ctx.restore();
}

function drawPhase(canvas, data) {
if (!canvas) return;
const ctx = canvas.getContext(“2d”);
const S = Math.min(canvas.clientWidth, canvas.clientHeight);
const dpr = window.devicePixelRatio || 1;
canvas.width = S * dpr;
canvas.height = S * dpr;
canvas.style.width = S + “px”;
canvas.style.height = S + “px”;
ctx.scale(dpr, dpr);

ctx.fillStyle = “#0a0e14”;
ctx.fillRect(0, 0, S, S);

const pad = 44;
const pw = S - 2 * pad;

function tx(F) { return pad + F * pw; }
function ty(W) { return pad + pw - ((W + 1) / 2) * pw; }

// regime zones (approximate)
// bifurcation zone
ctx.fillStyle = “rgba(255,180,0,0.06)”;
ctx.fillRect(tx(0.35), ty(1), tx(0.55) - tx(0.35), ty(-1) - ty(1));
// degraded zone
ctx.fillStyle = “rgba(255,50,50,0.06)”;
ctx.fillRect(tx(0), ty(1), tx(0.35) - tx(0), ty(-1) - ty(1));

// grid
ctx.strokeStyle = “#1a2030”;
ctx.lineWidth = 0.5;
for (let i = 0; i <= 10; i++) {
const x = pad + (i / 10) * pw;
ctx.beginPath(); ctx.moveTo(x, pad); ctx.lineTo(x, pad + pw); ctx.stroke();
ctx.beginPath(); ctx.moveTo(pad, x); ctx.lineTo(pad + pw, x); ctx.stroke();
}

// bifurcation line
ctx.strokeStyle = “rgba(255,180,0,0.4)”;
ctx.lineWidth = 1;
ctx.setLineDash([4, 4]);
ctx.beginPath();
ctx.moveTo(tx(0.55), ty(-1));
ctx.lineTo(tx(0.55), ty(1));
ctx.stroke();
ctx.setLineDash([]);

// trajectory
const N = data.t.length;
for (let i = 1; i < N; i++) {
const age = i / N;
const r = data.regime[i];
let color;
if (r === “degraded”) color = `rgba(255,80,80,${0.3 + age * 0.7})`;
else if (r === “bifurcation”) color = `rgba(255,200,0,${0.3 + age * 0.7})`;
else color = `rgba(0,255,136,${0.2 + age * 0.6})`;

```
ctx.strokeStyle = color;
ctx.lineWidth = 1 + age * 1.5;
ctx.beginPath();
ctx.moveTo(tx(data.F[i - 1]), ty(data.W[i - 1]));
ctx.lineTo(tx(data.F[i]), ty(data.W[i]));
ctx.stroke();
```

}

// start/end markers
ctx.fillStyle = “#ffffff”;
ctx.beginPath();
ctx.arc(tx(data.F[0]), ty(data.W[0]), 4, 0, Math.PI * 2);
ctx.fill();
ctx.fillStyle = “#ff3333”;
ctx.beginPath();
ctx.arc(tx(data.F[N - 1]), ty(data.W[N - 1]), 5, 0, Math.PI * 2);
ctx.fill();

// labels
ctx.fillStyle = “#556677”;
ctx.font = “10px monospace”;
ctx.textAlign = “center”;
ctx.fillText(“F (fertilizer)”, pad + pw / 2, S - 6);
ctx.save();
ctx.translate(10, pad + pw / 2);
ctx.rotate(-Math.PI / 2);
ctx.fillText(“W (weather stress)”, 0, 0);
ctx.restore();

// zone labels
ctx.font = “9px monospace”;
ctx.fillStyle = “rgba(0,255,136,0.3)”;
ctx.fillText(“STABLE”, tx(0.78), pad + 14);
ctx.fillStyle = “rgba(255,180,0,0.3)”;
ctx.fillText(“BIFURCATION”, tx(0.45), pad + 14);
ctx.fillStyle = “rgba(255,50,50,0.3)”;
ctx.fillText(“DEGRADED”, tx(0.17), pad + 14);

ctx.fillStyle = “#ffffff”;
ctx.font = “9px monospace”;
ctx.fillText(“● start”, tx(data.F[0]) + 20, ty(data.W[0]));
ctx.fillStyle = “#ff3333”;
ctx.fillText(“● end”, tx(data.F[N - 1]) + 20, ty(data.W[N - 1]));
}

function drawPrice(canvas, data) {
if (!canvas) return;
const ctx = canvas.getContext(“2d”);
const W = canvas.width;
const H = canvas.height;
const dpr = window.devicePixelRatio || 1;
canvas.width = canvas.clientWidth * dpr;
canvas.height = canvas.clientHeight * dpr;
const cw = canvas.clientWidth;
const ch = canvas.clientHeight;
canvas.style.width = cw + “px”;
canvas.style.height = ch + “px”;
ctx.scale(dpr, dpr);

ctx.fillStyle = “#0a0e14”;
ctx.fillRect(0, 0, cw, ch);

const pad = { l: 48, r: 16, t: 20, b: 28 };
const pw = cw - pad.l - pad.r;
const ph = ch - pad.t - pad.b;
const N = data.t.length;

const Pmax = Math.max(…data.P);
function tx(i) { return pad.l + (i / (N - 1)) * pw; }
function ty(v) { return pad.t + ph - (v / (Pmax + 1)) * ph; }

// danger zone
const dangerY = ty(5);
ctx.fillStyle = “rgba(255,50,50,0.05)”;
ctx.fillRect(pad.l, pad.t, pw, dangerY - pad.t);

// price line
ctx.strokeStyle = “#ff6b6b”;
ctx.lineWidth = 2;
ctx.beginPath();
for (let i = 0; i < N; i++) {
const x = tx(i);
const y = ty(data.P[i]);
if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
}
ctx.stroke();

// fill under
ctx.fillStyle = “rgba(255,107,107,0.1)”;
ctx.beginPath();
ctx.moveTo(tx(0), ty(0));
for (let i = 0; i < N; i++) ctx.lineTo(tx(i), ty(data.P[i]));
ctx.lineTo(tx(N - 1), ty(0));
ctx.closePath();
ctx.fill();

ctx.fillStyle = “#556677”;
ctx.font = “10px monospace”;
ctx.textAlign = “center”;
ctx.fillText(“season”, pad.l + pw / 2, ch - 4);
ctx.save();
ctx.translate(12, pad.t + ph / 2);
ctx.rotate(-Math.PI / 2);
ctx.fillText(“price ∝ 1/S”, 0, 0);
ctx.restore();

ctx.fillStyle = “#ff6b6b”;
ctx.font = “11px monospace”;
ctx.textAlign = “left”;
ctx.fillText(“Price Signal”, pad.l + 8, pad.t + 14);
}

// ─── SLIDER COMPONENT ────────────────────────────────────────

function Slider({ label, value, min, max, step, onChange, color = “#4ecdc4”, unit = “” }) {
const pct = ((value - min) / (max - min)) * 100;
return (
<div style={{ marginBottom: 10 }}>
<div style={{
display: “flex”, justifyContent: “space-between”, alignItems: “baseline”,
fontSize: 11, fontFamily: “monospace”, color: “#889”
}}>
<span>{label}</span>
<span style={{ color, fontWeight: 600 }}>{typeof value === ‘number’ ? (Number.isInteger(step) ? value : value.toFixed(2)) : value}{unit}</span>
</div>
<input
type=“range” min={min} max={max} step={step} value={value}
onChange={e => onChange(parseFloat(e.target.value))}
style={{
width: “100%”, height: 4, appearance: “none”, background: `linear-gradient(to right, ${color} ${pct}%, #1a2030 ${pct}%)`,
borderRadius: 2, outline: “none”, cursor: “pointer”,
accentColor: color,
}}
/>
</div>
);
}

// ─── MAIN APP ─────────────────────────────────────────────────

export default function FoodSystemSimulator() {
const [params, setParams] = useState(DEFAULT_PARAMS);
const [activeTab, setActiveTab] = useState(“forcing”);
const tsRef = useRef(null);
const phRef = useRef(null);
const prRef = useRef(null);

const data = useMemo(() => simulate(params), [params]);

const update = useCallback((key, val) => {
setParams(p => ({ …p, [key]: val }));
}, []);

useEffect(() => {
drawTimeSeries(tsRef.current, data, params);
drawPhase(phRef.current, data);
drawPrice(prRef.current, data);
}, [data, params]);

// summary stats
const minY = Math.min(…data.Y).toFixed(2);
const minF = Math.min(…data.F).toFixed(2);
const maxAlpha = Math.max(…data.alpha).toFixed(2);
const maxP = Math.max(…data.P).toFixed(1);
const degradedSeasons = data.regime.filter(r => r === “degraded”).length;
const bifurcSeasons = data.regime.filter(r => r === “bifurcation”).length;

const tabStyle = (t) => ({
padding: “6px 14px”,
fontSize: 11,
fontFamily: “monospace”,
background: activeTab === t ? “#1a2535” : “transparent”,
color: activeTab === t ? “#4ecdc4” : “#556”,
border: “none”,
borderBottom: activeTab === t ? “2px solid #4ecdc4” : “2px solid transparent”,
cursor: “pointer”,
transition: “all 0.2s”,
});

const statBox = (label, val, color) => (
<div style={{
flex: 1, padding: “8px 10px”, background: “#0d1219”,
borderLeft: `3px solid ${color}`, minWidth: 90,
}}>
<div style={{ fontSize: 9, fontFamily: “monospace”, color: “#556”, textTransform: “uppercase” }}>{label}</div>
<div style={{ fontSize: 16, fontFamily: “monospace”, color, fontWeight: 700 }}>{val}</div>
</div>
);

return (
<div style={{
background: “#0a0e14”, color: “#ccd”, minHeight: “100vh”,
fontFamily: “‘JetBrains Mono’, ‘Fira Code’, monospace”, padding: 16,
}}>
<div style={{ maxWidth: 900, margin: “0 auto” }}>
{/* Header */}
<div style={{ marginBottom: 16, borderBottom: “1px solid #1a2030”, paddingBottom: 12 }}>
<h1 style={{
fontSize: 16, fontWeight: 700, color: “#00ff88”, margin: 0,
letterSpacing: “0.05em”,
}}>
FOOD SYSTEM RESILIENCE MODEL
</h1>
<div style={{ fontSize: 10, color: “#445”, marginTop: 4 }}>
Y = Ymax · f(F) · g(W)  |  asymmetric α  |  reserves buffer  |  parametric instability
</div>
</div>

```
    {/* Stats bar */}
    <div style={{
      display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap",
    }}>
      {statBox("min yield", minY, "#00ff88")}
      {statBox("min fert", minF, "#4ecdc4")}
      {statBox("max α", maxAlpha, "#ff6b6b")}
      {statBox("max price", maxP + "×", "#ffe66d")}
      {statBox("degraded", degradedSeasons + "s", degradedSeasons > 0 ? "#ff4444" : "#334")}
      {statBox("bifurc", bifurcSeasons + "s", bifurcSeasons > 0 ? "#ffaa00" : "#334")}
    </div>

    {/* Main viz */}
    <div style={{ marginBottom: 12 }}>
      <canvas ref={tsRef} width={880} height={280}
        style={{ width: "100%", height: 280, borderRadius: 4, border: "1px solid #1a2030" }} />
    </div>

    {/* Phase + Price side by side */}
    <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
      <div style={{ flex: "1 1 280px", minWidth: 260 }}>
        <canvas ref={phRef} width={300} height={300}
          style={{ width: "100%", aspectRatio: "1", borderRadius: 4, border: "1px solid #1a2030" }} />
      </div>
      <div style={{ flex: "1 1 280px", minWidth: 260 }}>
        <canvas ref={prRef} width={500} height={300}
          style={{ width: "100%", height: 300, borderRadius: 4, border: "1px solid #1a2030" }} />
      </div>
    </div>

    {/* Control panel */}
    <div style={{
      background: "#0d1219", borderRadius: 6, border: "1px solid #1a2030",
      padding: 12,
    }}>
      <div style={{ display: "flex", gap: 0, borderBottom: "1px solid #1a2030", marginBottom: 12 }}>
        <button style={tabStyle("forcing")} onClick={() => setActiveTab("forcing")}>FORCING</button>
        <button style={tabStyle("response")} onClick={() => setActiveTab("response")}>RESPONSE</button>
        <button style={tabStyle("adaptation")} onClick={() => setActiveTab("adaptation")}>ADAPTATION</button>
        <button style={tabStyle("reserves")} onClick={() => setActiveTab("reserves")}>RESERVES</button>
      </div>

      {activeTab === "forcing" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          <div>
            <div style={{ fontSize: 10, color: "#4ecdc4", marginBottom: 8, textTransform: "uppercase" }}>ENSO</div>
            <Slider label="amplitude" value={params.ensoAmplitude} min={0} max={1.5} step={0.05} onChange={v => update("ensoAmplitude", v)} />
            <Slider label="period (seasons)" value={params.ensoPeriod} min={2} max={15} step={1} onChange={v => update("ensoPeriod", v)} />
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#ff6b35", marginBottom: 8, textTransform: "uppercase" }}>HORMUZ SHOCK</div>
            <Slider label="season" value={params.hormuzShockSeason} min={-1} max={params.seasons - 1} step={1} onChange={v => update("hormuzShockSeason", v)} color="#ff6b35" />
            <Slider label="depth" value={params.hormuzDepth} min={0} max={0.8} step={0.05} onChange={v => update("hormuzDepth", v)} color="#ff6b35" />
            <Slider label="duration" value={params.hormuzDuration} min={1} max={12} step={1} onChange={v => update("hormuzDuration", v)} color="#ff6b35" />
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#e84393", marginBottom: 8, textTransform: "uppercase" }}>WAR / SUPPLY SHOCK</div>
            <Slider label="season" value={params.warShockSeason} min={-1} max={params.seasons - 1} step={1} onChange={v => update("warShockSeason", v)} color="#e84393" />
            <Slider label="depth" value={params.warDepth} min={0} max={0.8} step={0.05} onChange={v => update("warDepth", v)} color="#e84393" />
            <Slider label="duration" value={params.warDuration} min={1} max={12} step={1} onChange={v => update("warDuration", v)} color="#e84393" />
          </div>
        </div>
      )}

      {activeTab === "response" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          <div>
            <div style={{ fontSize: 10, color: "#00ff88", marginBottom: 8, textTransform: "uppercase" }}>YIELD FUNCTION</div>
            <Slider label="Ymax" value={params.Ymax} min={0.5} max={1.5} step={0.05} onChange={v => update("Ymax", v)} color="#00ff88" />
            <Slider label="k (fert sensitivity)" value={params.k} min={0.05} max={0.5} step={0.01} onChange={v => update("k", v)} color="#00ff88" />
            <Slider label="α₀ (base weather vuln)" value={params.alpha0} min={0.1} max={2.0} step={0.05} onChange={v => update("alpha0", v)} color="#ff6b6b" />
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#4ecdc4", marginBottom: 8, textTransform: "uppercase" }}>FERTILIZER DYNAMICS</div>
            <Slider label="τ_F (relaxation)" value={params.tauF} min={0.5} max={8} step={0.5} onChange={v => update("tauF", v)} />
          </div>
        </div>
      )}

      {activeTab === "adaptation" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          <div>
            <div style={{ fontSize: 10, color: "#ff6b6b", marginBottom: 8, textTransform: "uppercase" }}>ASYMMETRIC α DYNAMICS</div>
            <Slider label="τ_α⁺ (recovery — slow)" value={params.tauAlphaPlus} min={2} max={20} step={1} onChange={v => update("tauAlphaPlus", v)} color="#00ff88" />
            <Slider label="τ_α⁻ (degrade — fast)" value={params.tauAlphaMinus} min={0.5} max={5} step={0.25} onChange={v => update("tauAlphaMinus", v)} color="#ff6b6b" />
            <Slider label="degrade threshold Y" value={params.degradeThreshold} min={0.3} max={0.9} step={0.05} onChange={v => update("degradeThreshold", v)} color="#ffe66d" />
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#889", marginBottom: 8, textTransform: "uppercase" }}>THE RATCHET</div>
            <div style={{ fontSize: 10, color: "#556", lineHeight: 1.5 }}>
              τ_α⁻ {"<"} τ_α⁺ = ratchet effect<br />
              each bad season does damage<br />
              that multiple good seasons<br />
              cannot undo.<br /><br />
              ratio: {(params.tauAlphaPlus / params.tauAlphaMinus).toFixed(1)}× asymmetry
            </div>
          </div>
        </div>
      )}

      {activeTab === "reserves" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          <div>
            <div style={{ fontSize: 10, color: "#ffe66d", marginBottom: 8, textTransform: "uppercase" }}>RESERVES BUFFER</div>
            <Slider label="initial reserves" value={params.reserveInit} min={0} max={1.0} step={0.05} onChange={v => update("reserveInit", v)} color="#ffe66d" />
            <Slider label="consumption fraction" value={params.consumption} min={0.5} max={1.0} step={0.01} onChange={v => update("consumption", v)} color="#ffe66d" />
            <Slider label="base loss rate" value={params.lossBase} min={0} max={0.2} step={0.01} onChange={v => update("lossBase", v)} color="#ffe66d" />
            <Slider label="transport cost mult" value={params.transportCostMult} min={0} max={0.8} step={0.05} onChange={v => update("transportCostMult", v)} color="#ffe66d" />
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#889", marginBottom: 8, textTransform: "uppercase" }}>PRICE CASCADE</div>
            <div style={{ fontSize: 10, color: "#556", lineHeight: 1.5 }}>
              P ∝ 1/S — hyperbolic<br />
              low stocks = price explosion<br /><br />
              Hormuz hits S from both sides:<br />
              — F drops → Y drops → less in<br />
              — transport cost → L rises → more out<br /><br />
              parametric instability:<br />
              forcing changes the restoring<br />
              force constant, not just the<br />
              displacement
            </div>
          </div>
        </div>
      )}

      {/* Simulation length */}
      <div style={{ marginTop: 16, borderTop: "1px solid #1a2030", paddingTop: 12 }}>
        <Slider label="simulation length (seasons)" value={params.seasons} min={10} max={80} step={1} onChange={v => update("seasons", v)} color="#889" />
        <button
          onClick={() => setParams(DEFAULT_PARAMS)}
          style={{
            background: "#1a2030", border: "1px solid #2a3040", color: "#889",
            padding: "6px 16px", fontSize: 10, fontFamily: "monospace",
            borderRadius: 3, cursor: "pointer", marginTop: 4,
          }}
        >
          RESET DEFAULTS
        </button>
      </div>
    </div>

    {/* Model equations footer */}
    <div style={{
      marginTop: 16, padding: 12, background: "#0d1219",
      borderRadius: 4, border: "1px solid #1a2030",
      fontSize: 9, color: "#334", fontFamily: "monospace", lineHeight: 1.6,
    }}>
      Y = Ymax · F/(F+k) · exp(-αW²) &nbsp;|&nbsp;
      F(t+1) = F + (D-F)/τF &nbsp;|&nbsp;
      α(t+1) = α ± (1/τ±) · h(Y) &nbsp;|&nbsp;
      S(t+1) = S + Y - cY - L &nbsp;|&nbsp;
      P ∝ 1/(S+ε) &nbsp;|&nbsp;
      CC0
    </div>
  </div>
</div>
```

);
}
