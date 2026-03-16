import { useState, useEffect, useCallback, useRef } from “react”;

// ═══════════════════════════════════════════════════════════════
// SIMULATION ENGINE
// ═══════════════════════════════════════════════════════════════

// Needs taxonomy (Rosenberg-derived)
const NEEDS = [“safety”, “autonomy”, “connection”, “meaning”, “resources”];

function createClassicalAgent(id, strategy = “rational”) {
return {
id,
type: “classical”,
strategy, // rational | tit-for-tat | hawkish | dovish
utility: 50,
utilityHistory: [50],
cooperateRate: strategy === “dovish” ? 0.7 : strategy === “hawkish” ? 0.2 : 0.5,
rigidity: 0.8, // doesn’t change much
perception: “zero-sum”, // how they frame the world
};
}

function createNVCAgent(id) {
return {
id,
type: “nvc”,
needs: Object.fromEntries(NEEDS.map((n) => [n, 40 + Math.random() * 20])),
needsHistory: [],
empathyBandwidth: 0.5 + Math.random() * 0.2,
connectionCapacity: 0.5,
neuroplasticity: 0.3, // ability to reshape through interaction
selfEmpathy: 0.5, // capacity to identify own needs
perception: “needs-based”,
utility: 50,
utilityHistory: [50],
};
}

// Classical interaction: payoff matrix lookup
function classicalInteract(a1, a2, scenario) {
const tension = scenario.tension;

// Cooperation probability influenced by strategy and history
const c1 = Math.random() < a1.cooperateRate;
const c2 = Math.random() < a2.cooperateRate;

let p1, p2;
if (c1 && c2) {
// Mutual cooperate
p1 = 3 * (1 - tension * 0.3);
p2 = 3 * (1 - tension * 0.3);
} else if (c1 && !c2) {
p1 = 0;
p2 = 5 * (1 - tension * 0.1);
} else if (!c1 && c2) {
p1 = 5 * (1 - tension * 0.1);
p2 = 0;
} else {
// Mutual defect
p1 = 1 * (1 - tension * 0.5);
p2 = 1 * (1 - tension * 0.5);
}

// Classical agents barely adapt
if (!c2 && a1.strategy === “rational”) {
a1.cooperateRate = Math.max(0.1, a1.cooperateRate - 0.02);
}
if (c2 && a1.strategy === “tit-for-tat”) {
a1.cooperateRate = Math.min(0.9, a1.cooperateRate + 0.01);
}

a1.utility = Math.max(0, Math.min(100, a1.utility + p1 - 1));
a2.utility = Math.max(0, Math.min(100, a2.utility + p2 - 1));
a1.utilityHistory.push(a1.utility);
a2.utilityHistory.push(a2.utility);

return { cooperated: [c1, c2], payoffs: [p1, p2] };
}

// NVC interaction: needs-based resonance
function nvcInteract(a1, a2, scenario) {
const tension = scenario.tension;

// Step 1: Self-empathy — identify own needs
const a1NeedClarity = a1.selfEmpathy * (0.7 + Math.random() * 0.3);
const a2NeedClarity = a2.selfEmpathy * (0.7 + Math.random() * 0.3);

// Step 2: Express needs (fidelity depends on clarity)
// Step 3: Empathic reception (depends on bandwidth and tension)
const receptionQuality1 = a2.empathyBandwidth * (1 - tension * 0.4) * a1NeedClarity;
const receptionQuality2 = a1.empathyBandwidth * (1 - tension * 0.4) * a2NeedClarity;

// Step 4: Mutual modeling — each agent builds a model of other’s needs
const mutualUnderstanding = (receptionQuality1 + receptionQuality2) / 2;

// Step 5: Strategy emerges from needs landscape, not payoff matrix
// When mutual understanding is high, creative solutions appear
const creativeSpace = mutualUnderstanding * a1.connectionCapacity * a2.connectionCapacity;

// Needs get met proportional to creative space opened
for (const need of NEEDS) {
const deficit1 = Math.max(0, 70 - a1.needs[need]);
const deficit2 = Math.max(0, 70 - a2.needs[need]);

```
a1.needs[need] = Math.min(100, a1.needs[need] + deficit1 * creativeSpace * 0.3);
a2.needs[need] = Math.min(100, a2.needs[need] + deficit2 * creativeSpace * 0.3);

// Tension degrades needs
a1.needs[need] = Math.max(5, a1.needs[need] - tension * 2);
a2.needs[need] = Math.max(5, a2.needs[need] - tension * 2);
```

}

// NEUROPLASTICITY: agents change through interaction
if (mutualUnderstanding > 0.3) {
a1.empathyBandwidth = Math.min(1, a1.empathyBandwidth + a1.neuroplasticity * 0.02);
a2.empathyBandwidth = Math.min(1, a2.empathyBandwidth + a2.neuroplasticity * 0.02);
a1.connectionCapacity = Math.min(1, a1.connectionCapacity + a1.neuroplasticity * 0.015);
a2.connectionCapacity = Math.min(1, a2.connectionCapacity + a2.neuroplasticity * 0.015);
a1.selfEmpathy = Math.min(1, a1.selfEmpathy + a1.neuroplasticity * 0.01);
a2.selfEmpathy = Math.min(1, a2.selfEmpathy + a2.neuroplasticity * 0.01);
} else {
// Failed connection can temporarily reduce capacity
a1.empathyBandwidth = Math.max(0.1, a1.empathyBandwidth - 0.01);
a2.empathyBandwidth = Math.max(0.1, a2.empathyBandwidth - 0.01);
}

// Convert needs-met to utility for comparison
const avgNeeds1 = Object.values(a1.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
const avgNeeds2 = Object.values(a2.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
a1.utility = avgNeeds1;
a2.utility = avgNeeds2;
a1.utilityHistory.push(a1.utility);
a2.utilityHistory.push(a2.utility);

a1.needsHistory.push({ …a1.needs });
a2.needsHistory.push({ …a2.needs });

return { mutualUnderstanding, creativeSpace, receptionQuality: [receptionQuality1, receptionQuality2] };
}

// Mixed interaction: NVC agent meets classical agent
function mixedInteract(nvcAgent, classicalAgent, scenario) {
const tension = scenario.tension;

// NVC agent tries to empathize; classical agent plays strategy
const nvcClarity = nvcAgent.selfEmpathy * (0.7 + Math.random() * 0.3);
const classicalCooperates = Math.random() < classicalAgent.cooperateRate;

// Classical agent doesn’t really model needs — reads cooperation/defection
// NVC agent tries to read needs underneath the strategy
const empathicRead = nvcAgent.empathyBandwidth * (1 - tension * 0.3) * 0.5; // halved — classical agent isn’t expressing needs

if (classicalCooperates) {
// Some connection possible
const partialCreative = empathicRead * nvcAgent.connectionCapacity * 0.6;

```
for (const need of NEEDS) {
  const deficit = Math.max(0, 70 - nvcAgent.needs[need]);
  nvcAgent.needs[need] = Math.min(100, nvcAgent.needs[need] + deficit * partialCreative * 0.2);
  nvcAgent.needs[need] = Math.max(5, nvcAgent.needs[need] - tension * 1.5);
}

classicalAgent.utility = Math.min(100, classicalAgent.utility + 2);

// Classical agent slightly influenced by NVC approach over time
if (empathicRead > 0.3) {
  classicalAgent.cooperateRate = Math.min(0.9, classicalAgent.cooperateRate + 0.005);
}
```

} else {
// Defection against NVC agent
for (const need of NEEDS) {
nvcAgent.needs[need] = Math.max(5, nvcAgent.needs[need] - tension * 3);
}
classicalAgent.utility = Math.min(100, classicalAgent.utility + 3);

```
// NVC agent still tries to maintain empathy but it costs
nvcAgent.empathyBandwidth = Math.max(0.1, nvcAgent.empathyBandwidth - 0.005);
```

}

const avgNeeds = Object.values(nvcAgent.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
nvcAgent.utility = avgNeeds;
nvcAgent.utilityHistory.push(nvcAgent.utility);
classicalAgent.utilityHistory.push(classicalAgent.utility);
nvcAgent.needsHistory.push({ …nvcAgent.needs });

return { classicalCooperates, empathicRead };
}

// Scenario presets
const SCENARIOS = {
resource: {
name: “Resource Negotiation”,
description: “Two parties competing for limited resources — water, land, trade routes”,
tension: 0.4,
icon: “⛏”,
},
territorial: {
name: “Territorial Dispute”,
description: “Overlapping sovereignty claims with historical grievances”,
tension: 0.7,
icon: “🗺”,
},
cultural: {
name: “Cultural Friction”,
description: “Value system collision — autonomy vs collective, sacred vs secular”,
tension: 0.5,
icon: “🌀”,
},
crisis: {
name: “Active Crisis”,
description: “Hostage, humanitarian emergency, or military escalation in progress”,
tension: 0.9,
icon: “🔥”,
},
trade: {
name: “Trade Agreement”,
description: “Economic interdependence with asymmetric power dynamics”,
tension: 0.3,
icon: “⚖”,
},
};

// ═══════════════════════════════════════════════════════════════
// VISUALIZATION COMPONENTS
// ═══════════════════════════════════════════════════════════════

const COLORS = {
bg: “#0a0c10”,
surface: “#12151c”,
surfaceLight: “#1a1e28”,
border: “#252a36”,
classical: “#e05252”,
classicalDim: “#e0525240”,
nvc: “#52b4e0”,
nvcDim: “#52b4e040”,
mixed: “#b490e0”,
text: “#c8cdd8”,
textDim: “#6b7280”,
accent: “#e0a852”,
green: “#52e088”,
warning: “#e08852”,
};

// Mini sparkline
function Sparkline({ data, color, width = 200, height = 40 }) {
if (!data || data.length < 2) return null;
const max = Math.max(…data, 1);
const min = Math.min(…data, 0);
const range = max - min || 1;
const points = data
.map((v, i) => {
const x = (i / (data.length - 1)) * width;
const y = height - ((v - min) / range) * (height - 4) - 2;
return `${x},${y}`;
})
.join(” “);
return (
<svg width={width} height={height} style={{ display: “block” }}>
<polyline
points={points}
fill="none"
stroke={color}
strokeWidth="1.5"
strokeLinecap="round"
strokeLinejoin="round"
/>
</svg>
);
}

// Needs radar chart
function NeedsRadar({ needs, size = 140, color }) {
if (!needs) return null;
const cx = size / 2;
const cy = size / 2;
const r = size / 2 - 15;
const values = NEEDS.map((n) => needs[n] / 100);

const angleStep = (Math.PI * 2) / NEEDS.length;

const gridPoints = (radius) =>
NEEDS.map((_, i) => {
const angle = i * angleStep - Math.PI / 2;
return `${cx + Math.cos(angle) * radius},${cy + Math.sin(angle) * radius}`;
}).join(” “);

const dataPoints = values
.map((v, i) => {
const angle = i * angleStep - Math.PI / 2;
return `${cx + Math.cos(angle) * r * v},${cy + Math.sin(angle) * r * v}`;
})
.join(” “);

return (
<svg width={size} height={size}>
{[0.25, 0.5, 0.75, 1].map((s) => (
<polygon
key={s}
points={gridPoints(r * s)}
fill=“none”
stroke={COLORS.border}
strokeWidth=“0.5”
/>
))}
{NEEDS.map((n, i) => {
const angle = i * angleStep - Math.PI / 2;
const lx = cx + Math.cos(angle) * (r + 12);
const ly = cy + Math.sin(angle) * (r + 12);
return (
<text
key={n}
x={lx}
y={ly}
textAnchor="middle"
dominantBaseline="middle"
fill={COLORS.textDim}
fontSize="8"
fontFamily="'JetBrains Mono', monospace"
>
{n.slice(0, 4).toUpperCase()}
</text>
);
})}
<polygon points={dataPoints} fill={color + “25”} stroke={color} strokeWidth=“1.5” />
</svg>
);
}

// System welfare gauge
function WelfareGauge({ label, value, maxValue = 100, color }) {
const pct = Math.min(100, (value / maxValue) * 100);
return (
<div style={{ marginBottom: 8 }}>
<div
style={{
display: “flex”,
justifyContent: “space-between”,
fontSize: 11,
fontFamily: “‘JetBrains Mono’, monospace”,
color: COLORS.textDim,
marginBottom: 3,
}}
>
<span>{label}</span>
<span style={{ color }}>{value.toFixed(1)}</span>
</div>
<div
style={{
height: 4,
background: COLORS.border,
borderRadius: 2,
overflow: “hidden”,
}}
>
<div
style={{
height: “100%”,
width: `${pct}%`,
background: color,
borderRadius: 2,
transition: “width 0.3s ease”,
}}
/>
</div>
</div>
);
}

// ═══════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════

export default function NVCGameTheorySim() {
const [scenario, setScenario] = useState(“resource”);
const [running, setRunning] = useState(false);
const [step, setStep] = useState(0);
const [speed, setSpeed] = useState(100);
const [mode, setMode] = useState(“compare”); // compare | mixed

// Agents
const [classicalA, setClassicalA] = useState(null);
const [classicalB, setClassicalB] = useState(null);
const [nvcA, setNvcA] = useState(null);
const [nvcB, setNvcB] = useState(null);
const [mixedNvc, setMixedNvc] = useState(null);
const [mixedClassical, setMixedClassical] = useState(null);

// Metrics
const [metrics, setMetrics] = useState({
classicalTotal: [],
nvcTotal: [],
mixedTotal: [],
gini_classical: [],
gini_nvc: [],
empathyGrowth: [],
connectionGrowth: [],
});

const intervalRef = useRef(null);

const initAgents = useCallback(() => {
setClassicalA(createClassicalAgent(“C1”, “rational”));
setClassicalB(createClassicalAgent(“C2”, “tit-for-tat”));
setNvcA(createNVCAgent(“N1”));
setNvcB(createNVCAgent(“N2”));
setMixedNvc(createNVCAgent(“MN”));
setMixedClassical(createClassicalAgent(“MC”, “rational”));
setStep(0);
setMetrics({
classicalTotal: [],
nvcTotal: [],
mixedTotal: [],
gini_classical: [],
gini_nvc: [],
empathyGrowth: [],
connectionGrowth: [],
});
}, []);

useEffect(() => {
initAgents();
}, [initAgents]);

const runStep = useCallback(() => {
if (!classicalA || !nvcA) return;

```
const sc = SCENARIOS[scenario];

// Classical pair
classicalInteract(classicalA, classicalB, sc);

// NVC pair
nvcInteract(nvcA, nvcB, sc);

// Mixed pair
mixedInteract(mixedNvc, mixedClassical, sc);

// Compute metrics
const cTotal = classicalA.utility + classicalB.utility;
const nTotal = nvcA.utility + nvcB.utility;
const mTotal = mixedNvc.utility + mixedClassical.utility;

// Gini coefficient (inequality measure)
const giniC = Math.abs(classicalA.utility - classicalB.utility) / (cTotal || 1);
const giniN = Math.abs(nvcA.utility - nvcB.utility) / (nTotal || 1);

setMetrics((prev) => ({
  classicalTotal: [...prev.classicalTotal, cTotal],
  nvcTotal: [...prev.nvcTotal, nTotal],
  mixedTotal: [...prev.mixedTotal, mTotal],
  gini_classical: [...prev.gini_classical, giniC],
  gini_nvc: [...prev.gini_nvc, giniN],
  empathyGrowth: [...prev.empathyGrowth, (nvcA.empathyBandwidth + nvcB.empathyBandwidth) / 2],
  connectionGrowth: [
    ...prev.connectionGrowth,
    (nvcA.connectionCapacity + nvcB.connectionCapacity) / 2,
  ],
}));

// Force re-render with new objects
setClassicalA({ ...classicalA });
setClassicalB({ ...classicalB });
setNvcA({ ...nvcA });
setNvcB({ ...nvcB });
setMixedNvc({ ...mixedNvc });
setMixedClassical({ ...mixedClassical });
setStep((s) => s + 1);
```

}, [classicalA, classicalB, nvcA, nvcB, mixedNvc, mixedClassical, scenario]);

useEffect(() => {
if (running) {
intervalRef.current = setInterval(runStep, speed);
}
return () => clearInterval(intervalRef.current);
}, [running, runStep, speed]);

if (!classicalA || !nvcA) return null;

const scenarioData = SCENARIOS[scenario];

const panelStyle = {
background: COLORS.surface,
border: `1px solid ${COLORS.border}`,
borderRadius: 6,
padding: 16,
};

const labelStyle = {
fontFamily: “‘JetBrains Mono’, monospace”,
fontSize: 10,
color: COLORS.textDim,
textTransform: “uppercase”,
letterSpacing: “0.08em”,
marginBottom: 8,
};

const statStyle = {
fontFamily: “‘JetBrains Mono’, monospace”,
fontSize: 22,
fontWeight: 600,
};

return (
<div
style={{
background: COLORS.bg,
color: COLORS.text,
minHeight: “100vh”,
padding: “20px 24px”,
fontFamily: “‘Inter’, ‘Segoe UI’, sans-serif”,
}}
>
<link
href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;600;700&display=swap"
rel="stylesheet"
/>

```
  {/* Header */}
  <div style={{ marginBottom: 24 }}>
    <h1
      style={{
        fontFamily: "'Space Grotesk', sans-serif",
        fontSize: 20,
        fontWeight: 700,
        margin: 0,
        color: COLORS.text,
      }}
    >
      Conflict Resolution Dynamics
    </h1>
    <div
      style={{
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
        color: COLORS.textDim,
        marginTop: 4,
      }}
    >
      NVC-substrate vs Classical Game Theory — Neuroplastic Agent Simulation
    </div>
  </div>

  {/* Controls */}
  <div
    style={{
      display: "flex",
      gap: 8,
      flexWrap: "wrap",
      marginBottom: 20,
      alignItems: "center",
    }}
  >
    {/* Scenario selector */}
    {Object.entries(SCENARIOS).map(([key, sc]) => (
      <button
        key={key}
        onClick={() => {
          setScenario(key);
          setRunning(false);
          initAgents();
        }}
        style={{
          background: scenario === key ? COLORS.surfaceLight : "transparent",
          border: `1px solid ${scenario === key ? COLORS.accent : COLORS.border}`,
          color: scenario === key ? COLORS.accent : COLORS.textDim,
          padding: "6px 12px",
          borderRadius: 4,
          cursor: "pointer",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 11,
          transition: "all 0.2s",
        }}
      >
        {sc.icon} {sc.name}
      </button>
    ))}

    <div style={{ flex: 1 }} />

    {/* Playback */}
    <button
      onClick={() => setRunning(!running)}
      style={{
        background: running ? COLORS.warning + "20" : COLORS.green + "20",
        border: `1px solid ${running ? COLORS.warning : COLORS.green}`,
        color: running ? COLORS.warning : COLORS.green,
        padding: "6px 16px",
        borderRadius: 4,
        cursor: "pointer",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
        fontWeight: 600,
      }}
    >
      {running ? "■ PAUSE" : "▶ RUN"}
    </button>
    <button
      onClick={runStep}
      disabled={running}
      style={{
        background: "transparent",
        border: `1px solid ${COLORS.border}`,
        color: COLORS.textDim,
        padding: "6px 12px",
        borderRadius: 4,
        cursor: running ? "default" : "pointer",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
        opacity: running ? 0.4 : 1,
      }}
    >
      STEP
    </button>
    <button
      onClick={() => {
        setRunning(false);
        initAgents();
      }}
      style={{
        background: "transparent",
        border: `1px solid ${COLORS.border}`,
        color: COLORS.textDim,
        padding: "6px 12px",
        borderRadius: 4,
        cursor: "pointer",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
      }}
    >
      RESET
    </button>
    <select
      value={speed}
      onChange={(e) => setSpeed(Number(e.target.value))}
      style={{
        background: COLORS.surface,
        border: `1px solid ${COLORS.border}`,
        color: COLORS.textDim,
        padding: "6px 8px",
        borderRadius: 4,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
      }}
    >
      <option value={200}>Slow</option>
      <option value={100}>Med</option>
      <option value={30}>Fast</option>
    </select>
  </div>

  {/* Scenario info bar */}
  <div
    style={{
      ...panelStyle,
      marginBottom: 16,
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "10px 16px",
    }}
  >
    <div>
      <span style={{ fontSize: 13, fontWeight: 600 }}>
        {scenarioData.icon} {scenarioData.name}
      </span>
      <span style={{ fontSize: 11, color: COLORS.textDim, marginLeft: 12 }}>
        {scenarioData.description}
      </span>
    </div>
    <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
      <div style={labelStyle}>
        TENSION{" "}
        <span style={{ color: COLORS.warning, fontSize: 13 }}>
          {(scenarioData.tension * 100).toFixed(0)}%
        </span>
      </div>
      <div style={labelStyle}>
        STEP <span style={{ color: COLORS.text, fontSize: 13 }}>{step}</span>
      </div>
    </div>
  </div>

  {/* Main grid */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
    {/* CLASSICAL PAIR */}
    <div style={panelStyle}>
      <div style={{ ...labelStyle, color: COLORS.classical }}>
        ● Classical Game Theory
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div style={{ ...statStyle, color: COLORS.classical }}>
            {classicalA.utility.toFixed(1)}
          </div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>
            Agent 1 — {classicalA.strategy}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ ...statStyle, color: COLORS.classical }}>
            {classicalB.utility.toFixed(1)}
          </div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>
            Agent 2 — {classicalB.strategy}
          </div>
        </div>
      </div>
      <Sparkline data={metrics.classicalTotal} color={COLORS.classical} width={260} height={50} />
      <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 4 }}>
        COMBINED WELFARE ↑
      </div>

      <div style={{ marginTop: 12 }}>
        <WelfareGauge
          label="Coop Rate A1"
          value={classicalA.cooperateRate * 100}
          color={COLORS.classical}
        />
        <WelfareGauge
          label="Coop Rate A2"
          value={classicalB.cooperateRate * 100}
          color={COLORS.classical}
        />
        <WelfareGauge
          label="Inequality (Gini)"
          value={(metrics.gini_classical[metrics.gini_classical.length - 1] || 0) * 100}
          color={COLORS.warning}
        />
      </div>

      <div
        style={{
          marginTop: 12,
          padding: "8px 10px",
          background: COLORS.classicalDim,
          borderRadius: 4,
          fontSize: 10,
          fontFamily: "'JetBrains Mono', monospace",
          color: COLORS.textDim,
          lineHeight: 1.6,
        }}
      >
        SUBSTRATE: Utility functions
        <br />
        AGENTS: Static — no learning
        <br />
        FRAME: Zero-sum payoff matrix
        <br />
        EQUILIBRIUM: Nash (stable, suboptimal)
      </div>
    </div>

    {/* NVC PAIR */}
    <div style={panelStyle}>
      <div style={{ ...labelStyle, color: COLORS.nvc }}>● NVC-Substrate Dynamics</div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div style={{ ...statStyle, color: COLORS.nvc }}>{nvcA.utility.toFixed(1)}</div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>Agent 1 — needs-based</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ ...statStyle, color: COLORS.nvc }}>{nvcB.utility.toFixed(1)}</div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>Agent 2 — needs-based</div>
        </div>
      </div>
      <Sparkline data={metrics.nvcTotal} color={COLORS.nvc} width={260} height={50} />
      <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 4 }}>
        COMBINED WELFARE ↑
      </div>

      {/* Needs radars */}
      <div style={{ display: "flex", justifyContent: "space-around", marginTop: 8 }}>
        <NeedsRadar needs={nvcA.needs} size={110} color={COLORS.nvc} />
        <NeedsRadar needs={nvcB.needs} size={110} color={COLORS.nvc} />
      </div>

      {/* Neuroplastic metrics */}
      <div style={{ marginTop: 8 }}>
        <WelfareGauge
          label="Empathy Bandwidth"
          value={((nvcA.empathyBandwidth + nvcB.empathyBandwidth) / 2) * 100}
          color={COLORS.nvc}
        />
        <WelfareGauge
          label="Connection Capacity"
          value={((nvcA.connectionCapacity + nvcB.connectionCapacity) / 2) * 100}
          color={COLORS.green}
        />
      </div>

      <div
        style={{
          marginTop: 8,
          padding: "8px 10px",
          background: COLORS.nvcDim,
          borderRadius: 4,
          fontSize: 10,
          fontFamily: "'JetBrains Mono', monospace",
          color: COLORS.textDim,
          lineHeight: 1.6,
        }}
      >
        SUBSTRATE: Needs vectors
        <br />
        AGENTS: Neuroplastic — grow through contact
        <br />
        FRAME: Needs-met attractor basins
        <br />
        EQUILIBRIUM: Emergent, co-evolving
      </div>
    </div>

    {/* MIXED PAIR */}
    <div style={panelStyle}>
      <div style={{ ...labelStyle, color: COLORS.mixed }}>● Cross-Substrate (Mixed)</div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div style={{ ...statStyle, color: COLORS.nvc }}>{mixedNvc.utility.toFixed(1)}</div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>NVC Agent</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ ...statStyle, color: COLORS.classical }}>
            {mixedClassical.utility.toFixed(1)}
          </div>
          <div style={{ fontSize: 10, color: COLORS.textDim }}>Classical Agent</div>
        </div>
      </div>
      <Sparkline data={metrics.mixedTotal} color={COLORS.mixed} width={260} height={50} />
      <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 4 }}>
        COMBINED WELFARE ↑
      </div>

      {/* NVC agent's needs in mixed context */}
      <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
        <NeedsRadar needs={mixedNvc.needs} size={110} color={COLORS.mixed} />
      </div>

      <div style={{ marginTop: 8 }}>
        <WelfareGauge
          label="NVC Empathy (under pressure)"
          value={mixedNvc.empathyBandwidth * 100}
          color={COLORS.mixed}
        />
        <WelfareGauge
          label="Classical Coop Drift"
          value={mixedClassical.cooperateRate * 100}
          color={COLORS.classical}
        />
      </div>

      <div
        style={{
          marginTop: 8,
          padding: "8px 10px",
          background: COLORS.mixed + "15",
          borderRadius: 4,
          fontSize: 10,
          fontFamily: "'JetBrains Mono', monospace",
          color: COLORS.textDim,
          lineHeight: 1.6,
        }}
      >
        KEY QUESTION: Can NVC-substrate
        <br />
        agents shift classical agents through
        <br />
        sustained empathic contact?
        <br />
        Watch classical coop drift ↑
      </div>
    </div>
  </div>

  {/* Bottom comparative metrics */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
    <div style={panelStyle}>
      <div style={labelStyle}>System Welfare Comparison (Total)</div>
      <div style={{ display: "flex", gap: 24 }}>
        <div>
          <Sparkline
            data={metrics.classicalTotal}
            color={COLORS.classical}
            width={180}
            height={45}
          />
          <div style={{ fontSize: 9, color: COLORS.classical, marginTop: 2 }}>
            ● CLASSICAL{" "}
            {(metrics.classicalTotal[metrics.classicalTotal.length - 1] || 0).toFixed(1)}
          </div>
        </div>
        <div>
          <Sparkline data={metrics.nvcTotal} color={COLORS.nvc} width={180} height={45} />
          <div style={{ fontSize: 9, color: COLORS.nvc, marginTop: 2 }}>
            ● NVC {(metrics.nvcTotal[metrics.nvcTotal.length - 1] || 0).toFixed(1)}
          </div>
        </div>
      </div>
      {step > 20 && (
        <div
          style={{
            marginTop: 10,
            fontSize: 11,
            fontFamily: "'JetBrains Mono', monospace",
            color: COLORS.accent,
          }}
        >
          Δ ={" "}
          {(
            (metrics.nvcTotal[metrics.nvcTotal.length - 1] || 0) -
            (metrics.classicalTotal[metrics.classicalTotal.length - 1] || 0)
          ).toFixed(1)}{" "}
          welfare units (
          {(metrics.nvcTotal[metrics.nvcTotal.length - 1] || 0) >
          (metrics.classicalTotal[metrics.classicalTotal.length - 1] || 0)
            ? "NVC leading"
            : "Classical leading"}
          )
        </div>
      )}
    </div>

    <div style={panelStyle}>
      <div style={labelStyle}>Neuroplastic Evolution (NVC agents only)</div>
      <div style={{ display: "flex", gap: 24 }}>
        <div>
          <Sparkline
            data={metrics.empathyGrowth}
            color={COLORS.nvc}
            width={180}
            height={45}
          />
          <div style={{ fontSize: 9, color: COLORS.nvc, marginTop: 2 }}>
            ● EMPATHY BANDWIDTH
          </div>
        </div>
        <div>
          <Sparkline
            data={metrics.connectionGrowth}
            color={COLORS.green}
            width={180}
            height={45}
          />
          <div style={{ fontSize: 9, color: COLORS.green, marginTop: 2 }}>
            ● CONNECTION CAPACITY
          </div>
        </div>
      </div>
      {step > 20 && (
        <div
          style={{
            marginTop: 10,
            fontSize: 11,
            fontFamily: "'JetBrains Mono', monospace",
            color: COLORS.textDim,
          }}
        >
          Classical agents: static. NVC agents: self-modifying. The gap compounds.
        </div>
      )}
    </div>
  </div>

  {/* Insight panel */}
  {step > 50 && (
    <div
      style={{
        ...panelStyle,
        marginTop: 12,
        borderColor: COLORS.accent + "40",
      }}
    >
      <div style={{ ...labelStyle, color: COLORS.accent }}>⚡ Emergent Observations</div>
      <div
        style={{
          fontSize: 12,
          lineHeight: 1.7,
          fontFamily: "'JetBrains Mono', monospace",
          color: COLORS.textDim,
        }}
      >
        {(() => {
          const nvcWin =
            (metrics.nvcTotal[metrics.nvcTotal.length - 1] || 0) >
            (metrics.classicalTotal[metrics.classicalTotal.length - 1] || 0);
          const empathyGrew =
            (metrics.empathyGrowth[metrics.empathyGrowth.length - 1] || 0) >
            (metrics.empathyGrowth[0] || 0);
          const classicalDecayed =
            classicalA.cooperateRate < 0.4 && classicalB.cooperateRate < 0.4;

          return (
            <>
              {nvcWin && (
                <div>
                  → NVC-substrate producing higher total welfare. The neuroplastic agents are
                  finding solutions outside the classical payoff matrix.
                </div>
              )}
              {empathyGrew && (
                <div style={{ marginTop: 4 }}>
                  → Empathy bandwidth expanding through use — the capacity to resolve conflict is
                  itself a renewable resource in NVC dynamics.
                </div>
              )}
              {classicalDecayed && (
                <div style={{ marginTop: 4 }}>
                  → Classical agents in cooperation death spiral. Without neuroplasticity, defection
                  breeds defection. The "rational" substrate produces irrational system outcomes.
                </div>
              )}
              <div style={{ marginTop: 4 }}>
                → Key structural insight: Classical game theory treats agent capacity as fixed.
                NVC treats it as the primary variable. Over time, this divergence dominates all
                other factors.
              </div>
            </>
          );
        })()}
      </div>
    </div>
  )}
</div>
```

);
}
