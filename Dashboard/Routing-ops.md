import { useState, useMemo, useCallback } from “react”;

const DOMAIN_COLORS = {
R: { bg: “#FF6B35”, fg: “#FFF”, label: “Route” },
W: { bg: “#4FC3F7”, fg: “#000”, label: “Weather” },
C: { bg: “#AB47BC”, fg: “#FFF”, label: “Comms” },
F: { bg: “#FF8F00”, fg: “#000”, label: “Fuel” },
L: { bg: “#00E676”, fg: “#000”, label: “Load” },
T: { bg: “#EF5350”, fg: “#FFF”, label: “Time/HOS” },
I: { bg: “#78909C”, fg: “#FFF”, label: “Infra” },
N: { bg: “#FFD740”, fg: “#000”, label: “Node” },
};

const DTag = ({ d }) => {
const c = DOMAIN_COLORS[d];
return c ? (
<span style={{
display: “inline-block”, background: c.bg, color: c.fg,
borderRadius: 3, padding: “0px 5px”, fontSize: 10,
fontWeight: 700, fontFamily: “monospace”, marginRight: 3,
}}>[{d}]</span>
) : null;
};

// ── SYSTEM STATE ENGINE ──
const SEGMENTS = [
{ id: 1, from: “Tomah”, to: “Black River Falls”, dist: 45, route: “I-94/US-12”, baseTime: 0.75, roadClass: “interstate”, commsLevel: 3, weatherBase: 1, nodes: [“Tomah (full)”, “BRF (full)”] },
{ id: 2, from: “Black River Falls”, to: “Eau Claire”, dist: 60, route: “I-94”, baseTime: 1.0, roadClass: “interstate”, commsLevel: 3, weatherBase: 1.5, nodes: [“Osseo”, “Eau Claire (full)”] },
{ id: 3, from: “Eau Claire”, to: “Chippewa Falls”, dist: 15, route: “US-53/WI-29”, baseTime: 0.3, roadClass: “us-highway”, commsLevel: 3, weatherBase: 1, nodes: [“Chippewa Falls”] },
{ id: 4, from: “Chippewa Falls”, to: “Ladysmith”, dist: 45, route: “WI-27”, baseTime: 0.85, roadClass: “state-highway”, commsLevel: 2, weatherBase: 2, nodes: [“Cornell (limited)”] },
{ id: 5, from: “Ladysmith”, to: “Rice Lake”, dist: 30, route: “WI-27/US-8”, baseTime: 0.6, roadClass: “state-highway”, commsLevel: 2, weatherBase: 2, nodes: [“Ladysmith (limited)”] },
{ id: 6, from: “Rice Lake”, to: “Hayward”, dist: 35, route: “WI-48/US-63”, baseTime: 0.7, roadClass: “state-highway”, commsLevel: 1, weatherBase: 2.5, nodes: [“Hayward (limited)”] },
{ id: 7, from: “Hayward”, to: “Superior”, dist: 75, route: “US-63/US-2”, baseTime: 1.4, roadClass: “us-highway”, commsLevel: 1, weatherBase: 3, nodes: [“Solon Springs (emergency)”] },
];

const GATES = [
{ id: 1, name: “Tomah”, segment: 0, description: “Full corridor assessment. Abort costs nothing.” },
{ id: 2, name: “Eau Claire”, segment: 2, description: “Check weather Seg 4–7, HOS remaining, fuel. Last full-service fallback.” },
{ id: 3, name: “Rice Lake”, segment: 5, description: “Final go/no-go for Superior leg. If no-go, hold here.” },
{ id: 4, name: “Hayward”, segment: 6, description: “Point of commitment. Past here → must reach Superior or roadside.” },
];

const computeState = (inputs) => {
const { currentSegment, hosRemaining, fuelLevel, reeferHours, weatherSeverity, season, roadClosures } = inputs;

// Time needed to complete from current position
const remainingSegments = SEGMENTS.filter(s => s.id >= currentSegment);
const weatherMultiplier = weatherSeverity === 0 ? 1.0 : weatherSeverity === 1 ? 1.15 : weatherSeverity === 2 ? 1.4 : 1.8;
const timeNeeded = remainingSegments.reduce((sum, s) => sum + s.baseTime * weatherMultiplier, 0);
const distRemaining = remainingSegments.reduce((sum, s) => sum + s.dist, 0);

// Fuel analysis
const fuelNeeded = distRemaining / 6.5; // worst-case MPG
const idleBurnRate = season === “winter” ? 1.5 : season === “shoulder” ? 0.8 : 0.3;
const fuelMargin = fuelLevel - fuelNeeded;

// HOS analysis
const hosMargin = hosRemaining - timeNeeded;
const hosBuffer = hosMargin;

// Comms state at current position
const currentSeg = SEGMENTS.find(s => s.id === currentSegment) || SEGMENTS[0];
const commsState = currentSeg.commsLevel;

// Reefer analysis
const reeferCritical = reeferHours < timeNeeded;

// Domain stress levels (0-3: nominal, caution, warning, critical)
const stress = {};
stress.T = hosBuffer < 0 ? 3 : hosBuffer < 1 ? 2 : hosBuffer < 2 ? 1 : 0;
stress.F = fuelMargin < 0 ? 3 : fuelMargin < 10 ? 2 : fuelMargin < 20 ? 1 : 0;
stress.W = weatherSeverity;
stress.C = commsState >= 3 ? 0 : commsState === 2 ? 1 : 2;
stress.L = reeferCritical ? (reeferHours < 1 ? 3 : 2) : reeferHours < timeNeeded + 2 ? 1 : 0;
stress.R = roadClosures.length > 0 ? 2 : weatherSeverity >= 2 ? 1 : 0;
stress.N = currentSegment >= 6 ? (weatherSeverity >= 2 ? 3 : 2) : currentSegment >= 4 ? 1 : 0;
stress.I = season === “shoulder” ? 1 : 0;

const maxStress = Math.max(…Object.values(stress));
const criticalDomains = Object.entries(stress).filter(([, v]) => v >= 2).map(([k]) => k);
const activeTensionCount = criticalDomains.length;

// Gate status
const gateStatus = GATES.map(g => {
const isPast = currentSegment > g.segment + 1;
const isCurrent = currentSegment === g.segment || currentSegment === g.segment + 1;
let recommendation = “GO”;
if (g.id >= 3 && (stress.T >= 2 || stress.W >= 2 || activeTensionCount >= 3)) recommendation = “HOLD”;
if (g.id >= 3 && (stress.T >= 3 || activeTensionCount >= 4)) recommendation = “NO-GO”;
if (g.id === 4 && stress.W >= 3) recommendation = “NO-GO”;
return { …g, isPast, isCurrent, recommendation };
});

// Tension lines active
const tensionLines = [];
if (criticalDomains.length >= 3 && currentSegment >= 5) {
tensionLines.push({ id: “northern-convergence”, title: “NORTHERN CONVERGENCE”, severity: 3, domains: criticalDomains });
}
if (stress.T >= 2 && currentSegment <= 3) {
tensionLines.push({ id: “dock-trap”, title: “DOCK TIME TRAP”, severity: 2, domains: [“T”, “R”] });
}
if (stress.F >= 1 && stress.W >= 1 && season === “winter”) {
tensionLines.push({ id: “idle-paradox”, title: “IDLE SHUTOFF PARADOX”, severity: stress.F + stress.W >= 4 ? 3 : 2, domains: [“F”, “W”, “T”] });
}
if (currentSegment >= 4 && stress.C >= 1) {
tensionLines.push({ id: “comms-cliff”, title: “COMMS CLIFF”, severity: stress.C >= 2 ? 3 : 2, domains: [“C”, “N”, “T”] });
}
if (stress.L >= 2) {
tensionLines.push({ id: “reefer-cascade”, title: “REEFER CASCADE”, severity: stress.L, domains: [“L”, “F”, “T”, “C”] });
}

// Overall system state
let systemState = “NOMINAL”;
let systemColor = “#00E676”;
if (maxStress >= 1) { systemState = “CAUTION”; systemColor = “#FFD740”; }
if (maxStress >= 2 || activeTensionCount >= 2) { systemState = “WARNING”; systemColor = “#FF8F00”; }
if (maxStress >= 3 || activeTensionCount >= 3) { systemState = “CRITICAL”; systemColor = “#EF5350”; }

return {
timeNeeded: Math.round(timeNeeded * 10) / 10,
distRemaining,
fuelNeeded: Math.round(fuelNeeded),
fuelMargin: Math.round(fuelMargin),
hosBuffer: Math.round(hosBuffer * 10) / 10,
idleBurnRate,
stress,
gateStatus,
tensionLines,
systemState,
systemColor,
criticalDomains,
reeferCritical,
weatherMultiplier,
commsState,
};
};

// ── UI COMPONENTS ──
const Slider = ({ label, value, onChange, min, max, step, unit, color = “#00ff88”, marks }) => (

  <div style={{ margin: "6px 0" }}>
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "baseline",
      fontSize: 11, fontFamily: "monospace", color: "#888", marginBottom: 2,
    }}>
      <span>{label}</span>
      <span style={{ color, fontWeight: 700, fontSize: 13 }}>{value}{unit}</span>
    </div>
    <input
      type="range" min={min} max={max} step={step} value={value}
      onChange={e => onChange(parseFloat(e.target.value))}
      style={{
        width: "100%", height: 4, appearance: "none", background: "#222",
        borderRadius: 2, outline: "none",
        accentColor: color,
      }}
    />
    {marks && (
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: "#555", fontFamily: "monospace", marginTop: 1 }}>
        {marks.map((m, i) => <span key={i}>{m}</span>)}
      </div>
    )}
  </div>
);

const SelectInput = ({ label, value, onChange, options }) => (

  <div style={{ margin: "6px 0" }}>
    <div style={{ fontSize: 11, fontFamily: "monospace", color: "#888", marginBottom: 2 }}>{label}</div>
    <div style={{ display: "flex", gap: 4 }}>
      {options.map(o => (
        <button key={o.value} onClick={() => onChange(o.value)} style={{
          flex: 1, padding: "4px 6px", fontSize: 10, fontFamily: "monospace",
          background: value === o.value ? (o.color || "#FFD740") + "33" : "#111",
          border: `1px solid ${value === o.value ? (o.color || "#FFD740") : "#333"}`,
          color: value === o.value ? (o.color || "#FFD740") : "#666",
          borderRadius: 3, cursor: "pointer", fontWeight: value === o.value ? 700 : 400,
        }}>{o.label}</button>
      ))}
    </div>
  </div>
);

const StressBar = ({ domain, level }) => {
const colors = [”#00E676”, “#FFD740”, “#FF8F00”, “#EF5350”];
const labels = [“NOM”, “CAU”, “WRN”, “CRT”];
const dc = DOMAIN_COLORS[domain];
return (
<div style={{
display: “flex”, alignItems: “center”, gap: 6, padding: “3px 0”,
fontFamily: “monospace”, fontSize: 11,
}}>
<DTag d={domain} />
<div style={{ flex: 1, display: “flex”, gap: 2, height: 8 }}>
{[0, 1, 2, 3].map(i => (
<div key={i} style={{
flex: 1, height: “100%”, borderRadius: 1,
background: i <= level ? colors[level] : “#1a1a1a”,
opacity: i <= level ? 1 : 0.3,
transition: “all 0.3s”,
}} />
))}
</div>
<span style={{
color: colors[level], fontWeight: 700, fontSize: 10, minWidth: 28, textAlign: “right”,
}}>{labels[level]}</span>
</div>
);
};

const GateIndicator = ({ gate, onClick }) => {
const colors = { “GO”: “#00E676”, “HOLD”: “#FFD740”, “NO-GO”: “#EF5350” };
const c = colors[gate.recommendation];
return (
<button onClick={onClick} style={{
display: “flex”, alignItems: “center”, gap: 8, padding: “6px 10px”,
background: gate.isCurrent ? c + “15” : “#0a0a0a”,
border: `1px solid ${gate.isPast ? "#333" : c}`,
borderRadius: 4, cursor: “pointer”, width: “100%”,
opacity: gate.isPast ? 0.4 : 1,
marginBottom: 4,
}}>
<div style={{
width: 10, height: 10, borderRadius: “50%”,
background: gate.isPast ? “#333” : c,
boxShadow: gate.isCurrent ? `0 0 8px ${c}` : “none”,
}} />
<div style={{ flex: 1, textAlign: “left” }}>
<div style={{
fontSize: 11, fontFamily: “monospace”, fontWeight: 700,
color: gate.isPast ? “#555” : “#ccc”,
}}>GATE {gate.id}: {gate.name}</div>
<div style={{ fontSize: 9, fontFamily: “monospace”, color: “#666” }}>{gate.description}</div>
</div>
<div style={{
fontSize: 11, fontFamily: “monospace”, fontWeight: 700,
color: gate.isPast ? “#555” : c,
padding: “2px 8px”, border: `1px solid ${gate.isPast ? "#333" : c}`,
borderRadius: 3,
}}>{gate.isPast ? “PAST” : gate.recommendation}</div>
</button>
);
};

const TensionAlert = ({ tension }) => {
const sevColors = { 1: “#FFD740”, 2: “#FF8F00”, 3: “#EF5350” };
const c = sevColors[tension.severity] || “#FF8F00”;
return (
<div style={{
background: “#1a0a0a”, border: `1px solid ${c}`,
borderLeft: `3px solid ${c}`, borderRadius: 4,
padding: “6px 10px”, margin: “4px 0”,
animation: tension.severity >= 3 ? “pulse 2s infinite” : “none”,
}}>
<div style={{
display: “flex”, alignItems: “center”, gap: 6,
fontSize: 11, fontFamily: “monospace”, fontWeight: 700, color: c,
}}>
{tension.severity >= 3 ? “🔴” : tension.severity >= 2 ? “🟠” : “🟡”} {tension.title}
<span style={{ marginLeft: “auto”, display: “flex”, gap: 2 }}>
{tension.domains.map(d => <DTag key={d} d={d} />)}
</span>
</div>
</div>
);
};

// ── CORRIDOR MAP ──
const LiveCorridorMap = ({ currentSegment, state }) => {
const positions = [
{ id: 1, label: “TOMAH”, x: 60, y: 340 },
{ id: 2, label: “BRF”, x: 90, y: 280 },
{ id: 3, label: “EAU CLAIRE”, x: 120, y: 210 },
{ id: 4, label: “CHIPPEWA”, x: 170, y: 185 },
{ id: 5, label: “LADYSMITH”, x: 195, y: 135 },
{ id: 6, label: “RICE LAKE”, x: 175, y: 90 },
{ id: 7, label: “HAYWARD”, x: 135, y: 55 },
{ id: 8, label: “SUPERIOR”, x: 100, y: 15 },
];

const getStressColor = (segId) => {
const seg = SEGMENTS.find(s => s.id === segId);
if (!seg) return “#333”;
const wRisk = seg.weatherBase * (state.weatherMultiplier > 1.3 ? 1.5 : 1);
if (wRisk >= 3) return “#EF5350”;
if (wRisk >= 2) return “#FF8F00”;
if (wRisk >= 1.5) return “#FFD740”;
return “#4FC3F7”;
};

return (
<svg viewBox=”-10 -5 300 370” style={{
width: “100%”, maxHeight: 340, background: “#060610”,
borderRadius: 4, border: “1px solid #1a1a1a”,
}}>
<style>{`@keyframes truckPulse { 0%,100%{r:6} 50%{r:9} }`}</style>
{SEGMENTS.map((seg, i) => {
const from = positions[i];
const to = positions[i + 1];
const isPast = seg.id < currentSegment;
const isCurrent = seg.id === currentSegment;
const color = getStressColor(seg.id);
return (
<g key={seg.id}>
<line x1={from.x} y1={from.y} x2={to.x} y2={to.y}
stroke={isPast ? “#333” : isCurrent ? “#fff” : color}
strokeWidth={isCurrent ? 3 : 2}
strokeDasharray={seg.commsLevel <= 1 ? “6 3” : “none”}
opacity={isPast ? 0.3 : 0.8}
/>
<text x={(from.x + to.x) / 2 + 12} y={(from.y + to.y) / 2 + 2}
fill={isPast ? “#333” : “#555”} fontSize={7} fontFamily=“monospace”
>{seg.dist}mi</text>
</g>
);
})}
{positions.map((p, i) => {
const isCurrentPos = i + 1 === currentSegment;
const isPast = i + 1 < currentSegment;
const isHub = [1, 3, 6, 8].includes(i + 1);
const gateHere = state.gateStatus.find(g =>
(g.id === 1 && i === 0) || (g.id === 2 && i === 2) || (g.id === 3 && i === 5) || (g.id === 4 && i === 6)
);
const gateColor = gateHere && !gateHere.isPast
? (gateHere.recommendation === “GO” ? “#00E676” : gateHere.recommendation === “HOLD” ? “#FFD740” : “#EF5350”)
: null;
return (
<g key={p.id}>
{isCurrentPos && (
<circle cx={p.x} cy={p.y} r={6} fill={state.systemColor}
style={{ animation: “truckPulse 1.5s ease-in-out infinite” }}
opacity={0.4}
/>
)}
<circle cx={p.x} cy={p.y}
r={isHub ? 6 : 4}
fill={isPast ? “#333” : isCurrentPos ? state.systemColor : gateColor || (isHub ? “#FFD740” : “#78909C”)}
stroke={gateColor || “#222”} strokeWidth={gateColor ? 2 : 1}
/>
<text
x={p.x + (p.x > 150 ? -8 : 10)} y={p.y + 3}
fill={isPast ? “#444” : isCurrentPos ? “#fff” : isHub ? “#FFD740” : “#888”}
fontSize={7} fontFamily=“monospace” fontWeight={isHub ? 700 : 400}
textAnchor={p.x > 150 ? “end” : “start”}
>{p.label}</text>
{gateColor && !gateHere.isPast && (
<text x={p.x + (p.x > 150 ? -8 : 10)} y={p.y + 12}
fill={gateColor} fontSize={6} fontFamily=“monospace” fontWeight={700}
textAnchor={p.x > 150 ? “end” : “start”}
>G{gateHere.id}: {gateHere.recommendation}</text>
)}
</g>
);
})}
</svg>
);
};

// ── MAIN DASHBOARD ──
export default function RoutingDashboard() {
const [currentSegment, setCurrentSegment] = useState(1);
const [hosRemaining, setHosRemaining] = useState(11);
const [fuelLevel, setFuelLevel] = useState(120);
const [reeferHours, setReeferHours] = useState(12);
const [weatherSeverity, setWeatherSeverity] = useState(0);
const [season, setSeason] = useState(“winter”);
const [roadClosures, setRoadClosures] = useState([]);

const state = useMemo(() => computeState({
currentSegment, hosRemaining, fuelLevel, reeferHours,
weatherSeverity, season, roadClosures,
}), [currentSegment, hosRemaining, fuelLevel, reeferHours, weatherSeverity, season, roadClosures]);

const [selectedPanel, setSelectedPanel] = useState(“overview”);

return (
<div style={{
display: “flex”, flexDirection: “column”, height: “100vh”,
background: “#050508”, color: “#ccc”, fontFamily: “monospace”,
overflow: “hidden”,
}}>
{/* TOP BAR */}
<div style={{
display: “flex”, alignItems: “center”, gap: 12,
padding: “8px 16px”, borderBottom: “1px solid #1a1a1a”,
background: “#0a0a10”,
}}>
<span style={{ fontSize: 14, fontWeight: 800, color: “#FF6B35”, letterSpacing: 1 }}>
ROUTING OPS
</span>
<div style={{
marginLeft: “auto”, display: “flex”, alignItems: “center”, gap: 8,
}}>
<span style={{ fontSize: 11, color: “#666” }}>SYSTEM:</span>
<span style={{
fontSize: 12, fontWeight: 800, color: state.systemColor,
padding: “2px 10px”, border: `1px solid ${state.systemColor}`,
borderRadius: 3,
boxShadow: state.systemState === “CRITICAL” ? `0 0 12px ${state.systemColor}44` : “none”,
animation: state.systemState === “CRITICAL” ? “pulse 1.5s infinite” : “none”,
}}>{state.systemState}</span>
</div>
</div>

```
  <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }`}</style>

  <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
    {/* LEFT: INPUTS */}
    <div style={{
      width: 240, minWidth: 240, background: "#0a0a10",
      borderRight: "1px solid #1a1a1a", padding: "10px 12px",
      overflowY: "auto",
    }}>
      <div style={{
        fontSize: 10, color: "#666", textTransform: "uppercase",
        letterSpacing: 1.5, marginBottom: 8,
      }}>CURRENT STATE</div>

      <SelectInput label="Position" value={currentSegment} onChange={setCurrentSegment}
        options={SEGMENTS.map(s => ({ value: s.id, label: `${s.from}→` }))}
      />

      <Slider label="HOS Remaining" value={hosRemaining} onChange={setHosRemaining}
        min={0} max={11} step={0.5} unit="hr" color="#EF5350"
        marks={["0", "2.75", "5.5", "8.25", "11"]}
      />

      <Slider label="Fuel Level" value={fuelLevel} onChange={setFuelLevel}
        min={0} max={150} step={5} unit=" gal" color="#FF8F00"
        marks={["0", "37", "75", "112", "150"]}
      />

      <Slider label="Reefer Diesel" value={reeferHours} onChange={setReeferHours}
        min={0} max={24} step={0.5} unit="hr" color="#00E676"
        marks={["0", "6", "12", "18", "24"]}
      />

      <SelectInput label="Weather Severity (Seg 4–7)" value={weatherSeverity} onChange={setWeatherSeverity}
        options={[
          { value: 0, label: "Clear", color: "#00E676" },
          { value: 1, label: "Advisory", color: "#FFD740" },
          { value: 2, label: "Warning", color: "#FF8F00" },
          { value: 3, label: "Severe", color: "#EF5350" },
        ]}
      />

      <SelectInput label="Season" value={season} onChange={setSeason}
        options={[
          { value: "summer", label: "Summer", color: "#00E676" },
          { value: "shoulder", label: "Shoulder", color: "#FFD740" },
          { value: "winter", label: "Winter", color: "#4FC3F7" },
        ]}
      />

      <div style={{
        marginTop: 12, padding: "8px 0", borderTop: "1px solid #222",
      }}>
        <div style={{
          fontSize: 10, color: "#666", textTransform: "uppercase",
          letterSpacing: 1.5, marginBottom: 6,
        }}>COMPUTED</div>
        <div style={{ fontSize: 11, color: "#888", padding: "2px 0" }}>
          Dist remaining: <span style={{ color: "#ccc" }}>{state.distRemaining} mi</span>
        </div>
        <div style={{ fontSize: 11, color: "#888", padding: "2px 0" }}>
          Time needed: <span style={{ color: state.stress.T >= 2 ? "#EF5350" : "#ccc" }}>{state.timeNeeded} hr</span>
          <span style={{ color: "#555" }}> (×{state.weatherMultiplier} wx)</span>
        </div>
        <div style={{ fontSize: 11, color: "#888", padding: "2px 0" }}>
          HOS buffer: <span style={{ color: state.hosBuffer < 0 ? "#EF5350" : state.hosBuffer < 1 ? "#FF8F00" : "#00E676" }}>
            {state.hosBuffer > 0 ? "+" : ""}{state.hosBuffer} hr
          </span>
        </div>
        <div style={{ fontSize: 11, color: "#888", padding: "2px 0" }}>
          Fuel needed: <span style={{ color: "#ccc" }}>{state.fuelNeeded} gal</span>
          {" "}margin: <span style={{ color: state.fuelMargin < 0 ? "#EF5350" : state.fuelMargin < 10 ? "#FF8F00" : "#00E676" }}>
            {state.fuelMargin > 0 ? "+" : ""}{state.fuelMargin}
          </span>
        </div>
        {season === "winter" && (
          <div style={{ fontSize: 11, color: "#888", padding: "2px 0" }}>
            Idle burn: <span style={{ color: "#FF8F00" }}>{state.idleBurnRate} gal/hr</span>
          </div>
        )}
      </div>
    </div>

    {/* CENTER: MAP + PANELS */}
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* MAP */}
      <div style={{ padding: "8px 16px", borderBottom: "1px solid #1a1a1a" }}>
        <LiveCorridorMap currentSegment={currentSegment} state={state} />
      </div>

      {/* PANEL TABS */}
      <div style={{
        display: "flex", gap: 0, borderBottom: "1px solid #1a1a1a",
        background: "#0a0a0a",
      }}>
        {[
          ["overview", "Domain Stress"],
          ["gates", "Decision Gates"],
          ["tensions", "Tension Lines"],
          ["action", "Action"],
        ].map(([id, label]) => (
          <button key={id} onClick={() => setSelectedPanel(id)} style={{
            flex: 1, padding: "8px", fontSize: 11, fontFamily: "monospace",
            background: selectedPanel === id ? "#111" : "transparent",
            border: "none", borderBottom: selectedPanel === id ? `2px solid #FFD740` : "2px solid transparent",
            color: selectedPanel === id ? "#FFD740" : "#555",
            cursor: "pointer", fontWeight: selectedPanel === id ? 700 : 400,
          }}>{label}
            {id === "tensions" && state.tensionLines.length > 0 && (
              <span style={{
                marginLeft: 4, background: "#EF5350", color: "#fff",
                borderRadius: "50%", padding: "0 5px", fontSize: 9,
              }}>{state.tensionLines.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* PANEL CONTENT */}
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 16px" }}>
        {selectedPanel === "overview" && (
          <div>
            <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              DOMAIN STRESS LEVELS
            </div>
            {Object.keys(DOMAIN_COLORS).map(d => (
              <StressBar key={d} domain={d} level={state.stress[d] || 0} />
            ))}
            {state.criticalDomains.length > 0 && (
              <div style={{
                marginTop: 12, padding: "8px 10px", background: "#1a0a0a",
                border: "1px solid #EF5350", borderRadius: 4,
                fontSize: 11, fontFamily: "monospace",
              }}>
                <span style={{ color: "#EF5350", fontWeight: 700 }}>
                  {state.criticalDomains.length} DOMAINS AT WARNING+:
                </span>
                <span style={{ color: "#ccc", marginLeft: 6 }}>
                  {state.criticalDomains.map(d => `[${d}]`).join(" ")}
                </span>
              </div>
            )}
          </div>
        )}

        {selectedPanel === "gates" && (
          <div>
            <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              DECISION GATES
            </div>
            {state.gateStatus.map(g => (
              <GateIndicator key={g.id} gate={g} />
            ))}
            <div style={{
              marginTop: 12, padding: "8px 10px", background: "#0a0a14",
              border: "1px solid #333", borderRadius: 4,
              fontSize: 10, fontFamily: "monospace", color: "#888", lineHeight: 1.6,
            }}>
              Gate recommendations computed from domain stress.
              3+ domains at WARNING → HOLD at upcoming gates.
              4+ domains at WARNING or any at CRITICAL → NO-GO.
              Once past Gate 4 (Hayward), must reach Superior.
            </div>
          </div>
        )}

        {selectedPanel === "tensions" && (
          <div>
            <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              ACTIVE TENSION LINES ({state.tensionLines.length})
            </div>
            {state.tensionLines.length === 0 ? (
              <div style={{ fontSize: 12, color: "#555", fontFamily: "monospace", padding: "20px 0", textAlign: "center" }}>
                No tension lines active at current state.
              </div>
            ) : (
              state.tensionLines.map(t => <TensionAlert key={t.id} tension={t} />)
            )}
            <div style={{
              marginTop: 12, fontSize: 10, color: "#555", fontFamily: "monospace", lineHeight: 1.5,
            }}>
              Tension lines activate when multiple domains simultaneously
              approach failure thresholds at the current position. Severity
              increases with the number of stressed domains and proximity
              to the node desert (Segments 6–7).
            </div>
          </div>
        )}

        {selectedPanel === "action" && (
          <div>
            <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              RECOMMENDED ACTION
            </div>
            <div style={{
              padding: "12px", background: state.systemColor + "11",
              border: `1px solid ${state.systemColor}`,
              borderRadius: 4, fontFamily: "monospace",
            }}>
              {state.systemState === "NOMINAL" && (
                <>
                  <div style={{ fontSize: 13, color: "#00E676", fontWeight: 700, marginBottom: 6 }}>
                    PROCEED — All domains nominal
                  </div>
                  <div style={{ fontSize: 11, color: "#aaa", lineHeight: 1.5 }}>
                    Continue on planned route. Monitor weather updates approaching Segment 4.
                    {currentSegment <= 2 && " Re-evaluate at Gate 2 (Eau Claire)."}
                  </div>
                </>
              )}
              {state.systemState === "CAUTION" && (
                <>
                  <div style={{ fontSize: 13, color: "#FFD740", fontWeight: 700, marginBottom: 6 }}>
                    PROCEED WITH MONITORING
                  </div>
                  <div style={{ fontSize: 11, color: "#aaa", lineHeight: 1.5 }}>
                    Single-domain stress detected. Continue but increase monitoring frequency.
                    {state.stress.T >= 1 && " HOS buffer thinning — minimize non-essential stops."}
                    {state.stress.W >= 1 && " Weather advisory active — confirm conditions at next gate."}
                    {state.stress.F >= 1 && " Fuel margin below comfort — plan next fuel stop."}
                  </div>
                </>
              )}
              {state.systemState === "WARNING" && (
                <>
                  <div style={{ fontSize: 13, color: "#FF8F00", fontWeight: 700, marginBottom: 6 }}>
                    HOLD AT NEXT GATE — Multi-domain stress
                  </div>
                  <div style={{ fontSize: 11, color: "#aaa", lineHeight: 1.5 }}>
                    {state.criticalDomains.length} domains at warning or above: {state.criticalDomains.map(d => `[${d}]`).join(" ")}.
                    {" "}Do not advance past next gate without resolution.
                    {currentSegment <= 5 && " Consider I-35/Duluth alternate if weather is the primary driver."}
                    {state.stress.L >= 2 && " Reefer integrity at risk — retreat to nearest shore power (Eau Claire or Superior)."}
                  </div>
                </>
              )}
              {state.systemState === "CRITICAL" && (
                <>
                  <div style={{ fontSize: 13, color: "#EF5350", fontWeight: 700, marginBottom: 6 }}>
                    {currentSegment >= 7 ? "EMERGENCY — No safe fallback"
                      : currentSegment >= 6 ? "DO NOT ADVANCE — Hold at current position"
                      : "RETREAT TO LAST HUB NODE"}
                  </div>
                  <div style={{ fontSize: 11, color: "#aaa", lineHeight: 1.5 }}>
                    {state.tensionLines.length} tension lines active. Compound cascade risk.
                    {currentSegment <= 3 && " Return to Eau Claire — full services, shore power, comms."}
                    {currentSegment >= 4 && currentSegment <= 5 && " Hold at Rice Lake if reachable. Do NOT enter Segment 6–7 in this state."}
                    {currentSegment >= 6 && currentSegment < 7 && " You are in the node desert. If road is open, push to Superior. If not, shelter in place and conserve fuel."}
                    {currentSegment >= 7 && " Committed to Superior leg. Conserve fuel, maintain speed if road is passable. CB radio for any nearby traffic. Shelter immediately if conditions deteriorate further."}
                  </div>
                </>
              )}
            </div>

            {/* Alternate route suggestion */}
            {state.stress.W >= 2 && currentSegment <= 5 && (
              <div style={{
                marginTop: 8, padding: "8px 10px", background: "#0a1a0a",
                border: "1px solid #00E676", borderRadius: 4,
                fontSize: 11, fontFamily: "monospace",
              }}>
                <div style={{ color: "#00E676", fontWeight: 700, marginBottom: 4 }}>
                  ALT ROUTE: I-35 via Duluth
                </div>
                <div style={{ color: "#aaa", lineHeight: 1.5 }}>
                  +60mi, +1.2hr. Stays on interstate. Full cellular entire route.
                  Frequent fuel/parking nodes. Eliminates Segments 5–7 exposure entirely.
                  Cost: ~9 gal additional fuel.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  </div>
</div>
```

);
}
