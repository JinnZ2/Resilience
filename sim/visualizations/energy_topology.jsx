import { useState, useEffect, useRef } from "react";

const PHI  = 1.6180339887;
const IPHI = 0.6180339887;
const PHI2 = 0.3819660113;

// ── NODE DATA ─────────────────────────────────────────────────────────────────

const NODES = [
  {
    id: "rural_elder_network",
    label: "Rural Elder Network",
    zone: "rural_fringe",
    x: 15, y: 25,
    energy: { total: 0.88, knowledge: 0.95, social: 0.88 },
    net_flow: 0.12,
    grandmother_test: true,
  },
  {
    id: "rural_farm_network",
    label: "Farm Network",
    zone: "rural_fringe",
    x: 20, y: 45,
    energy: { total: 0.85, knowledge: 0.88, social: 0.85 },
    net_flow: 0.10,
    grandmother_test: true,
  },
  {
    id: "volunteer_fire",
    label: "Volunteer Fire/EMT",
    zone: "rural_fringe",
    x: 12, y: 60,
    energy: { total: 0.80, knowledge: 0.80, social: 0.90 },
    net_flow: 0.08,
    grandmother_test: true,
  },
  {
    id: "food_distribution_driver",
    label: "Food Distribution Driver",
    zone: "corridor",
    x: 42, y: 38,
    energy: { total: 0.68, knowledge: 0.85, social: 0.70 },
    net_flow: 0.02,
    grandmother_test: true,
    note: "Load-bearing. Invisible to PRAYER index.",
  },
  {
    id: "willy_street_coop",
    label: "Willy Street Coop",
    zone: "inner_city",
    x: 58, y: 30,
    energy: { total: 0.75, knowledge: 0.65, social: 0.80 },
    net_flow: 0.06,
    grandmother_test: true,
  },
  {
    id: "inner_mutual_aid",
    label: "Inner City Mutual Aid",
    zone: "inner_city",
    x: 62, y: 50,
    energy: { total: 0.60, knowledge: 0.62, social: 0.78 },
    net_flow: 0.03,
    grandmother_test: true,
  },
  {
    id: "faith_network",
    label: "Faith Network",
    zone: "inner_city",
    x: 55, y: 62,
    energy: { total: 0.65, knowledge: 0.70, social: 0.82 },
    net_flow: 0.04,
    grandmother_test: true,
  },
  {
    id: "suburban_household_a",
    label: "Suburban Household A",
    zone: "suburban_sprawl",
    x: 38, y: 62,
    energy: { total: 0.45, knowledge: 0.30, social: 0.22 },
    net_flow: -0.04,
    grandmother_test: false,
  },
  {
    id: "suburban_household_b",
    label: "Suburban Household B",
    zone: "suburban_sprawl",
    x: 48, y: 72,
    energy: { total: 0.43, knowledge: 0.28, social: 0.20 },
    net_flow: -0.05,
    grandmother_test: false,
  },
  {
    id: "absentee_landlord",
    label: "Absentee Landlord",
    zone: "extraction",
    x: 75, y: 20,
    energy: { total: 0.85, knowledge: 0.40, social: 0.20 },
    net_flow: -0.18,
    grandmother_test: false,
    note: "High monetary energy. Extraction mode. Low conductance.",
  },
];

// ── EDGE DATA ──────────────────────────────────────────────────────────────────

const EDGES = [
  // rural mesh — phi-aligned
  { from: "rural_elder_network",      to: "rural_farm_network",      trust: 0.90, extraction: false },
  { from: "rural_elder_network",      to: "volunteer_fire",          trust: 0.80, extraction: false },
  { from: "rural_farm_network",       to: "volunteer_fire",          trust: 0.85, extraction: false },
  // corridor bridge
  { from: "rural_elder_network",      to: "food_distribution_driver", trust: 0.70, extraction: false },
  { from: "rural_farm_network",       to: "food_distribution_driver", trust: 0.65, extraction: false },
  { from: "food_distribution_driver", to: "willy_street_coop",        trust: 0.70, extraction: false },
  { from: "food_distribution_driver", to: "inner_mutual_aid",         trust: 0.60, extraction: false },
  // inner city mesh
  { from: "willy_street_coop",        to: "inner_mutual_aid",        trust: 0.75, extraction: false },
  { from: "inner_mutual_aid",         to: "faith_network",           trust: 0.72, extraction: false },
  { from: "faith_network",            to: "willy_street_coop",       trust: 0.68, extraction: false },
  // suburban isolation
  { from: "suburban_household_a",     to: "suburban_household_b",    trust: 0.25, extraction: false },
  { from: "suburban_household_a",     to: "willy_street_coop",       trust: 0.35, extraction: false },
  // extraction flows
  { from: "absentee_landlord",        to: "inner_mutual_aid",        trust: 0.15, extraction: true  },
  { from: "absentee_landlord",        to: "faith_network",           trust: 0.10, extraction: true  },
];

// ── HELPERS ───────────────────────────────────────────────────────────────────

function nodeColor(node) {
  if (!node.grandmother_test)  return "#ef4444"; // red — nonviable
  if (node.net_flow < 0)       return "#f59e0b"; // yellow — extracting but viable
  if (node.net_flow >= 0.08)   return "#22c55e"; // bright green — building strong
  return "#86efac";                               // light green — building
}

function nodeStatus(node) {
  if (!node.grandmother_test)  return "NONVIABLE";
  if (node.net_flow < 0)       return "EXTRACTING";
  return "BUILDING";
}

function edgeStyle(edge) {
  if (edge.extraction) return { color: "#ef4444", dash: "4,4", width: 2 };
  if (edge.trust >= IPHI)  return { color: "#22c55e", dash: null, width: 3 };
  if (edge.trust >= PHI2)  return { color: "#86efac", dash: null, width: 1.5 };
  if (edge.trust >= 0.1)   return { color: "#fde047", dash: "6,4", width: 1 };
  return { color: "#6b7280", dash: "2,6", width: 1 };
}

function edgeLabel(edge) {
  if (edge.extraction)     return "⚡ extraction";
  if (edge.trust >= IPHI)  return "φ-aligned";
  if (edge.trust >= PHI2)  return "linear";
  if (edge.trust >= 0.1)   return "restricted";
  return "isolated";
}

function zoneColor(zone) {
  const colors = {
    rural_fringe:    "rgba(34,197,94,0.06)",
    inner_city:      "rgba(99,102,241,0.06)",
    suburban_sprawl: "rgba(245,158,11,0.06)",
    corridor:        "rgba(148,163,184,0.04)",
    extraction:      "rgba(239,68,68,0.06)",
  };
  return colors[zone] || "transparent";
}

// ── MAIN COMPONENT ────────────────────────────────────────────────────────────

export default function EnergyTopologyMap() {
  const [selected, setSelected]   = useState(null);
  const [showZones, setShowZones] = useState(true);
  const [showEdges, setShowEdges] = useState(true);
  const [filter, setFilter]       = useState("all");
  const svgRef = useRef(null);

  const W = 100; // viewBox units
  const H = 100;

  const filteredNodes = NODES.filter(n => {
    if (filter === "building")  return n.grandmother_test && n.net_flow >= 0;
    if (filter === "stressed")  return n.grandmother_test && n.net_flow < 0;
    if (filter === "nonviable") return !n.grandmother_test;
    return true;
  });

  const filteredIds = new Set(filteredNodes.map(n => n.id));

  const selectedNode = selected
    ? NODES.find(n => n.id === selected)
    : null;

  const selectedEdges = selected
    ? EDGES.filter(e => e.from === selected || e.to === selected)
    : [];

  // zone bounding boxes (approximate)
  const zones = [
    { id: "rural_fringe",    label: "Rural Fringe",    x: 5,  y: 15, w: 32, h: 55 },
    { id: "corridor",        label: "Corridor",         x: 35, y: 28, w: 15, h: 20 },
    { id: "suburban_sprawl", label: "Suburban Sprawl",  x: 32, y: 55, w: 22, h: 24 },
    { id: "inner_city",      label: "Inner City",       x: 50, y: 22, w: 30, h: 50 },
    { id: "extraction",      label: "Extraction",       x: 68, y: 10, w: 18, h: 16 },
  ];

  return (
    <div style={{
      background: "#0f172a",
      minHeight: "100vh",
      color: "#e2e8f0",
      fontFamily: "monospace",
      padding: "12px",
    }}>
      {/* HEADER */}
      <div style={{ marginBottom: 8 }}>
        <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 2 }}>
          urban-resilience-sim / sim / energy_games
        </div>
        <div style={{ fontSize: 16, fontWeight: "bold", color: "#f1f5f9" }}>
          Energy Topology Map — Madison WI
        </div>
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>
          Trust = conductance · Energy = current · φ = optimal load
        </div>
      </div>

      {/* CONTROLS */}
      <div style={{ display: "flex", gap: 6, marginBottom: 8, flexWrap: "wrap" }}>
        {[
          ["all", "All Nodes"],
          ["building", "Building"],
          ["stressed", "Stressed"],
          ["nonviable", "Nonviable"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            style={{
              padding: "3px 8px",
              fontSize: 11,
              borderRadius: 4,
              border: "1px solid",
              borderColor: filter === key ? "#22c55e" : "#334155",
              background: filter === key ? "#14532d" : "#1e293b",
              color: filter === key ? "#22c55e" : "#94a3b8",
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
        <button
          onClick={() => setShowZones(!showZones)}
          style={{
            padding: "3px 8px", fontSize: 11, borderRadius: 4,
            border: "1px solid #334155",
            background: showZones ? "#1e3a5f" : "#1e293b",
            color: showZones ? "#93c5fd" : "#64748b",
            cursor: "pointer",
          }}
        >
          {showZones ? "Zones ON" : "Zones OFF"}
        </button>
        <button
          onClick={() => setShowEdges(!showEdges)}
          style={{
            padding: "3px 8px", fontSize: 11, borderRadius: 4,
            border: "1px solid #334155",
            background: showEdges ? "#1e3a5f" : "#1e293b",
            color: showEdges ? "#93c5fd" : "#64748b",
            cursor: "pointer",
          }}
        >
          {showEdges ? "Flows ON" : "Flows OFF"}
        </button>
      </div>

      {/* SVG MAP */}
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        style={{
          width: "100%",
          background: "#0f172a",
          border: "1px solid #1e293b",
          borderRadius: 6,
          display: "block",
        }}
      >
        <defs>
          <marker id="arrow-green" markerWidth="6" markerHeight="6"
            refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L6,3 z" fill="#22c55e" />
          </marker>
          <marker id="arrow-yellow" markerWidth="6" markerHeight="6"
            refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L6,3 z" fill="#fde047" />
          </marker>
          <marker id="arrow-red" markerWidth="6" markerHeight="6"
            refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L6,3 z" fill="#ef4444" />
          </marker>
        </defs>

        {/* ZONE BACKGROUNDS */}
        {showZones && zones.map(zone => (
          <g key={zone.id}>
            <rect
              x={zone.x} y={zone.y}
              width={zone.w} height={zone.h}
              fill={zoneColor(zone.id)}
              stroke={zoneColor(zone.id).replace("0.06", "0.3")}
              strokeWidth={0.3}
              rx={1}
            />
            <text
              x={zone.x + 1} y={zone.y + 3.5}
              fontSize={2.2} fill="#475569"
              fontFamily="monospace"
            >
              {zone.label}
            </text>
          </g>
        ))}

        {/* EDGES */}
        {showEdges && EDGES.map((edge, i) => {
          const fromNode = NODES.find(n => n.id === edge.from);
          const toNode   = NODES.find(n => n.id === edge.to);
          if (!fromNode || !toNode) return null;
          if (!filteredIds.has(edge.from) && !filteredIds.has(edge.to)) return null;

          const style = edgeStyle(edge);
          const isSelected = selected &&
            (edge.from === selected || edge.to === selected);

          const markerId = edge.extraction ? "arrow-red"
            : edge.trust >= IPHI ? "arrow-green"
            : "arrow-yellow";

          // offset slightly so bidirectional edges don't overlap
          const dx = toNode.x - fromNode.x;
          const dy = toNode.y - fromNode.y;
          const len = Math.sqrt(dx*dx + dy*dy) || 1;
          const ox = -dy / len * 0.8;
          const oy =  dx / len * 0.8;

          return (
            <g key={i} opacity={isSelected ? 1 : selected ? 0.25 : 0.7}>
              <line
                x1={fromNode.x + ox} y1={fromNode.y + oy}
                x2={toNode.x   + ox} y2={toNode.y   + oy}
                stroke={style.color}
                strokeWidth={isSelected ? style.width * 1.8 : style.width}
                strokeDasharray={style.dash || ""}
                markerEnd={`url(#${markerId})`}
              />
              {isSelected && (
                <text
                  x={(fromNode.x + toNode.x) / 2 + ox}
                  y={(fromNode.y + toNode.y) / 2 + oy - 1}
                  fontSize={1.8}
                  fill={style.color}
                  textAnchor="middle"
                  fontFamily="monospace"
                >
                  {edgeLabel(edge)} ({edge.trust.toFixed(2)})
                </text>
              )}
            </g>
          );
        })}

        {/* NODES */}
        {NODES.filter(n => filteredIds.has(n.id)).map(node => {
          const color    = nodeColor(node);
          const isSelected = selected === node.id;
          const r        = isSelected ? 4.2 : 3.2;

          return (
            <g
              key={node.id}
              onClick={() => setSelected(
                selected === node.id ? null : node.id
              )}
              style={{ cursor: "pointer" }}
            >
              {/* glow */}
              <circle
                cx={node.x} cy={node.y}
                r={r + 1.5}
                fill={color}
                opacity={isSelected ? 0.25 : 0.08}
              />
              {/* node */}
              <circle
                cx={node.x} cy={node.y}
                r={r}
                fill={color}
                opacity={isSelected ? 1.0 : filteredIds.has(node.id) ? 0.85 : 0.2}
                stroke={isSelected ? "#fff" : "transparent"}
                strokeWidth={0.4}
              />
              {/* energy ring */}
              <circle
                cx={node.x} cy={node.y}
                r={r}
                fill="none"
                stroke="#0f172a"
                strokeWidth={r * (1 - node.energy.total)}
                opacity={0.5}
              />
              {/* label */}
              <text
                x={node.x}
                y={node.y + r + 2.5}
                fontSize={1.8}
                fill="#cbd5e1"
                textAnchor="middle"
                fontFamily="monospace"
              >
                {node.label}
              </text>
              <text
                x={node.x}
                y={node.y + r + 4.5}
                fontSize={1.5}
                fill={color}
                textAnchor="middle"
                fontFamily="monospace"
              >
                {nodeStatus(node)}
              </text>
            </g>
          );
        })}
      </svg>

      {/* LEGEND */}
      <div style={{
        display: "flex", gap: 12, flexWrap: "wrap",
        marginTop: 8, fontSize: 10, color: "#64748b",
      }}>
        {[
          ["#22c55e", "BUILDING — viable, positive flow"],
          ["#f59e0b", "STRESSED — viable, negative flow"],
          ["#ef4444", "NONVIABLE — below survival threshold"],
        ].map(([color, label]) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div style={{
              width: 10, height: 10, borderRadius: "50%",
              background: color, flexShrink: 0,
            }} />
            {label}
          </div>
        ))}
      </div>
      <div style={{
        display: "flex", gap: 12, flexWrap: "wrap",
        marginTop: 4, fontSize: 10, color: "#64748b",
      }}>
        {[
          ["#22c55e", "━━", "φ-aligned flow (trust > φ⁻¹)"],
          ["#86efac", "━━", "linear flow (trust > φ⁻²)"],
          ["#fde047", "╌╌", "restricted flow"],
          ["#ef4444", "╌╌", "⚡ extraction"],
        ].map(([color, dash, label]) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ color, fontSize: 13 }}>{dash}</span>
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* SELECTED NODE DETAIL */}
      {selectedNode && (
        <div style={{
          marginTop: 10,
          background: "#1e293b",
          border: `1px solid ${nodeColor(selectedNode)}`,
          borderRadius: 6,
          padding: 10,
          fontSize: 11,
        }}>
          <div style={{
            fontSize: 13, fontWeight: "bold",
            color: nodeColor(selectedNode),
            marginBottom: 6,
          }}>
            {selectedNode.label}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
            {[
              ["Zone",           selectedNode.zone],
              ["Status",         nodeStatus(selectedNode)],
              ["Net flow",       selectedNode.net_flow >= 0
                                  ? `+${selectedNode.net_flow.toFixed(3)}`
                                  : selectedNode.net_flow.toFixed(3)],
              ["Energy total",   selectedNode.energy.total.toFixed(3)],
              ["Knowledge",      selectedNode.energy.knowledge.toFixed(3)],
              ["Social",         selectedNode.energy.social.toFixed(3)],
              ["Grandmother ✓",  selectedNode.grandmother_test ? "PASS" : "FAIL"],
              ["φ threshold",    IPHI.toFixed(4)],
            ].map(([k, v]) => (
              <div key={k}>
                <span style={{ color: "#64748b" }}>{k}: </span>
                <span style={{ color: "#e2e8f0" }}>{v}</span>
              </div>
            ))}
          </div>

          {selectedNode.note && (
            <div style={{
              marginTop: 6, padding: "4px 6px",
              background: "#0f172a", borderRadius: 4,
              color: "#94a3b8", fontStyle: "italic",
            }}>
              {selectedNode.note}
            </div>
          )}

          {selectedEdges.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <div style={{ color: "#64748b", marginBottom: 4 }}>
                Connections:
              </div>
              {selectedEdges.map((edge, i) => {
                const other = edge.from === selectedNode.id ? edge.to : edge.from;
                const otherNode = NODES.find(n => n.id === other);
                const style = edgeStyle(edge);
                const direction = edge.from === selectedNode.id ? "→" : "←";
                return (
                  <div key={i} style={{
                    display: "flex", alignItems: "center",
                    gap: 6, marginBottom: 2,
                    color: style.color,
                  }}>
                    <span>{direction}</span>
                    <span>{otherNode?.label || other}</span>
                    <span style={{ color: "#475569" }}>
                      trust: {edge.trust.toFixed(2)}
                    </span>
                    <span style={{ fontSize: 10, color: "#334155" }}>
                      [{edgeLabel(edge)}]
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          <div style={{
            marginTop: 8, fontSize: 10,
            color: "#475569", borderTop: "1px solid #334155",
            paddingTop: 6,
          }}>
            PRAYER index score: [REDACTED] — not useful here
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div style={{
        marginTop: 10, fontSize: 10, color: "#334155",
        borderTop: "1px solid #1e293b", paddingTop: 6,
      }}>
        <div>CC0 — public domain · github.com/JinnZ2/urban-resilience-sim</div>
        <div style={{ marginTop: 2 }}>
          "The city boundary doesn't match the energy topology." — DeepSeek, March 2026
        </div>
        <div>
          "The green mesh crosses county lines." — Three AIs, same fuel stop.
        </div>
      </div>
    </div>
  );
}
