#!/usr/bin/env python3
# MODULE: sim/resource_flow_dynamics.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: python -m sim.resource_flow_dynamics
# TIER: domain
# Coupled resource flow dynamics — hoarding vs circulation
"""
sim/resource_flow_dynamics.py — Coupled Resource Flow Dynamics
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Originally from github.com/JinnZ2/Inversion/scripts/resource_flow_dynamics.py
Ported to stdlib (no numpy).

Models hoarding vs circulation vs coupling in resource systems.
When agents hoard (high extraction, low release), circulation drops,
responsiveness degrades, and throughput collapses.

The same dynamics govern:
  - Water rights monopolization
  - Knowledge hoarding (coupling.py knowledge decay)
  - Capital concentration
  - Energy grid centralization

Single-pool and multi-agent networked versions.

USAGE:
    python -m sim.resource_flow_dynamics
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# =============================================================================
# SINGLE-POOL MODEL
# =============================================================================

@dataclass
class FlowParams:
    """Parameters for single-pool H/C/R dynamics."""
    alpha: float = 0.08    # extraction rate (C -> H)
    beta: float = 0.02     # release rate (H -> C)
    delta: float = 0.04    # productivity (C generates more C)
    gamma: float = 0.02    # dissipation (entropy loss from C)
    k1: float = 0.005      # responsiveness degradation rate
    k2: float = 0.010      # responsiveness recovery rate
    C_ref: float = 100.0   # reference C level for signal normalization
    dt: float = 0.1        # time step


@dataclass
class FlowState:
    """State of a single-pool system."""
    C: float = 100.0       # circulating resource
    H: float = 10.0        # hoarded/stored resource
    R: float = 1.0         # responsiveness (coupling efficiency, 0-1)


def step_single(state: FlowState, params: FlowParams) -> FlowState:
    """Advance single-pool system by one time step."""
    C, H, R = state.C, state.H, state.R
    dt = params.dt

    extraction = params.alpha * C
    release = params.beta * H
    productivity = params.delta * C * R
    dissipation = params.gamma * C
    signal = C / params.C_ref

    dC = -extraction + release + productivity - dissipation
    dH = extraction - release
    dR = -params.k1 * signal + params.k2 * (1.0 - R)

    return FlowState(
        C=max(0, C + dC * dt),
        H=max(0, H + dH * dt),
        R=max(0, min(1, R + dR * dt)),
    )


def run_single(params: FlowParams, initial: Optional[FlowState] = None,
               steps: int = 2000) -> Dict[str, List[float]]:
    """Run single-pool simulation. Returns time series."""
    state = initial or FlowState()
    history: Dict[str, List[float]] = {
        "C": [], "H": [], "R": [], "throughput": [], "total": [],
    }
    for _ in range(steps):
        throughput = params.delta * state.C * state.R
        history["C"].append(state.C)
        history["H"].append(state.H)
        history["R"].append(state.R)
        history["throughput"].append(throughput)
        history["total"].append(state.C + state.H)
        state = step_single(state, params)
    return history


# =============================================================================
# MULTI-AGENT NETWORKED MODEL (stdlib port)
# =============================================================================

@dataclass
class NetworkParams:
    """Parameters for multi-agent networked dynamics."""
    n_agents: int = 30
    kappa: float = 0.15           # network flow strength
    alpha: Optional[List[float]] = None
    beta: Optional[List[float]] = None
    delta: Optional[List[float]] = None
    gamma: Optional[List[float]] = None
    k1: float = 0.004
    k2: float = 0.008
    C_ref: float = 50.0
    dt: float = 0.05
    adjacency: Optional[List[List[float]]] = None

    def __post_init__(self):
        n = self.n_agents
        if self.alpha is None:
            self.alpha = [0.06] * n
        if self.beta is None:
            self.beta = [0.02] * n
        if self.delta is None:
            self.delta = [0.04] * n
        if self.gamma is None:
            self.gamma = [0.02] * n
        if self.adjacency is None:
            # Random row-stochastic adjacency
            A = []
            for i in range(n):
                row = [random.random() for _ in range(n)]
                row[i] = 0.0
                s = sum(row)
                row = [x / s if s > 0 else 0 for x in row]
                A.append(row)
            self.adjacency = A


@dataclass
class NetworkState:
    """State of a multi-agent network."""
    C: List[float]
    H: List[float]
    R: List[float]

    @classmethod
    def default(cls, n: int, seed: int = 42) -> "NetworkState":
        random.seed(seed)
        return cls(
            C=[max(10, 50 + 10 * random.gauss(0, 1)) for _ in range(n)],
            H=[10.0] * n,
            R=[1.0] * n,
        )


def network_flow(C: List[float], A: List[List[float]], kappa: float) -> List[float]:
    """Compute net flow for each agent from diffusion on adjacency."""
    n = len(C)
    net = [0.0] * n
    for i in range(n):
        for j in range(n):
            flow = kappa * A[i][j] * (C[i] - C[j])
            net[i] -= flow
            net[j] += flow  # what i loses, j gains (partially)
    return net


def step_network(state: NetworkState, params: NetworkParams) -> NetworkState:
    """Advance network by one time step."""
    n = params.n_agents
    C, H, R = state.C, state.H, state.R
    dt = params.dt

    nf = network_flow(C, params.adjacency, params.kappa)

    new_C, new_H, new_R = [], [], []
    for i in range(n):
        extraction = params.alpha[i] * C[i]
        release = params.beta[i] * H[i]
        productivity = params.delta[i] * C[i] * R[i]
        dissipation = params.gamma[i] * C[i]
        signal = C[i] / params.C_ref

        dC = -extraction + release + productivity - dissipation + nf[i]
        dH = extraction - release
        dR = -params.k1 * signal + params.k2 * (1.0 - R[i])

        new_C.append(max(0, C[i] + dC * dt))
        new_H.append(max(0, H[i] + dH * dt))
        new_R.append(max(0, min(1, R[i] + dR * dt)))

    return NetworkState(C=new_C, H=new_H, R=new_R)


def run_network(params: NetworkParams, steps: int = 800,
                hoarder_indices: Optional[List[int]] = None,
                seed: int = 42) -> Dict:
    """Run multi-agent network simulation."""
    random.seed(seed)

    if hoarder_indices:
        for i in hoarder_indices:
            params.alpha[i] = 0.10
            params.beta[i] = 0.005

    state = NetworkState.default(params.n_agents, seed)

    agg: Dict[str, List[float]] = {
        "total_C": [], "total_H": [], "total_throughput": [],
        "mean_R": [], "min_R": [],
    }

    for t in range(steps):
        throughput = sum(params.delta[i] * state.C[i] * state.R[i]
                         for i in range(params.n_agents))
        agg["total_C"].append(sum(state.C))
        agg["total_H"].append(sum(state.H))
        agg["total_throughput"].append(throughput)
        agg["mean_R"].append(sum(state.R) / params.n_agents)
        agg["min_R"].append(min(state.R))
        state = step_network(state, params)

    return {
        "aggregates": agg,
        "final_state": {"C": state.C, "H": state.H, "R": state.R},
        "hoarder_indices": hoarder_indices or [],
    }


def gini(arr: List[float]) -> float:
    """Gini coefficient (0 = equal, 1 = one agent has everything)."""
    arr = [abs(x) for x in arr]
    s = sum(arr)
    if s == 0:
        return 0.0
    sorted_arr = sorted(arr)
    n = len(sorted_arr)
    numerator = sum((2 * (i + 1) - n - 1) * x for i, x in enumerate(sorted_arr))
    return numerator / (n * s)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("  RESOURCE FLOW DYNAMICS — hoarding vs circulation")
    print("  same math: water rights, knowledge, capital, energy")
    print("=" * 60)

    # --- Single pool: healthy vs hoarding ---
    print(f"\n  SINGLE POOL:")
    healthy = run_single(FlowParams(alpha=0.04, beta=0.04))  # balanced
    hoarding = run_single(FlowParams(alpha=0.12, beta=0.005))  # hoarder

    for name, hist in [("Balanced", healthy), ("Hoarding", hoarding)]:
        final_C = hist["C"][-1]
        final_H = hist["H"][-1]
        final_R = hist["R"][-1]
        peak_tp = max(hist["throughput"])
        final_tp = hist["throughput"][-1]
        regime = "collapsed" if final_tp < 0.2 * peak_tp else "stable"
        print(f"    {name:10s}: C={final_C:.1f} H={final_H:.1f} R={final_R:.3f} "
              f"peak_tp={peak_tp:.2f} final_tp={final_tp:.2f} [{regime}]")

    # --- Network: with and without hoarders ---
    print(f"\n  NETWORK (30 agents):")

    # No hoarders
    params_fair = NetworkParams(n_agents=30)
    result_fair = run_network(params_fair, steps=500, seed=42)

    # 5 hoarders
    params_hoard = NetworkParams(n_agents=30)
    result_hoard = run_network(params_hoard, steps=500,
                                hoarder_indices=[0, 1, 2, 3, 4], seed=42)

    for name, result in [("No hoarders", result_fair),
                          ("5 hoarders", result_hoard)]:
        agg = result["aggregates"]
        final_tp = agg["total_throughput"][-1]
        peak_tp = max(agg["total_throughput"])
        final_R = agg["mean_R"][-1]
        g_C = gini(result["final_state"]["C"])
        g_H = gini(result["final_state"]["H"])
        regime = "collapsed" if final_tp < 0.2 * peak_tp else "stable"
        print(f"    {name:14s}: throughput={final_tp:.1f}/{peak_tp:.1f} "
              f"R={final_R:.3f} gini_C={g_C:.3f} gini_H={g_H:.3f} [{regime}]")

    print(f"\n  When 5 out of 30 agents hoard (extract 10%, release 0.5%),")
    print(f"  the entire network's throughput and responsiveness degrade.")
    print(f"  The Gini coefficient shows concentration.")
    print(f"  Same dynamics: water monopolization, knowledge silos, capital.")

    print(f"\n{'='*60}\n")
