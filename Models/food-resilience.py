# MODULE: Models/food-resilience.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: demo
# Michaelis-Menten yield + ENSO forcing with reserve buffers
"""
Food System Resilience Model
Nonlinear yield with reserves buffer, asymmetric adaptation, parametric instability.
CC0 — No rights reserved.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Params:
    """All model parameters with defaults calibrated to US high-input agriculture."""
    Ymax: float = 1.0          # max yield (normalized)
    k: float = 0.15            # fertilizer sensitivity (Michaelis-Menten half-sat)
    alpha0: float = 0.8        # base weather vulnerability
    tau_F: float = 2.0         # fertilizer relaxation time (seasons)
    tau_alpha_plus: float = 8.0   # adaptation recovery (slow)
    tau_alpha_minus: float = 1.5  # adaptation degradation (fast)
    degrade_threshold: float = 0.65  # Y below this = degradation regime
    reserve_init: float = 0.30      # initial grain reserves
    consumption: float = 0.85       # fraction of yield consumed
    loss_base: float = 0.05         # baseline storage/logistics loss
    transport_cost_mult: float = 0.3  # how much energy cost amplifies losses
    enso_amplitude: float = 0.6     # ENSO forcing amplitude
    enso_period: float = 7.0        # ENSO period (seasons)
    hormuz_season: int = -1         # onset season (-1 = disabled)
    hormuz_depth: float = 0.4       # max fertilizer reduction
    hormuz_duration: int = 4        # shock duration (seasons)
    war_season: int = -1
    war_depth: float = 0.3
    war_duration: int = 6
    seasons: int = 40


@dataclass
class State:
    """Single timestep output."""
    t: int = 0
    Y: float = 0.0    # yield
    F: float = 1.0     # fertilizer availability
    W: float = 0.0     # weather stress
    alpha: float = 0.8 # weather vulnerability
    S: float = 0.3     # reserves
    P: float = 0.0     # price signal
    f_val: float = 0.0 # nutrient response
    g_val: float = 0.0 # weather response
    regime: str = "stable"


def f_nutrient(F: float, k: float) -> float:
    """Saturating nutrient response. Asymmetric on the downside."""
    return F / (F + k)


def g_weather(W: float, alpha: float) -> float:
    """Gaussian weather penalty. Modest anomalies small; extremes devastating."""
    return math.exp(-alpha * W * W)


def enso_forcing(t: int, amplitude: float, period: float) -> float:
    """Sinusoidal ENSO approximation."""
    return amplitude * math.sin(2 * math.pi * t / period)


def supply_shock(t: int, onset: int, depth: float, duration: int) -> float:
    """Cosine-ramped supply disruption. Returns multiplier on F (1.0 = no shock)."""
    if onset < 0:
        return 1.0
    dt = t - onset
    if dt < 0 or dt >= duration:
        return 1.0
    ramp = 0.5 * (1 - math.cos(math.pi * dt / duration))
    return 1.0 - depth * (1.0 - ramp)


def simulate(params: Params) -> List[State]:
    """Run full simulation. Returns list of State per season."""
    results = []
    F = 1.0
    alpha = params.alpha0
    S = params.reserve_init

    for t in range(params.seasons):
        # --- External forcing ---
        W = enso_forcing(t, params.enso_amplitude, params.enso_period)

        F_ext = (supply_shock(t, params.hormuz_season, params.hormuz_depth, params.hormuz_duration)
                 * supply_shock(t, params.war_season, params.war_depth, params.war_duration))

        # --- Fertilizer dynamics ---
        D = min(F_ext, 1.0)
        F = F + (1.0 / params.tau_F) * (D - F)
        F = max(0.01, min(1.0, F))

        # --- Yield ---
        fv = f_nutrient(F, params.k)
        gv = g_weather(W, alpha)
        Y = params.Ymax * fv * gv

        # --- Reserves ---
        L = params.loss_base + params.transport_cost_mult * (1.0 - F_ext)
        S = S + Y - params.consumption * Y - L
        S = max(0.0, S)

        # --- Price (hyperbolic on reserves) ---
        P = min(1.0 / (S + 0.05), 20.0)

        # --- Asymmetric alpha adaptation ---
        if Y < params.degrade_threshold:
            # Fast degradation
            alpha += ((1.0 / params.tau_alpha_minus)
                      * (params.alpha0 * 1.3 - alpha)
                      * (params.degrade_threshold - Y))
        else:
            # Slow recovery
            alpha -= ((1.0 / params.tau_alpha_plus)
                      * (alpha - params.alpha0 * 0.7)
                      * (Y - params.degrade_threshold))
        alpha = max(0.1, min(3.0, alpha))

        # --- Regime classification ---
        if F < 0.35 or Y < 0.3:
            regime = "degraded"
        elif F < 0.55 and abs(W) > 0.3:
            regime = "bifurcation"
        else:
            regime = "stable"

        results.append(State(
            t=t, Y=Y, F=F, W=W, alpha=alpha,
            S=S, P=P, f_val=fv, g_val=gv, regime=regime
        ))

    return results


def summary(results: List[State]) -> Dict:
    """Extract key diagnostics."""
    return {
        "min_yield": min(s.Y for s in results),
        "min_F": min(s.F for s in results),
        "max_alpha": max(s.alpha for s in results),
        "max_price": max(s.P for s in results),
        "degraded_seasons": sum(1 for s in results if s.regime == "degraded"),
        "bifurcation_seasons": sum(1 for s in results if s.regime == "bifurcation"),
        "final_reserves": results[-1].S,
        "final_alpha": results[-1].alpha,
    }


# ─── Run if called directly ────────────────────────────────────

if __name__ == "__main__":
    # Default: no shocks
    p = Params()
    res = simulate(p)
    s = summary(res)
    print("=== BASELINE (no shocks) ===")
    for k, v in s.items():
        print(f"  {k}: {v:.3f}")

    # Hormuz at season 8, war at season 12
    p2 = Params(hormuz_season=8, war_season=12)
    res2 = simulate(p2)
    s2 = summary(res2)
    print("\n=== HORMUZ(8) + WAR(12) ===")
    for k, v in s2.items():
        print(f"  {k}: {v:.3f}")

    # Show the ratchet: compare alpha before and after
    print(f"\n  Alpha ratchet: {p2.alpha0:.2f} → {res2[-1].alpha:.2f}")
    print(f"  Recovery would require {(res2[-1].alpha - p2.alpha0*0.7) * p2.tau_alpha_plus:.1f} good seasons")
