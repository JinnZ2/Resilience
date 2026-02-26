import { useState, useMemo } from “react”;

const DOMAIN_COLORS = {
R: { bg: “#FF6B35”, fg: “#FFF”, label: “Route”, hex: “#FF6B35” },
W: { bg: “#4FC3F7”, fg: “#000”, label: “Weather”, hex: “#4FC3F7” },
C: { bg: “#AB47BC”, fg: “#FFF”, label: “Comms”, hex: “#AB47BC” },
F: { bg: “#FF8F00”, fg: “#000”, label: “Fuel”, hex: “#FF8F00” },
L: { bg: “#00E676”, fg: “#000”, label: “Load”, hex: “#00E676” },
T: { bg: “#EF5350”, fg: “#FFF”, label: “Time/HOS”, hex: “#EF5350” },
I: { bg: “#78909C”, fg: “#FFF”, label: “Infra”, hex: “#78909C” },
N: { bg: “#FFD740”, fg: “#000”, label: “Node”, hex: “#FFD740” },
};

const DomainTag = ({ d }) => {
const c = DOMAIN_COLORS[d];
if (!c) return null;
return (
<span style={{
display: “inline-block”, background: c.bg, color: c.fg,
borderRadius: 3, padding: “1px 6px”, fontSize: 11,
fontWeight: 700, fontFamily: “monospace”, marginRight: 4,
verticalAlign: “middle”,
}}>[{d}]</span>
);
};

const DomainLegend = () => (

  <div style={{
    display: "flex", flexWrap: "wrap", gap: 6, padding: "8px 0",
    borderBottom: "1px solid #333", marginBottom: 12,
  }}>
    {Object.entries(DOMAIN_COLORS).map(([k, v]) => (
      <span key={k} style={{
        background: v.bg, color: v.fg, padding: "2px 8px",
        borderRadius: 3, fontSize: 11, fontFamily: "monospace", fontWeight: 700,
      }}>[{k}] {v.label}</span>
    ))}
  </div>
);

const CascadeBox = ({ target, effects }) => (

  <div style={{
    background: "#0f0f1a", border: "1px solid #FFD740",
    borderLeft: "3px solid #FFD740", borderRadius: 4,
    padding: "8px 12px", margin: "8px 0",
  }}>
    <div style={{
      fontSize: 12, fontWeight: 700, color: "#FFD740",
      fontFamily: "monospace", marginBottom: 6,
    }}>⚡ CASCADE: {target}</div>
    {effects.map((e, i) => (
      <div key={i} style={{ fontSize: 12, color: "#ccc", fontFamily: "monospace", padding: "2px 0" }}>
        <DomainTag d={e.domain} /> {e.text}
      </div>
    ))}
  </div>
);

const TensionLine = ({ title, domains, description, failure }) => (

  <div style={{
    background: "#1a0a0a", border: "1px solid #EF5350",
    borderLeft: "3px solid #EF5350", borderRadius: 4,
    padding: "8px 12px", margin: "8px 0",
  }}>
    <div style={{
      fontSize: 12, fontWeight: 700, color: "#EF5350",
      fontFamily: "monospace", marginBottom: 4,
      display: "flex", alignItems: "center", gap: 6,
    }}>
      🔺 TENSION LINE: {title}
      <span style={{ display: "flex", gap: 3, marginLeft: "auto" }}>
        {domains.map(d => <DomainTag key={d} d={d} />)}
      </span>
    </div>
    <div style={{ fontSize: 12, color: "#ccc", fontFamily: "monospace", lineHeight: 1.5 }}>{description}</div>
    {failure && (
      <div style={{ fontSize: 11, color: "#EF5350", fontFamily: "monospace", marginTop: 4 }}>
        ENTROPY EVENT: {failure}
      </div>
    )}
  </div>
);

const Param = ({ label, value, unit, note }) => (

  <div style={{
    display: "flex", alignItems: "baseline", gap: 8,
    padding: "3px 0", fontSize: 12, fontFamily: "monospace",
  }}>
    <span style={{ color: "#888", minWidth: 160 }}>{label}:</span>
    <span style={{ color: "#00ff88", fontWeight: 700 }}>
      {value}{unit && <span style={{ color: "#888", fontWeight: 400, marginLeft: 2 }}>{unit}</span>}
    </span>
    {note && <span style={{ color: "#666", fontSize: 11 }}>← {note}</span>}
  </div>
);

const Text = ({ children }) => (

  <div style={{ color: "#bbb", fontSize: 12, fontFamily: "monospace", lineHeight: 1.6, margin: "4px 0" }}>
    {children}
  </div>
);

const SubHead = ({ children }) => (

  <div style={{
    color: "#888", fontSize: 11, fontFamily: "monospace",
    textTransform: "uppercase", letterSpacing: 1.5,
    margin: "12px 0 6px", borderBottom: "1px solid #222", paddingBottom: 4,
  }}>{children}</div>
);

const Section = ({ id, title, domains, children, activeSection, setActiveSection }) => {
const isOpen = activeSection === id;
return (
<div style={{
borderBottom: “1px solid #1a1a1a”,
background: isOpen ? “#0a0a12” : “transparent”,
}}>
<button onClick={() => setActiveSection(isOpen ? null : id)} style={{
width: “100%”, display: “flex”, alignItems: “center”, gap: 8,
padding: “10px 16px”, background: “none”, border: “none”,
cursor: “pointer”, textAlign: “left”,
}}>
<span style={{
color: isOpen ? “#FFD740” : “#555”, fontFamily: “monospace”,
fontSize: 14, transition: “transform 0.2s”,
transform: isOpen ? “rotate(90deg)” : “rotate(0)”, display: “inline-block”,
}}>▶</span>
<span style={{
color: isOpen ? “#fff” : “#aaa”, fontFamily: “monospace”,
fontSize: 13, fontWeight: 700, flex: 1,
}}>{title}</span>
<span style={{ display: “flex”, gap: 3 }}>
{domains.map(d => <DomainTag key={d} d={d} />)}
</span>
</button>
{isOpen && <div style={{ padding: “0 16px 16px 32px” }}>{children}</div>}
</div>
);
};

// ── CORRIDOR MAP as SVG ──
const CorridorMap = ({ activeSegment, setActiveSegment }) => {
const nodes = [
{ id: “tomah”, label: “TOMAH”, x: 100, y: 380, type: “hub” },
{ id: “brf”, label: “BLACK RIVER FALLS”, x: 150, y: 310, type: “node” },
{ id: “eauclaire”, label: “EAU CLAIRE”, x: 200, y: 230, type: “hub” },
{ id: “chippewa”, label: “CHIPPEWA FALLS”, x: 270, y: 200, type: “node” },
{ id: “ladysmith”, label: “LADYSMITH”, x: 310, y: 150, type: “node” },
{ id: “ricelake”, label: “RICE LAKE”, x: 280, y: 110, type: “hub” },
{ id: “hayward”, label: “HAYWARD”, x: 220, y: 70, type: “node” },
{ id: “superior”, label: “SUPERIOR”, x: 160, y: 20, type: “hub” },
];

const segments = [
{ from: “tomah”, to: “brf”, id: “s1”, route: “I-94 / US-12”, dist: “45mi”, comms: “cellular OK”, weather_risk: “low” },
{ from: “brf”, to: “eauclaire”, id: “s2”, route: “I-94”, dist: “60mi”, comms: “cellular OK”, weather_risk: “moderate” },
{ from: “eauclaire”, to: “chippewa”, id: “s3”, route: “US-53/WI-29”, dist: “15mi”, comms: “cellular OK”, weather_risk: “low” },
{ from: “chippewa”, to: “ladysmith”, id: “s4”, route: “WI-27”, dist: “45mi”, comms: “degraded”, weather_risk: “high” },
{ from: “ladysmith”, to: “ricelake”, id: “s5”, route: “WI-27/US-8”, dist: “30mi”, comms: “degraded”, weather_risk: “high” },
{ from: “ricelake”, to: “hayward”, id: “s6”, route: “WI-48/US-63”, dist: “35mi”, comms: “poor — LoRa only”, weather_risk: “high” },
{ from: “hayward”, to: “superior”, id: “s7”, route: “US-63/US-2”, dist: “75mi”, comms: “poor — LoRa only”, weather_risk: “severe” },
];

const getNode = (id) => nodes.find(n => n.id === id);

return (
<div style={{ margin: “8px 0” }}>
<svg viewBox=”-20 -10 420 420” style={{
width: “100%”, maxHeight: 400, background: “#080810”,
borderRadius: 4, border: “1px solid #222”,
}}>
{/* Segments */}
{segments.map(s => {
const f = getNode(s.from);
const t = getNode(s.to);
const isActive = activeSegment === s.id;
const riskColor = s.weather_risk === “severe” ? “#EF5350” :
s.weather_risk === “high” ? “#FF8F00” :
s.weather_risk === “moderate” ? “#FFD740” : “#4FC3F7”;
return (
<g key={s.id} style={{ cursor: “pointer” }} onClick={() => setActiveSegment(isActive ? null : s.id)}>
<line x1={f.x} y1={f.y} x2={t.x} y2={t.y}
stroke={isActive ? “#fff” : riskColor}
strokeWidth={isActive ? 3 : 2}
strokeDasharray={s.comms.includes(“poor”) ? “6 3” : “none”}
opacity={isActive ? 1 : 0.7}
/>
<text
x={(f.x + t.x) / 2 + 15} y={(f.y + t.y) / 2}
fill={isActive ? “#fff” : “#666”} fontSize={8} fontFamily=“monospace”
>{s.dist}</text>
</g>
);
})}
{/* Nodes */}
{nodes.map(n => (
<g key={n.id}>
<circle cx={n.x} cy={n.y}
r={n.type === “hub” ? 8 : 5}
fill={n.type === “hub” ? “#FFD740” : “#78909C”}
stroke=”#222” strokeWidth={1}
/>
<text
x={n.x + (n.x > 250 ? -10 : 12)}
y={n.y + 4}
fill={n.type === “hub” ? “#FFD740” : “#aaa”}
fontSize={8} fontFamily=“monospace” fontWeight={n.type === “hub” ? 700 : 400}
textAnchor={n.x > 250 ? “end” : “start”}
>{n.label}</text>
</g>
))}
{/* Legend */}
<g transform="translate(300, 250)">
<text fill="#666" fontSize={8} fontFamily="monospace" y={0}>WEATHER RISK</text>
{[[“low”, “#4FC3F7”], [“moderate”, “#FFD740”], [“high”, “#FF8F00”], [“severe”, “#EF5350”]].map(([l, c], i) => (
<g key={l} transform={`translate(0, ${14 + i * 14})`}>
<line x1={0} y1={-3} x2={20} y2={-3} stroke={c} strokeWidth={2} />
<text x={25} fill={c} fontSize={7} fontFamily="monospace">{l}</text>
</g>
))}
<g transform="translate(0, 74)">
<line x1={0} y1={-3} x2={20} y2={-3} stroke="#888" strokeWidth={2} strokeDasharray="6 3" />
<text x={25} fill="#888" fontSize={7} fontFamily="monospace">degraded comms</text>
</g>
</g>
</svg>
{/* Segment detail */}
{activeSegment && (() => {
const seg = segments.find(s => s.id === activeSegment);
return seg ? (
<div style={{
background: “#0a0a14”, border: “1px solid #333”,
borderRadius: 4, padding: “8px 12px”, marginTop: 4,
}}>
<div style={{ fontSize: 12, color: “#fff”, fontFamily: “monospace”, fontWeight: 700 }}>
{getNode(seg.from).label} → {getNode(seg.to).label}
</div>
<Param label="Route" value={seg.route} />
<Param label="Distance" value={seg.dist} />
<Param label="Comms" value={seg.comms} />
<Param label="Weather Risk" value={seg.weather_risk} />
</div>
) : null;
})()}
</div>
);
};

export default function RoutingResilienceSystem() {
const [activeSection, setActiveSection] = useState(“corridor-map”);
const [activeSegment, setActiveSegment] = useState(null);
const [navCollapsed, setNavCollapsed] = useState(false);

return (
<div style={{
display: “flex”, minHeight: “100vh”,
background: “#050508”, color: “#ccc”, fontFamily: “monospace”,
}}>
{/* NAV */}
<div style={{
width: navCollapsed ? 40 : 200, minWidth: navCollapsed ? 40 : 200,
background: “#0a0a10”, borderRight: “1px solid #1a1a1a”,
padding: navCollapsed ? “8px 4px” : “12px 8px”,
transition: “width 0.2s, min-width 0.2s”,
overflowY: “auto”, overflowX: “hidden”,
}}>
<button onClick={() => setNavCollapsed(!navCollapsed)} style={{
background: “none”, border: “none”, color: “#666”,
cursor: “pointer”, fontSize: 14, padding: 4, width: “100%”,
textAlign: navCollapsed ? “center” : “right”,
}}>{navCollapsed ? “→” : “←”}</button>
{!navCollapsed && (
<div style={{ marginTop: 8 }}>
<div style={{
fontSize: 10, color: “#FF6B35”, letterSpacing: 2,
textTransform: “uppercase”, marginBottom: 12, padding: “0 4px”,
}}>SUBSYSTEMS</div>
{[
[“corridor-map”, “Corridor Map”],
[“corridor-segments”, “Segment Parameters”],
[“weather-cascade”, “Weather Cascade”],
[“hos-energy”, “HOS Energy Budget”],
[“comms-topology”, “Comms Topology”],
[“fuel-thermal”, “Fuel + Thermal Load”],
[“load-integrity”, “Load Integrity”],
[“node-network”, “Node Network”],
[“tension-lines”, “Tension Lines”],
[“fallback-protocol”, “Fallback Protocols”],
[“seasonal-modes”, “Seasonal Modes”],
[“cascade-scenarios”, “Cascade Scenarios”],
].map(([id, label]) => (
<button key={id} onClick={() => setActiveSection(id)} style={{
display: “block”, width: “100%”, textAlign: “left”,
background: activeSection === id ? “#FFD74015” : “none”,
border: “none”,
borderLeft: activeSection === id ? “2px solid #FFD740” : “2px solid transparent”,
color: activeSection === id ? “#FFD740” : “#666”,
fontSize: 11, padding: “5px 8px”, cursor: “pointer”, fontFamily: “monospace”,
}}>{label}</button>
))}
</div>
)}
</div>

```
  {/* MAIN */}
  <div style={{ flex: 1, overflowY: "auto", maxHeight: "100vh" }}>
    <div style={{
      padding: "16px 20px", borderBottom: "1px solid #1a1a1a",
      background: "linear-gradient(180deg, #0f0f18 0%, #050508 100%)",
    }}>
      <h1 style={{
        margin: 0, fontSize: 18, fontWeight: 800,
        fontFamily: "monospace", color: "#FF6B35", letterSpacing: 1,
      }}>RURAL ROUTING RESILIENCE SYSTEM</h1>
      <div style={{ fontSize: 11, color: "#555", marginTop: 4 }}>
        Tomah → Eau Claire → Rice Lake → Superior | Food Distribution | 11hr HOS Window
      </div>
      <DomainLegend />
    </div>

    <div>
      {/* 1. CORRIDOR MAP */}
      <Section id="corridor-map" title="1. CORRIDOR MAP" domains={["R", "W", "C", "I"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <Text>Click any segment for parameters. Dashed lines = degraded comms. Color = weather risk gradient south→north.</Text>
        <CorridorMap activeSegment={activeSegment} setActiveSegment={setActiveSegment} />
      </Section>

      {/* 2. SEGMENT PARAMETERS */}
      <Section id="corridor-segments" title="2. SEGMENT PARAMETERS" domains={["R", "I", "N"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Segment 1: Tomah → Black River Falls</SubHead>
        <Param label="[R] Route" value="I-94 / US-12" />
        <Param label="[R] Distance" value="45" unit="mi" />
        <Param label="[I] Road Class" value="Interstate" note="high maintenance priority" />
        <Param label="[N] Fuel Nodes" value="Tomah (full), BRF (full)" />
        <Param label="[C] Coverage" value="Full cellular" />
        <Param label="[W] Exposure" value="Low" note="sheltered river valley" />

        <SubHead>Segment 2: Black River Falls → Eau Claire</SubHead>
        <Param label="[R] Route" value="I-94" />
        <Param label="[R] Distance" value="60" unit="mi" />
        <Param label="[I] Road Class" value="Interstate" />
        <Param label="[N] Fuel Nodes" value="Osseo, Eau Claire (full)" />
        <Param label="[C] Coverage" value="Full cellular" />
        <Param label="[W] Exposure" value="Moderate" note="open terrain, crosswind corridor" />

        <SubHead>Segment 3: Eau Claire → Chippewa Falls</SubHead>
        <Param label="[R] Route" value="US-53 / WI-29" />
        <Param label="[R] Distance" value="15" unit="mi" />
        <Param label="[I] Road Class" value="US Highway" />
        <Param label="[N] Safe Parking" value="Chippewa Falls truck stop" />
        <Param label="[C] Coverage" value="Full cellular" />

        <SubHead>Segment 4: Chippewa Falls → Ladysmith</SubHead>
        <Param label="[R] Route" value="WI-27" />
        <Param label="[R] Distance" value="45" unit="mi" />
        <Param label="[I] Road Class" value="State Highway" note="lower plow priority" />
        <Param label="[N] Fuel Nodes" value="Cornell (limited)" />
        <Param label="[C] Coverage" value="Degraded" note="cellular gaps 10-15mi" />
        <Param label="[W] Exposure" value="High" note="elevation gain, forest corridor" />

        <SubHead>Segment 5: Ladysmith → Rice Lake</SubHead>
        <Param label="[R] Route" value="WI-27 / US-8" />
        <Param label="[R] Distance" value="30" unit="mi" />
        <Param label="[I] Road Class" value="State/US Highway" />
        <Param label="[C] Coverage" value="Degraded" />
        <Param label="[W] Exposure" value="High" />

        <SubHead>Segment 6: Rice Lake → Hayward</SubHead>
        <Param label="[R] Route" value="WI-48 / US-63" />
        <Param label="[R] Distance" value="35" unit="mi" />
        <Param label="[I] Road Class" value="State Highway" note="minimal winter maintenance" />
        <Param label="[C] Coverage" value="Poor — LoRa mesh only" />
        <Param label="[W] Exposure" value="High" note="lake effect, exposed ridgelines" />
        <Param label="[N] Safe Parking" value="Hayward (limited)" />

        <SubHead>Segment 7: Hayward → Superior</SubHead>
        <Param label="[R] Route" value="US-63 / US-2" />
        <Param label="[R] Distance" value="75" unit="mi" />
        <Param label="[I] Road Class" value="US Highway" note="long exposure, sparse services" />
        <Param label="[C] Coverage" value="Poor — LoRa mesh only" note="longest comms dead zone" />
        <Param label="[W] Exposure" value="Severe" note="Lake Superior weather systems, whiteout risk" />
        <Param label="[N] Safe Parking" value="Solon Springs (emergency only)" />
      </Section>

      {/* 3. WEATHER CASCADE */}
      <Section id="weather-cascade" title="3. WEATHER CASCADE PROPAGATION" domains={["W", "R", "T", "C", "F", "L"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <Text>
          A weather event is never single-domain. It propagates through every other system variable simultaneously.
          The propagation speed and severity increase northward as [C] comms degrade and [N] fallback nodes thin out.
        </Text>

        <CascadeBox target="Winter Storm Warning (Segments 5–7)" effects={[
          { domain: "R", text: "Route capacity drops — WI-27/WI-48 may close. No alternate routes without 60+ mi detour." },
          { domain: "T", text: "HOS clock keeps running during weather hold. 11hr window compresses." },
          { domain: "C", text: "Cellular already degraded. Ice loading on LoRa antennas degrades mesh." },
          { domain: "F", text: "Idle fuel burn spikes — engine must run for heat. 1.0–1.5 gal/hr drain." },
          { domain: "L", text: "Reefer load temp drift begins. Perishable integrity window: 4–6hr without shore power." },
          { domain: "N", text: "Safe parking nodes saturate. Hayward lot holds ~8 trucks max." },
        ]} />

        <CascadeBox target="Fog / Freezing Rain (Segment 2 — Crosswind Corridor)" effects={[
          { domain: "R", text: "I-94 open but speed restricted. Drive time Tomah→EC doubles." },
          { domain: "T", text: "Time budget consumed on 'safe' segment — leaves less margin for northern legs." },
          { domain: "F", text: "Stop-and-go increases fuel consumption 30–40% vs cruise." },
          { domain: "I", text: "Bridge decks freeze before road surface. US-53 Chippewa River crossing = ice point." },
        ]} />

        <SubHead>Seasonal Weather Energy Budget</SubHead>
        <Param label="Nov–Mar" value="High weather load" note="plan +2hr buffer minimum" />
        <Param label="Apr–May" value="Freeze/thaw cycle" note="road damage peaks, [I] degrades" />
        <Param label="Jun–Sep" value="Low weather load" note="but severe thunderstorm risk on open segments" />
        <Param label="Oct" value="Transition" note="first ice events, summer gear still deployed" />
      </Section>

      {/* 4. HOS ENERGY BUDGET */}
      <Section id="hos-energy" title="4. HOS ENERGY BUDGET [T]" domains={["T", "R", "F", "L"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <Text>
          The 11-hour drive window is a fixed energy budget. Every delay, detour, idle event, and weather hold
          is a withdrawal. The budget does not flex. When it hits zero, the truck stops regardless of position.
        </Text>

        <SubHead>Baseline Time Budget — Tomah → Superior</SubHead>
        <Param label="Total Distance" value="~305" unit="mi" />
        <Param label="Cruise Time" value="5.5–6.0" unit="hr" note="at legal speed, no stops" />
        <Param label="Fuel Stops" value="0.5–1.0" unit="hr" note="1-2 stops depending on tank" />
        <Param label="Dock Time" value="1.0–2.0" unit="hr" note="loading/unloading, varies by facility" />
        <Param label="Buffer" value="2.0–4.0" unit="hr" note="THIS IS THE RESILIENCE MARGIN" />

        <SubHead>Budget Drains</SubHead>
        <Param label="Weather Hold" value="-1.0 to -4.0" unit="hr" note="unpredictable, can consume entire buffer" />
        <Param label="Construction Detour" value="-0.5 to -1.5" unit="hr" note="seasonal, knowable in advance" />
        <Param label="Dock Delay" value="-0.5 to -2.0" unit="hr" note="facility-dependent, hardest to predict" />
        <Param label="Fuel Queue" value="-0.25" unit="hr" note="per stop, worse at popular stops" />

        <TensionLine
          title="HOS Exhaustion at Segment 6–7 Boundary"
          domains={["T", "R", "N", "C"]}
          description="If buffer is consumed by weather or dock delays on southern segments, driver reaches
            Hayward–Superior leg with zero margin. This is the longest segment (75mi), worst comms, worst weather,
            and fewest safe parking options. The system fails precisely where it's most dangerous."
          failure="Driver forced to stop on roadside in comms dead zone during weather event. No safe parking. No communication."
        />
      </Section>

      {/* 5. COMMS TOPOLOGY */}
      <Section id="comms-topology" title="5. COMMS TOPOLOGY" domains={["C", "R", "I"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Layer 1: Cellular (Primary)</SubHead>
        <Param label="Coverage" value="Tomah → Chippewa Falls" note="reliable, full data" />
        <Param label="Degradation Begins" value="North of Chippewa Falls" note="gaps on WI-27" />
        <Param label="Effectively Dead" value="Rice Lake → Superior backcountry" />

        <SubHead>Layer 2: CB Radio (Legacy)</SubHead>
        <Param label="Range" value="5–15" unit="mi" note="terrain-dependent" />
        <Param label="Reliability" value="High" note="no infrastructure dependency" />
        <Param label="Bandwidth" value="Voice only" note="no data, no position" />
        <Param label="Coverage" value="Universal where other trucks present" />

        <SubHead>Layer 3: LoRa Mesh (Resilience Layer)</SubHead>
        <Param label="Range (node-to-node)" value="2–10" unit="mi" note="terrain-dependent, higher with elevation" />
        <Param label="Bandwidth" value="Low" note="position + status packets only" />
        <Param label="Infrastructure" value="Fixed nodes at [N] positions + mobile truck nodes" />
        <Param label="Failure Mode" value="Ice loading on antennas, node power loss" />

        <CascadeBox target="Comms Layer Collapse (Segment 7, Winter)" effects={[
          { domain: "C", text: "Cellular dead. LoRa nodes ice-loaded or power-failed. CB range limited by terrain." },
          { domain: "T", text: "Dispatch cannot adjust schedule. Driver operates on last-known plan." },
          { domain: "L", text: "Load status unknown. Reefer alarm cannot propagate." },
          { domain: "N", text: "Cannot coordinate parking. No awareness of other trucks' positions." },
        ]} />
      </Section>

      {/* 6. FUEL + THERMAL */}
      <Section id="fuel-thermal" title="6. FUEL + THERMAL LOAD" domains={["F", "T", "W", "L"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Fuel Energy Budget</SubHead>
        <Param label="Tank Capacity" value="~150" unit="gal" note="Cascadia dual tank" />
        <Param label="Cruise Consumption" value="6.5–7.5" unit="mpg" />
        <Param label="Idle Consumption" value="1.0–1.5" unit="gal/hr" note="winter, heat running" />
        <Param label="Reefer Consumption" value="0.5–1.0" unit="gal/hr" note="separate diesel tank typically" />

        <SubHead>Thermal Load Interaction [F/W]</SubHead>
        <Text>
          In sub-zero conditions, fuel burn has two components: propulsion and thermal maintenance.
          A weather hold doesn't just consume [T] time — it drains [F] fuel at idle rate while the truck produces zero miles.
        </Text>
        <Param label="4hr weather hold" value="4–6" unit="gal consumed" note="zero distance gained" />
        <Param label="Effective MPG during hold" value="0" note="infinite cost per mile" />

        <TensionLine
          title="Fuel Exhaustion vs. Mandatory Idle"
          domains={["F", "W", "T"]}
          description="180-second idle shutoff systems force engine restart cycles that consume more fuel than
            continuous idle and create thermal shock on engine components. In sub-freezing holds,
            the operator must choose between fuel conservation and keeping the cab habitable."
          failure="Fuel exhaustion during extended hold. Cab temperature drops below safe threshold. No fuel nodes within walking distance."
        />
      </Section>

      {/* 7. LOAD INTEGRITY */}
      <Section id="load-integrity" title="7. LOAD INTEGRITY" domains={["L", "T", "W", "F"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Perishable Load Parameters</SubHead>
        <Param label="Target Temp" value="34–38" unit="°F" note="typical refrigerated food" />
        <Param label="Tolerance Window" value="±3" unit="°F" note="before quality degradation begins" />
        <Param label="Reefer Runtime" value="Continuous" note="requires diesel or shore power" />
        <Param label="Shore Power Nodes" value="Tomah, Eau Claire, Superior" note="nothing between EC and Superior" />

        <SubHead>Drift Rate Without Reefer</SubHead>
        <Param label="Summer (90°F ambient)" value="+5°F/hr" note="fast drift, 1hr margin" />
        <Param label="Winter (-10°F ambient)" value="-2°F/hr" note="overcooling risk — frozen product" />
        <Param label="Shoulder Season" value="Variable" note="hardest to predict" />

        <CascadeBox target="Reefer Fuel Exhaustion (Segment 6–7)" effects={[
          { domain: "L", text: "Load temp begins drifting. Clock starts on product integrity." },
          { domain: "F", text: "Reefer tank empty. Main tank cannot cross-feed on most units." },
          { domain: "T", text: "Urgency to reach Superior increases. Pressure to drive in marginal conditions." },
          { domain: "C", text: "Cannot report load status — comms degraded. Receiver has no warning." },
        ]} />
      </Section>

      {/* 8. NODE NETWORK */}
      <Section id="node-network" title="8. NODE NETWORK" domains={["N", "R", "F", "C"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <Text>
          Nodes are safe positions where the system can hold without degrading.
          The node density decreases northward in inverse proportion to the risk level.
        </Text>

        <SubHead>Hub Nodes (Full Capability)</SubHead>
        <Param label="Tomah" value="Fuel, parking, food, comms, shore power, repair" />
        <Param label="Eau Claire" value="Fuel, parking, food, comms, shore power, repair" />
        <Param label="Rice Lake" value="Fuel, parking, comms, limited repair" />
        <Param label="Superior" value="Fuel, parking, food, comms, shore power, repair" />

        <SubHead>Intermediate Nodes (Partial)</SubHead>
        <Param label="Black River Falls" value="Fuel, parking, food" />
        <Param label="Osseo" value="Fuel" note="limited parking" />
        <Param label="Chippewa Falls" value="Fuel, parking" />
        <Param label="Cornell" value="Fuel (limited)" note="may close early" />
        <Param label="Ladysmith" value="Fuel, parking (limited)" />

        <SubHead>Emergency-Only Nodes</SubHead>
        <Param label="Hayward" value="Fuel, minimal parking" note="lot saturates fast in weather events" />
        <Param label="Solon Springs" value="Fuel (if open)" note="reduced hours, single station" />

        <TensionLine
          title="Node Desert: Rice Lake → Superior"
          domains={["N", "R", "C", "F"]}
          description="110 miles with two marginal nodes (Hayward, Solon Springs). Both can close or saturate.
            This is simultaneously the worst-weather, worst-comms, longest-segment portion of the corridor.
            Every domain is maximally stressed at the same time."
          failure="All nodes saturated or closed. Driver has no safe position between Rice Lake and Superior."
        />
      </Section>

      {/* 9. TENSION LINES */}
      <Section id="tension-lines" title="9. TENSION LINES (SYSTEM BREAK POINTS)" domains={["R", "W", "T", "C", "N", "F", "L"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <Text>
          These are the points where multiple domain constraints converge simultaneously.
          A system that looks resilient in any single domain can fail catastrophically when three or more
          domains hit their limits at the same time and position.
        </Text>

        <TensionLine
          title="The Northern Convergence (Segments 6–7)"
          domains={["W", "C", "N", "T", "F", "L"]}
          description="All six operational domains reach their worst state simultaneously
            on the Rice Lake → Superior leg. Weather: severe. Comms: LoRa only. Nodes: sparse.
            HOS: late in shift. Fuel: depleted by southern delays. Load: longest time since shore power."
          failure="Compound cascade. Any single additional stressor (road closure, reefer failure, fuel miscalculation) creates an unrecoverable state."
        />

        <TensionLine
          title="The Dock Time Trap"
          domains={["T", "L", "R"]}
          description="Dock delays at origin (Tomah) or intermediate stops consume [T] budget invisibly.
            A 2-hour dock delay at Tomah feels manageable — but it eliminates the weather buffer
            for the entire northern corridor. The damage is done 200 miles before it manifests."
          failure="Driver enters high-risk segments with zero time margin. Forced to push through marginal conditions or violate HOS."
        />

        <TensionLine
          title="The Idle Shutoff Paradox"
          domains={["F", "W", "T", "L"]}
          description="Mandatory 180-second idle shutoff creates a forced restart cycle during weather holds.
            Each restart: thermal shock on engine, momentary loss of cab heat, fuel spike from cold start.
            System designed to save fuel actually increases consumption and mechanical wear during
            the exact conditions where the truck must hold position."
          failure="Cumulative thermal cycling damages starter, batteries, and engine components. In extreme cold, engine may not restart."
        />

        <TensionLine
          title="The Comms Cliff"
          domains={["C", "N", "T"]}
          description="Cellular coverage doesn't degrade gradually — it drops off a cliff north of Chippewa Falls.
            The transition from 'dispatch can reroute you' to 'you're on your own' happens
            at the exact point where route options narrow and weather risk increases."
          failure="Operator makes decisions with stale information. Dispatch manages a ghost — last known position may be hours old."
        />
      </Section>

      {/* 10. FALLBACK PROTOCOLS */}
      <Section id="fallback-protocol" title="10. FALLBACK PROTOCOLS" domains={["R", "T", "N", "C"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Decision Gates (Go/No-Go)</SubHead>
        <Text>
          Each gate is a position + condition check. Once past a gate, the fallback options narrow.
          The gates are ordered south→north because that's the direction of increasing commitment.
        </Text>

        <Param label="Gate 1: Tomah" value="Full corridor assessment" note="abort costs nothing" />
        <Param label="Gate 2: Eau Claire" value="Check weather Seg 4–7, HOS remaining, fuel state" note="last full-service fallback" />
        <Param label="Gate 3: Rice Lake" value="Final go/no-go for Superior leg" note="if no-go, hold here" />
        <Param label="Gate 4: Hayward" value="Point of commitment" note="past here, must reach Superior or roadside" />

        <CascadeBox target="Gate 3 Hold Decision (Rice Lake)" effects={[
          { domain: "T", text: "Hold consumes HOS — but preserves the option to complete tomorrow" },
          { domain: "F", text: "Fuel available at Rice Lake. Can top off and idle safely." },
          { domain: "C", text: "Cellular still works at Rice Lake. Can coordinate with dispatch." },
          { domain: "L", text: "Shore power not available — reefer on diesel. Clock ticking on load integrity." },
          { domain: "N", text: "Parking available but limited. Early arrival = better position." },
        ]} />

        <SubHead>Alternate Routes</SubHead>
        <Param label="Seg 4 Alt" value="I-94 → US-53 north" note="+30mi but stays on higher-class road" />
        <Param label="Seg 6–7 Alt" value="US-53 → I-35 → Superior" note="+60mi, better road class + comms, higher fuel cost" />
        <Text>
          The I-35 alternate via Duluth adds significant distance but keeps the truck on interstate-class roads
          with full cellular coverage and frequent nodes the entire way. This is the high-energy but low-risk path.
        </Text>
      </Section>

      {/* 11. SEASONAL MODES */}
      <Section id="seasonal-modes" title="11. SEASONAL OPERATING MODES" domains={["W", "R", "F", "T", "I"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Mode 1: Summer (Jun–Sep)</SubHead>
        <Param label="Primary Risk" value="Thunderstorms, construction" />
        <Param label="[W] Buffer" value="+1hr" note="reduced from winter" />
        <Param label="[F] Thermal Load" value="Low" note="no idle heating" />
        <Param label="[L] Risk" value="Overcooling unlikely. Heat drift is primary concern." />
        <Param label="[I] Road State" value="Best condition. Construction zones active." />

        <SubHead>Mode 2: Shoulder (Oct, Apr–May)</SubHead>
        <Param label="Primary Risk" value="Unpredictability" note="conditions change mid-route" />
        <Param label="[W] Buffer" value="+2hr" />
        <Param label="[F] Thermal Load" value="Variable" />
        <Param label="[I] Road State" value="Apr–May: freeze-thaw damage peaks. Potholes, heaves." />

        <SubHead>Mode 3: Winter (Nov–Mar)</SubHead>
        <Param label="Primary Risk" value="Compound cascade (all domains stressed)" />
        <Param label="[W] Buffer" value="+3–4hr minimum" />
        <Param label="[F] Thermal Load" value="Maximum" note="idle burn 1.0–1.5 gal/hr" />
        <Param label="[I] Road State" value="State highways: delayed plowing. County roads: may not be plowed." />
        <Param label="[C] Risk" value="Ice loading on LoRa. Battery drain on mobile nodes." />
        <Param label="Decision Bias" value="Favor I-35 alternate on any marginal forecast" />
      </Section>

      {/* 12. CASCADE SCENARIOS */}
      <Section id="cascade-scenarios" title="12. CASCADE SCENARIOS" domains={["W", "R", "T", "C", "F", "L", "N"]}
        activeSection={activeSection} setActiveSection={setActiveSection}>
        <SubHead>Scenario A: Clean Run (Baseline)</SubHead>
        <Text>Clear weather, no delays. Tomah 0600 → Superior 1200. Buffer: 5hr. All domains nominal.</Text>

        <SubHead>Scenario B: Southern Delay + Northern Weather</SubHead>
        <Text>
          2hr dock delay at Tomah. Depart 0800. Eau Claire by 1100. Weather advisory posted Seg 5–7.
          Gate 2 decision: proceed or hold?
        </Text>
        <CascadeBox target="Scenario B — Gate 2 Decision Tree" effects={[
          { domain: "T", text: "3hr remaining in buffer. Northern leg needs 3.5hr minimum in weather." },
          { domain: "W", text: "Advisory = possible but not certain. Could clear or intensify." },
          { domain: "C", text: "Last reliable comms point. Once past Chippewa, updates stop." },
          { domain: "N", text: "Rice Lake hold possible, but no shore power for reefer." },
          { domain: "L", text: "Reefer has 8hr diesel remaining. Hold at EC = shore power available." },
        ]} />
        <Text style={{ color: "#FFD740" }}>
          Optimal intervention: Hold at Eau Claire. Shore power preserves [L]. Full comms preserves [C].
          Resume when advisory lifts. Accept the [T] cost of the hold — it's cheaper than the compound failure.
        </Text>

        <SubHead>Scenario C: Mid-Route Reefer Failure (Segment 5)</SubHead>
        <CascadeBox target="Scenario C — Reefer Failure at Ladysmith" effects={[
          { domain: "L", text: "Load temp drift begins immediately. 4–6hr integrity window (winter: overcooling)." },
          { domain: "C", text: "Cellular degraded. Cannot confirm with receiver or dispatch." },
          { domain: "T", text: "Pressure to push through to Superior (3.5hr) vs. retreat to Eau Claire (2hr)." },
          { domain: "F", text: "Reefer fuel irrelevant. Main engine fuel nominal." },
          { domain: "R", text: "Forward path: longer, worse conditions. Retreat: shorter, better conditions." },
        ]} />
        <Text style={{ color: "#FFD740" }}>
          Optimal intervention: Retreat to Eau Claire. Shorter distance, better comms, shore power available,
          repair facilities present. The load survives the 2hr return. It may not survive 3.5hr forward
          into degraded conditions with no support infrastructure.
        </Text>

        <SubHead>Scenario D: Full Cascade (Worst Case)</SubHead>
        <Text>
          Winter storm hits Segments 5–7 during transit. Driver at Hayward (Gate 4 — committed).
          WI-48 closed behind. US-63 north: whiteout conditions. Hayward lot: full.
        </Text>
        <TensionLine
          title="Scenario D: Unrecoverable State"
          domains={["W", "R", "T", "C", "N", "F", "L"]}
          description="All domains simultaneously at failure threshold. No route forward or back.
            No safe parking. Comms limited to CB range. HOS clock still running.
            Reefer on remaining diesel. Load integrity window closing."
          failure="This scenario has no good outcome — only least-bad outcomes.
            The only intervention is prevention: this state should never be entered.
            Gate 3 (Rice Lake) is the last point where this cascade can be avoided."
        />
      </Section>
    </div>
  </div>
</div>
```

);
}
