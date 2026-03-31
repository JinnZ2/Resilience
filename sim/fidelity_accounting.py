#!/usr/bin/env python3
"""
sim/fidelity_accounting.py — Knowledge Fidelity as Corporate Accounting
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Knowledge fidelity is the real balance sheet.
When decisions are made from degraded knowledge with blocked feedback,
the risk doesn't disappear — it gets externalized to the field
(soil, water, health, community).

Corporate accounting hides this. This module makes it visible.

The loop:
    Knowledge Node (fidelity, openness)
        -> Decision (quality, risk externalization)
            -> Field Impact (soil, nutrients, waste, coupling)
                -> Feedback (if not blocked: updates fidelity)
                -> If blocked: exponential degradation

Fidelity F = weighted score of:
    C = coherence (1 - internal contradiction)
    R = replication (successful replications / attempts)
    P = precision (1 - abstraction penalty)
    A = alignment (1 - constraint violation)
    T = temporal stability (duration / expected timescale)

When F is high and the decision is rejected anyway → system error.
When feedback is blocked → F can't self-correct → exponential collapse.

This is the accounting that matters. Not quarterly earnings.

USAGE:
    python -m sim.fidelity_accounting
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


# =============================================================================
# KNOWLEDGE NODE — the real asset
# =============================================================================

@dataclass
class KnowledgeNode:
    """
    A unit of knowledge with measurable fidelity.
    Fidelity = how much this knowledge reflects reality.
    """
    name: str
    value: float = 1.0              # what this knowledge is worth
    fidelity: float = 0.9           # 0-1: how accurately it reflects reality
    openness: float = 0.8           # 0-1: how freely it can flow
    feedback_blocked: bool = False  # is the feedback channel suppressed?

    # Fidelity components (CRPAT)
    coherence: float = 0.9          # 1 - internal contradiction
    replication: float = 0.8        # successful replications / attempts
    precision: float = 0.85         # 1 - abstraction penalty
    alignment: float = 0.9          # 1 - constraint violation score
    temporal_stability: float = 0.8 # duration / expected timescale

    def compute_fidelity(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        F = weighted combination of C, R, P, A, T.
        This is the real balance sheet metric.
        """
        if weights is None:
            weights = {"C": 0.2, "R": 0.2, "P": 0.2, "A": 0.2, "T": 0.2}
        self.fidelity = (
            self.coherence * weights["C"] +
            self.replication * weights["R"] +
            self.precision * weights["P"] +
            self.alignment * weights["A"] +
            self.temporal_stability * weights["T"]
        )
        self.fidelity = max(0, min(1, self.fidelity))
        return self.fidelity


# =============================================================================
# DECISION — what happens when knowledge meets incentive
# =============================================================================

@dataclass
class Decision:
    """Result of applying knowledge through an incentive structure."""
    quality: float = 1.0            # 0-1: how good is this decision?
    risk_externalization: float = 0.0  # 0-1: how much risk pushed to field
    source_node: str = ""


def decision_from_knowledge(node: KnowledgeNode,
                             incentive_bias: float = 0.5) -> Decision:
    """
    Decision quality degrades with:
    - Low knowledge fidelity (bad information)
    - High incentive bias * low openness (information can't flow freely)

    The distortion IS the risk externalization.
    What you don't know (or can't say) becomes someone else's problem.
    """
    distortion = (1 - node.fidelity) + incentive_bias * (1 - node.openness)
    distortion = min(1.0, max(0.0, distortion))
    return Decision(
        quality=max(0, 1 - distortion),
        risk_externalization=distortion,
        source_node=node.name,
    )


# =============================================================================
# FIELD STATE — where externalized risk lands
# =============================================================================

@dataclass
class FieldState:
    """
    The physical field that absorbs externalized decisions.
    Same variables as field_system.py but tracking degradation source.
    """
    soil_trend: float = 0.8         # -1 to 1 (positive = building)
    nutrient_density: float = 0.9   # 0-1
    waste_factor: float = 0.1       # 0-1 (lower = less waste)
    coupling_strength: float = 0.7  # ecological coupling (k in field_system)
    disturbance: float = 0.1        # 0-1 (lower = less disturbed)
    water_quality: float = 0.9      # 0-1

    def health_score(self) -> float:
        """Aggregate field health. 0 = destroyed, 1 = pristine."""
        return (
            max(0, self.soil_trend) * 0.2 +
            self.nutrient_density * 0.2 +
            (1 - self.waste_factor) * 0.15 +
            self.coupling_strength * 0.2 +
            (1 - self.disturbance) * 0.1 +
            self.water_quality * 0.15
        )


def apply_decision_to_field(state: FieldState, decision: Decision) -> FieldState:
    """
    Externalized risk degrades the field.
    The higher the risk_externalization, the more damage.
    This is the hidden cost that corporate accounting ignores.
    """
    L = min(decision.risk_externalization, 1.0)

    state.soil_trend -= 0.2 * L
    state.nutrient_density -= 0.3 * L
    state.waste_factor += 0.25 * L
    state.coupling_strength -= 0.3 * L
    state.disturbance += 0.3 * L
    state.water_quality -= 0.15 * L

    # Clamp
    state.soil_trend = max(-1, min(1, state.soil_trend))
    state.nutrient_density = max(0, min(1, state.nutrient_density))
    state.waste_factor = max(0, min(1, state.waste_factor))
    state.coupling_strength = max(0, min(1, state.coupling_strength))
    state.disturbance = max(0, min(1, state.disturbance))
    state.water_quality = max(0, min(1, state.water_quality))

    return state


# =============================================================================
# FEEDBACK — the channel that corrects or collapses
# =============================================================================

def feedback_to_knowledge(node: KnowledgeNode, state: FieldState) -> KnowledgeNode:
    """
    If feedback is not blocked: field degradation updates fidelity.
    The knowledge learns from the damage it caused.

    If feedback IS blocked: no update. Fidelity stays wrong.
    Next decision is worse. Field degrades more. Exponential.
    """
    if node.feedback_blocked:
        return node  # no correction possible

    # Measure degradation
    degradation = (
        (1 - state.nutrient_density) +
        state.waste_factor +
        state.disturbance
    ) / 3

    # Update fidelity (harsh — degradation directly lowers fidelity)
    node.fidelity -= 0.5 * degradation
    node.fidelity = max(0, min(1, node.fidelity))

    # Also update component scores
    node.alignment -= 0.3 * degradation
    node.alignment = max(0, node.alignment)
    node.temporal_stability -= 0.1 * degradation
    node.temporal_stability = max(0, node.temporal_stability)

    return node


# =============================================================================
# AGGREGATE — multiple knowledge inputs
# =============================================================================

def aggregate_knowledge(nodes: List[KnowledgeNode]) -> float:
    """
    Weighted average of knowledge values, weighted by fidelity.
    High-fidelity knowledge counts more. Low-fidelity gets discounted.
    """
    total_weight = 0.0
    weighted = 0.0
    for node in nodes:
        weight = node.fidelity
        weighted += node.value * weight
        total_weight += weight
    return weighted / total_weight if total_weight > 0 else 0


def detect_system_errors(nodes: List[KnowledgeNode],
                          rejection_threshold: float = 0.7) -> List[Dict]:
    """
    When high-fidelity knowledge is rejected by the system,
    that's a system error — not a knowledge error.

    F > threshold AND rejected → the system is filtering out
    accurate information. This is the inversion pattern.
    """
    errors = []
    for node in nodes:
        if node.fidelity > rejection_threshold and node.openness < 0.3:
            errors.append({
                "node": node.name,
                "fidelity": round(node.fidelity, 3),
                "openness": round(node.openness, 3),
                "error_type": "high_fidelity_suppressed",
                "interpretation": f"{node.name} has F={node.fidelity:.2f} "
                                  f"but openness={node.openness:.2f} — "
                                  f"accurate knowledge being blocked",
            })
    return errors


# =============================================================================
# SIMULATION — run the full feedback loop
# =============================================================================

def simulate_fidelity_loop(node: KnowledgeNode, state: FieldState,
                            incentive_bias: float = 0.5,
                            steps: int = 20) -> Dict:
    """
    Run the full loop:
        Knowledge -> Decision -> Field Impact -> Feedback -> Knowledge update

    Returns history of fidelity, field health, and decision quality.
    """
    history = {
        "fidelity": [], "field_health": [], "decision_quality": [],
        "risk_externalized": [], "step": [],
    }

    for t in range(steps):
        # Recompute fidelity from components
        node.compute_fidelity()

        # Make decision
        decision = decision_from_knowledge(node, incentive_bias)

        # Apply to field
        state = apply_decision_to_field(state, decision)

        # Feedback (if not blocked)
        node = feedback_to_knowledge(node, state)

        # Record
        history["step"].append(t)
        history["fidelity"].append(round(node.fidelity, 4))
        history["field_health"].append(round(state.health_score(), 4))
        history["decision_quality"].append(round(decision.quality, 4))
        history["risk_externalized"].append(round(decision.risk_externalization, 4))

    return history


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  FIDELITY ACCOUNTING — the real balance sheet")
    print("  knowledge fidelity drives everything downstream")
    print("=" * 60)

    # --- Scenario 1: Open feedback (self-correcting) ---
    print(f"\n  SCENARIO 1: Open feedback (healthy system)")
    node_open = KnowledgeNode("soil_knowledge", fidelity=0.7, openness=0.8)
    field_open = FieldState()
    hist_open = simulate_fidelity_loop(node_open, field_open,
                                        incentive_bias=0.3, steps=15)

    for t in [0, 4, 9, 14]:
        print(f"    t={t:2d}: F={hist_open['fidelity'][t]:.3f}  "
              f"field={hist_open['field_health'][t]:.3f}  "
              f"decision={hist_open['decision_quality'][t]:.3f}  "
              f"risk_ext={hist_open['risk_externalized'][t]:.3f}")

    # --- Scenario 2: Blocked feedback (exponential collapse) ---
    print(f"\n  SCENARIO 2: Feedback blocked (institutional inversion)")
    node_blocked = KnowledgeNode("soil_knowledge", fidelity=0.7, openness=0.8,
                                  feedback_blocked=True)
    field_blocked = FieldState()
    hist_blocked = simulate_fidelity_loop(node_blocked, field_blocked,
                                           incentive_bias=0.3, steps=15)

    for t in [0, 4, 9, 14]:
        print(f"    t={t:2d}: F={hist_blocked['fidelity'][t]:.3f}  "
              f"field={hist_blocked['field_health'][t]:.3f}  "
              f"decision={hist_blocked['decision_quality'][t]:.3f}  "
              f"risk_ext={hist_blocked['risk_externalized'][t]:.3f}")

    # --- Scenario 3: High incentive bias (corporate) ---
    print(f"\n  SCENARIO 3: High incentive bias (corporate accounting)")
    node_corp = KnowledgeNode("market_knowledge", fidelity=0.9, openness=0.3)
    field_corp = FieldState()
    hist_corp = simulate_fidelity_loop(node_corp, field_corp,
                                        incentive_bias=0.8, steps=15)

    for t in [0, 4, 9, 14]:
        print(f"    t={t:2d}: F={hist_corp['fidelity'][t]:.3f}  "
              f"field={hist_corp['field_health'][t]:.3f}  "
              f"decision={hist_corp['decision_quality'][t]:.3f}  "
              f"risk_ext={hist_corp['risk_externalized'][t]:.3f}")

    # --- System error detection ---
    print(f"\n  SYSTEM ERROR DETECTION:")
    test_nodes = [
        KnowledgeNode("elder_soil_knowledge", fidelity=0.95, openness=0.2),
        KnowledgeNode("corporate_projection", fidelity=0.3, openness=0.9),
        KnowledgeNode("indigenous_water_knowledge", fidelity=0.9, openness=0.15),
    ]
    errors = detect_system_errors(test_nodes)
    for e in errors:
        print(f"    {e['interpretation']}")

    if not errors:
        print(f"    No system errors detected")

    # --- Comparison ---
    print(f"\n{'='*60}")
    print("  THE COMPARISON")
    print(f"{'='*60}")

    final_open = hist_open['field_health'][-1]
    final_blocked = hist_blocked['field_health'][-1]
    final_corp = hist_corp['field_health'][-1]

    print(f"""
  After 15 steps:

    Open feedback:    field health = {final_open:.3f}
    Blocked feedback: field health = {final_blocked:.3f}
    Corporate bias:   field health = {final_corp:.3f}

  When feedback flows, the system self-corrects.
  When feedback is blocked, the field absorbs the error.
  When incentive bias is high AND openness is low,
  high-fidelity knowledge gets suppressed and the field
  degrades even though the knowledge existed to prevent it.

  That's the accounting that matters:
    Observation -> Fidelity Score -> Decision Weight
         |
    Field Outcome -> Feedback -> Fidelity Update

  Block any link in that loop and the cost shows up
  in the soil, the water, the health, the community.

  Corporate quarterly reports don't track soil_trend.
  This does.
""")
