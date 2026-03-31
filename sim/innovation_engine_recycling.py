# innovation_engine_recycling.py
# Systematic Innovation with Dynamic Energy Recycling
# First-principles exploration of new couplings, captures, and loops

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ---------------------------
# 1. Nodes and Baseline
# ---------------------------

nodes = ["G", "T", "M", "B", "A"]

# Current coupling matrix (eta_current)
eta_current = np.array([
    [0.1, 0.6, 0.2, 0.0, 0.1],
    [0.1, 0.2, 0.0, 0.3, 0.4],
    [0.3, 0.0, 0.2, 0.0, 0.5],
    [0.8, 0.0, 0.0, 0.1, 0.1],
    [0.05, 0.3, 0.0, 0.1, 0.55]
])

# Current energy distribution (MW)
E_current = np.array([3.24, 4.85, 0.81, 2.34, 6.46])
E_input = 17.7  # Total input MW

# ---------------------------
# 2. Innovation Class
# ---------------------------

@dataclass
class Innovation:
    name: str
    category: str
    description: str
    target_nodes: List[str]
    new_couplings: List[Tuple[str, str, float]]  # (from, to, efficiency)
    energy_gain_mw: float
    feasibility: float  # 0-1
    cost_scale: str  # low, medium, high
    first_principles_basis: str

# ---------------------------
# 3. Innovation Engine
# ---------------------------

class InnovationEngine:
    """Generate and evaluate innovations with dynamic energy recycling."""

    def __init__(self, current_energy, current_coupling):
        self.current_energy = current_energy
        self.current_coupling = current_coupling
        self.innovations: List[Innovation] = []
        self._generate_innovations()

    def _generate_innovations(self):
        """Populate innovations (same as previous engine)."""
        # Example: only a few for brevity
        self.innovations.append(Innovation(
            name="High-Altitude Kite Turbines",
            category="Atmospheric Capture",
            description="Tethered kites capture high-altitude wind energy",
            target_nodes=["M"],
            new_couplings=[("A", "M", 0.25), ("M", "G", 0.20)],
            energy_gain_mw=2.5,
            feasibility=0.75,
            cost_scale="medium",
            first_principles_basis="Wind power scales with cube of velocity; higher altitude → higher velocity"
        ))
        self.innovations.append(Innovation(
            name="Thermoelectric Waste Heat Recovery",
            category="Thermal Recovery",
            description="Capture thermal waste via Seebeck effect",
            target_nodes=["T", "G"],
            new_couplings=[("T", "G", 0.15), ("T", "M", 0.10)],
            energy_gain_mw=1.8,
            feasibility=0.85,
            cost_scale="medium",
            first_principles_basis="Seebeck effect: temperature gradient generates voltage"
        ))
        # Additional innovations can be added here...

    # ---------------------------
    # Dynamic Coupling Model
    # ---------------------------

    def run_dynamic_model(self, coupling_matrix, base_energy, injected_energy=0.0, tolerance=0.01, max_iter=100):
        """
        Propagate energy across the network until convergence.
        - base_energy: starting energy distribution
        - injected_energy: MW directly added by innovation
        """
        E = base_energy + injected_energy
        for _ in range(max_iter):
            E_next = coupling_matrix.T @ E
            if np.all(np.abs(E_next - E) < tolerance):
                break
            E = E_next
        return E

    # ---------------------------
    # Evaluate Single Innovation
    # ---------------------------

    def evaluate_innovation(self, innovation: Innovation):
        # Update coupling matrix
        eta_new = self.current_coupling.copy()
        for frm, to, eff in innovation.new_couplings:
            i = nodes.index(frm)
            j = nodes.index(to)
            eta_new[i, j] = max(eta_new[i, j], eff)

        # Run dynamic energy propagation including innovation injection
        E_new = self.run_dynamic_model(eta_new, self.current_energy, innovation.energy_gain_mw)

        # Compute gain
        gain = np.sum(E_new) - np.sum(self.current_energy)
        eff_current = np.sum(self.current_energy) / E_input
        eff_new = np.sum(E_new) / E_input

        return {
            "name": innovation.name,
            "gain_mw": gain,
            "gain_percent": gain / np.sum(self.current_energy) * 100,
            "new_efficiency": eff_new * 100,
            "feasibility": innovation.feasibility,
            "cost_scale": innovation.cost_scale,
            "new_distribution": {nodes[i]: E_new[i] for i in range(len(nodes))},
            "innovation": innovation
        }

    # ---------------------------
    # Prioritize Innovations
    # ---------------------------

    def prioritize_innovations(self):
        results = []
        for innov in self.innovations:
            eval_result = self.evaluate_innovation(innov)
            # Impact/cost ratio
            cost_weight = {"low": 3, "medium": 2, "high": 1}
            impact_cost = eval_result["gain_mw"] * cost_weight[innov.cost_scale]
            eval_result["impact_cost_ratio"] = impact_cost
            eval_result["category"] = innov.category
            results.append(eval_result)
        # Sort descending by impact/cost
        results.sort(key=lambda x: -x["impact_cost_ratio"])
        return results

# ---------------------------
# 4. Run Analysis
# ---------------------------

def run_analysis():
    engine = InnovationEngine(E_current, eta_current)
    prioritized = engine.prioritize_innovations()

    print("=" * 80)
    print("DYNAMIC RECYCLING INNOVATION ANALYSIS")
    print("=" * 80)

    print(f"BASELINE TOTAL POWER: {np.sum(E_current):.2f} MW | Efficiency: {np.sum(E_current)/E_input*100:.1f}%")

    for i, item in enumerate(prioritized, 1):
        innov = item["innovation"]
        print(f"\n{i}. {innov.name} ({innov.category})")
        print(f"   Gain: +{item['gain_mw']:.2f} MW (+{item['gain_percent']:.1f}%)")
        print(f"   New Efficiency: {item['new_efficiency']:.1f}%")
        print(f"   Feasibility: {innov.feasibility:.0%} | Cost: {innov.cost_scale}")
        print(f"   Node Distribution: {item['new_distribution']}")

    return prioritized

# ---------------------------
# 5. Execution
# ---------------------------

if __name__ == "__main__":
    run_analysis()
