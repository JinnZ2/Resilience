#!/usr/bin/env python3
# MODULE: sim/innovation_engine_recycling_full.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: tool
# Full recycling innovation engine with complete pipeline
# innovation_engine_recycling_full.py
# Full Innovation Suite with Dynamic Energy Recycling
# Multiple innovations, cumulative effects, and optimization
# CC0 public domain — github.com/JinnZ2/urban-resilience-sim

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Note: requires numpy for matrix operations. pip install numpy")

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import itertools

if not HAS_NUMPY:
    raise SystemExit(1)

# ---------------------------
# 1. Nodes and Baseline
# ---------------------------

nodes = ["G", "T", "M", "B", "A"]
n_nodes = len(nodes)

eta_current = np.array([
    [0.1, 0.6, 0.2, 0.0, 0.1],
    [0.1, 0.2, 0.0, 0.3, 0.4],
    [0.3, 0.0, 0.2, 0.0, 0.5],
    [0.8, 0.0, 0.0, 0.1, 0.1],
    [0.05, 0.3, 0.0, 0.1, 0.55]
])

E_current = np.array([3.24, 4.85, 0.81, 2.34, 6.46])
E_input = 17.7

# ---------------------------
# 2. Innovation Class
# ---------------------------

@dataclass
class Innovation:
    name: str
    category: str
    description: str
    target_nodes: List[str]
    new_couplings: List[Tuple[str, str, float]]
    energy_gain_mw: float
    feasibility: float
    cost_scale: str
    first_principles_basis: str
    coupling_improvements: List[Tuple[str, str, float]] = field(default_factory=list)

# ---------------------------
# 3. Full Innovation Library
# ---------------------------

class FullInnovationLibrary:
    @staticmethod
    def get_all_innovations() -> List[Innovation]:
        return [
            # Atmospheric Capture
            Innovation("High-Altitude Kite Turbines", "Atmospheric Capture",
                "Tethered kites at 500-2000ft capture jet stream energy",
                ["M"], [("A","M",0.25),("M","G",0.20)], 2.5, 0.75, "medium",
                "Wind power scales with cube of velocity; 2000ft winds 3-5x surface"),
            Innovation("Atmospheric Electrostatic Harvesting", "Atmospheric Capture",
                "Capture charge differential between ionosphere and ground",
                ["M","A"], [("A","M",0.15),("A","G",0.10)], 1.2, 0.5, "high",
                "Earth-ionosphere potential gradient: ~400kV; tall structures as antennas"),
            # Solar
            Innovation("Concentrated Solar Thermal", "Solar",
                "Mirrors concentrate sunlight for high-temperature heat and power",
                ["T","G"], [("A","T",0.40),("T","G",0.20)], 3.0, 0.8, "high",
                "Concentration ratios 500-1000x; temperatures 500-1000C"),
            Innovation("Agrivoltaics", "Solar",
                "Solar panels above crops; crops cool panels, increase efficiency",
                ["G","B"], [("G","B",0.20),("B","G",0.10)], 1.0, 0.85, "medium",
                "Panel efficiency increases 2-5% when cooled; dual land use"),
            # Thermal Recovery
            Innovation("Thermoelectric Waste Heat Recovery", "Thermal Recovery",
                "Thermoelectric generators on all waste heat streams",
                ["T","G"], [("T","G",0.15),("T","M",0.10)], 1.8, 0.85, "medium",
                "Seebeck effect: temperature gradient generates voltage"),
            Innovation("Phase-Change Thermal Storage", "Thermal Recovery",
                "Store thermal energy in phase-change materials",
                ["T","G"], [("T","G",0.25),("T","B",0.20)], 1.5, 0.8, "medium",
                "Latent heat storage; energy density 5-10x sensible heat"),
            # Storage
            Innovation("Sand Thermal Battery", "Storage",
                "Store excess solar/wind as heat in desert sand",
                ["T","G","A"], [("G","T",0.50),("T","G",0.25)], 2.2, 0.85, "medium",
                "Sand specific heat: 800 J/kg*K; 1 m3 stores 200 kWh at 400C dT"),
            Innovation("Gravity Storage in Vertical Shafts", "Storage",
                "Lift weights in elevator shafts; release to generate power",
                ["G","M"], [("G","G",0.20),("M","G",0.15)], 1.5, 0.75, "high",
                "Potential energy: mgh; 1000 tons at 100m = 272 kWh"),
            # Biological
            Innovation("Enhanced Biogas from Multiple Feedstocks", "Biological",
                "Co-digestion of human waste, agricultural waste, food waste",
                ["B","G"], [("B","G",0.85),("B","M",0.15)], 2.0, 0.9, "low",
                "Anaerobic digestion yields 0.5-0.7 m3 biogas per kg organic matter"),
            Innovation("Algae CO2 Capture + Biofuel", "Biological",
                "Algae capture CO2 from biogas; produce biodiesel and protein",
                ["B","M","A"], [("B","G",0.30),("B","M",0.20),("A","B",0.15)], 1.5, 0.7, "medium",
                "Algae lipid content 20-50%; CO2 capture rate 1.8 kg CO2 per kg biomass"),
            # Mobility
            Innovation("Regenerative Braking Network", "Mobility",
                "All vehicles and transit capture braking energy to grid",
                ["M","G"], [("M","G",0.35),("M","B",0.10)], 1.2, 0.9, "medium",
                "Regenerative braking recovers 15-30% of kinetic energy"),
            Innovation("Piezoelectric Roads", "Mobility",
                "Roads generate electricity from vehicle weight and vibration",
                ["M","G"], [("M","G",0.15),("M","B",0.05)], 0.8, 0.7, "high",
                "Piezoelectric effect: 1-5 W per vehicle pass"),
            # Coupling Enhancement
            Innovation("Thermal-to-Biological Accelerator", "Coupling",
                "Waste heat accelerates biogas digestion (thermophilic)",
                ["T","B"], [("T","B",0.45)], 1.0, 0.8, "low",
                "Biogas yield increases 2-3x at 55C vs 35C"),
            Innovation("CO2-Algae-Biochar Loop", "Coupling",
                "CO2 from biogas -> algae -> biochar -> soil -> more biomass",
                ["A","B","G"], [("A","B",0.25),("B","G",0.20),("B","T",0.15)], 1.8, 0.7, "medium",
                "Carbon-negative loop; each cycle sequesters more carbon"),
            # Geothermal
            Innovation("Deep Geothermal Wells", "Geothermal",
                "Enhanced geothermal systems at 3-5km depth",
                ["A","T"], [("A","T",0.50),("A","G",0.30)], 5.0, 0.65, "high",
                "Geothermal gradient 25-30C/km; EGS can access 10-50x current capacity"),
        ]


# ---------------------------
# 4. Innovation Engine
# ---------------------------

class DynamicInnovationEngine:
    def __init__(self, current_energy, current_coupling, input_power):
        self.current_energy = current_energy
        self.current_coupling = current_coupling
        self.input_power = input_power
        self.innovation_library = FullInnovationLibrary()

    def run_dynamic_model(self, coupling_matrix, base_energy, injected_energy=0.0,
                          tolerance=0.01, max_iter=100):
        E = base_energy + injected_energy
        history = [E.copy()]
        for _ in range(max_iter):
            E_next = coupling_matrix.T @ E
            history.append(E_next.copy())
            if np.all(np.abs(E_next - E) < tolerance):
                break
            E = E_next
        return E, history

    def evaluate_innovation(self, innovation: Innovation):
        eta_new = self.current_coupling.copy()
        for frm, to, eff in innovation.new_couplings:
            i, j = nodes.index(frm), nodes.index(to)
            eta_new[i, j] = max(eta_new[i, j], eff)
        E_new, history = self.run_dynamic_model(eta_new, self.current_energy,
                                                 innovation.energy_gain_mw)
        baseline_total = np.sum(self.current_energy)
        new_total = np.sum(E_new)
        gain = new_total - baseline_total
        return {
            "name": innovation.name, "category": innovation.category,
            "gain_mw": gain, "gain_percent": gain / baseline_total * 100,
            "new_efficiency": new_total / self.input_power * 100,
            "feasibility": innovation.feasibility, "cost_scale": innovation.cost_scale,
            "new_distribution": {nodes[i]: E_new[i] for i in range(n_nodes)},
            "innovation": innovation, "convergence_iterations": len(history),
        }

    def evaluate_multiple_innovations(self, innovations: List[Innovation]) -> Dict:
        eta = self.current_coupling.copy()
        total_injected = 0
        for innov in innovations:
            for frm, to, eff in innov.new_couplings:
                i, j = nodes.index(frm), nodes.index(to)
                eta[i, j] = max(eta[i, j], eff)
            total_injected += innov.energy_gain_mw
        E_final, history = self.run_dynamic_model(eta, self.current_energy, total_injected)
        baseline = np.sum(self.current_energy)
        final = np.sum(E_final)
        return {
            "innovations_applied": [i.name for i in innovations],
            "count": len(innovations), "total_injected_mw": total_injected,
            "baseline_total_mw": baseline, "final_total_mw": final,
            "gain_mw": final - baseline, "gain_percent": (final - baseline) / baseline * 100,
            "final_efficiency": final / self.input_power * 100,
            "final_distribution": {nodes[i]: E_final[i] for i in range(n_nodes)},
            "convergence_iterations": len(history),
        }

    def prioritize_innovations(self) -> List[Dict]:
        results = []
        for innov in self.innovation_library.get_all_innovations():
            r = self.evaluate_innovation(innov)
            cost_weight = {"low": 3, "medium": 2, "high": 1}
            r["impact_cost_ratio"] = r["gain_mw"] * cost_weight[innov.cost_scale]
            results.append(r)
        results.sort(key=lambda x: -x["impact_cost_ratio"])
        return results

    def find_optimal_combination(self, max_innovations: int = 4) -> Dict:
        all_innov = self.innovation_library.get_all_innovations()
        best_result, best_gain = None, 0
        for n in range(1, max_innovations + 1):
            for combo in itertools.combinations(all_innov, n):
                result = self.evaluate_multiple_innovations(list(combo))
                if result["gain_mw"] > best_gain:
                    best_gain = result["gain_mw"]
                    best_result = result
        return best_result


# ---------------------------
# 5. Run
# ---------------------------

if __name__ == "__main__":
    engine = DynamicInnovationEngine(E_current, eta_current, E_input)
    baseline = np.sum(E_current)

    print("=" * 70)
    print("  DYNAMIC RECYCLING INNOVATION ENGINE")
    print(f"  Baseline: {baseline:.2f} MW, {baseline/E_input*100:.1f}% efficiency")
    print("=" * 70)

    prioritized = engine.prioritize_innovations()
    print(f"\n  TOP 10 INNOVATIONS (by impact/cost):")
    for i, item in enumerate(prioritized[:10], 1):
        print(f"    {i:2d}. {item['name']:<40s} +{item['gain_mw']:.2f} MW  "
              f"({item['innovation'].cost_scale})  ratio={item['impact_cost_ratio']:.2f}")

    top5 = [item["innovation"] for item in prioritized[:5]]
    cumulative = engine.evaluate_multiple_innovations(top5)
    print(f"\n  TOP 5 CUMULATIVE:")
    print(f"    Baseline: {cumulative['baseline_total_mw']:.2f} MW")
    print(f"    Final:    {cumulative['final_total_mw']:.2f} MW "
          f"(+{cumulative['gain_percent']:.0f}%)")
    print(f"    Efficiency: {cumulative['final_efficiency']:.1f}%")

    print(f"\n  SEARCHING OPTIMAL COMBO (up to 4)...")
    optimal = engine.find_optimal_combination(4)
    if optimal:
        print(f"    Best: {', '.join(optimal['innovations_applied'])}")
        print(f"    Gain: +{optimal['gain_mw']:.2f} MW ({optimal['gain_percent']:.0f}%)")

    print(f"\n{'='*70}\n")
