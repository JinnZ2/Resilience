#!/usr/bin/env python3
"""
Dissipative Systems Simulation — Institutional Thermodynamics of Inversion

Models institutions as open thermodynamic systems that maintain internal order
(low entropy) by exporting entropy to their environment — Prigogine's
dissipative structures framework applied to organizational dynamics.

Each institution has:
  - Internal entropy S_i (disorder, accumulated contradictions)
  - Energy throughput Φ (resources, information, legitimacy flowing through)
  - Dissipation channels: pathways that export entropy (feedback loops,
    transparency, accountability, adaptive reform)
  - Coupling to environment and other institutions

An "inversion" is modeled as a dissipation channel blockage: the institution
can no longer export entropy through legitimate means. Internal entropy
accumulates until a phase transition (collapse or restructuring).

Key thermodynamic principles:
  - Second Law: dS_total/dt ≥ 0 (total entropy of system + environment
    never decreases)
  - Steady state: dS_i/dt = σ_i - J_e,i where σ_i is internal entropy
    production and J_e,i is entropy export rate
  - Minimum entropy production (Prigogine): near-equilibrium steady states
    minimize σ, but far-from-equilibrium systems can form ordered structures
  - Blocked dissipation: when J_e → 0, dS_i/dt → σ_i > 0, entropy
    accumulates monotonically → system destabilization

Metrics tracked:
  - Internal entropy S_i per institution
  - Entropy production rate σ_i = dS_i/dt + J_e,i
  - Entropy export rate J_e,i through each dissipation channel
  - Free energy F = E - T·S (capacity for useful work)
  - Coupling entropy: mutual information between institutions
  - Phase transition detection: when S_i exceeds critical threshold

References:
  - Prigogine (1967): Introduction to Thermodynamics of Irreversible Processes
  - Prigogine & Stengers (1984): Order Out of Chaos
  - Kondepudi & Prigogine (1998): Modern Thermodynamics
  - Schneider & Kay (1994): Life as a manifestation of the second law
  - Kauffman (1993): Origins of Order — self-organization at the edge of chaos
  - England (2013): Statistical physics of self-replication
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Core thermodynamic model
# ---------------------------------------------------------------------------

@dataclass
class DissipationChannel:
    """A pathway through which an institution exports entropy.

    Examples: public accountability, competitive markets, free press,
    scientific peer review, democratic elections, whistleblower protections.
    """
    name: str
    conductance: float       # how effectively it exports entropy [0, 1]
    base_conductance: float  # original conductance before any blockage
    blocked: bool = False    # whether this channel has been inverted/blocked


@dataclass
class Institution:
    """An open thermodynamic system maintaining internal order."""
    name: str
    internal_entropy: float          # S_i: accumulated disorder (nats)
    energy_throughput: float          # Φ: resource/information flow rate
    temperature: float                # T: "operational temperature" (activity level)
    channels: list[DissipationChannel] = field(default_factory=list)

    # Derived quantities (computed each tick)
    entropy_production: float = 0.0   # σ_i: rate of internal entropy generation
    entropy_export: float = 0.0       # J_e,i: total entropy exported per tick
    free_energy: float = 0.0          # F = Φ - T·S (capacity for useful work)

    @property
    def total_conductance(self) -> float:
        """Sum of active channel conductances."""
        return sum(c.conductance for c in self.channels if not c.blocked)

    @property
    def blocked_fraction(self) -> float:
        """Fraction of dissipation channels that are blocked."""
        if not self.channels:
            return 0.0
        return sum(1 for c in self.channels if c.blocked) / len(self.channels)


@dataclass
class SystemConfig:
    """Configuration for the dissipative systems simulation."""
    n_institutions: int = 5
    ticks: int = 300
    dt: float = 0.1

    # Thermodynamic parameters
    base_energy: float = 10.0        # baseline energy throughput
    base_temperature: float = 1.0     # baseline operational temperature
    entropy_prod_coeff: float = 0.15  # σ = coeff * Φ * (1 + S/S_crit)
    export_coeff: float = 1.0         # J_e = coeff * conductance * S * T

    # Dissipation channels per institution
    n_channels: int = 5
    channel_conductance_min: float = 0.3
    channel_conductance_max: float = 0.9

    # Coupling between institutions
    coupling_strength: float = 0.02   # entropy transfer between coupled institutions

    # Inversion parameters
    inversion_onset: int = 50         # tick when inversions begin
    inversion_rate: float = 0.03      # probability per tick per channel of blockage
    inversion_max_fraction: float = 0.8  # max fraction of channels that get blocked

    # Phase transition
    critical_entropy: float = 5.0     # S_crit: entropy threshold for instability
    collapse_entropy: float = 10.0    # S at which institution collapses

    # Reconstitution
    enable_reconstitution: bool = False  # whether collapsed institutions can reform
    reconstitution_threshold: float = 8.0  # environment entropy that triggers reform

    seed: int = 42


@dataclass
class SystemState:
    """Measurable state of the full system at one time step."""
    tick: int
    institutions: list[dict]         # per-institution metrics
    total_entropy: float             # S_total = Σ S_i + S_env
    environment_entropy: float       # entropy absorbed by environment
    total_entropy_production: float  # Σ σ_i
    total_free_energy: float         # Σ F_i
    mean_blocked_fraction: float     # average channel blockage across institutions
    n_collapsed: int
    n_active: int


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

def create_institutions(cfg: SystemConfig, rng: random.Random) -> list[Institution]:
    """Initialize institutions with dissipation channels."""
    names = [
        "Governance", "Academy", "Market", "Media", "Commons",
        "Judiciary", "Healthcare", "Education", "Infrastructure", "Culture",
    ]
    institutions = []
    for i in range(cfg.n_institutions):
        name = names[i] if i < len(names) else f"Institution-{i}"
        channels = []
        channel_names = [
            "Transparency", "Accountability", "Competition",
            "Feedback", "Reform",
            "Peer-review", "Elections", "Audit",
            "Whistleblower", "Public-discourse",
        ]
        for j in range(cfg.n_channels):
            cname = channel_names[j] if j < len(channel_names) else f"Channel-{j}"
            cond = rng.uniform(cfg.channel_conductance_min, cfg.channel_conductance_max)
            channels.append(DissipationChannel(
                name=cname,
                conductance=cond,
                base_conductance=cond,
            ))
        inst = Institution(
            name=name,
            internal_entropy=rng.uniform(0.5, 1.5),  # start with some disorder
            energy_throughput=cfg.base_energy * rng.uniform(0.8, 1.2),
            temperature=cfg.base_temperature * rng.uniform(0.9, 1.1),
            channels=channels,
        )
        institutions.append(inst)
    return institutions


def compute_entropy_production(inst: Institution, cfg: SystemConfig) -> float:
    """Internal entropy production rate σ_i.

    σ increases with energy throughput (more activity = more waste heat)
    and accelerates as internal entropy approaches critical threshold
    (positive feedback: disorder begets more disorder).

    σ_i = coeff * Φ_i * (1 + S_i / S_crit)

    This reflects the thermodynamic principle that systems far from
    equilibrium with blocked dissipation produce entropy at accelerating
    rates (Kondepudi & Prigogine, 1998, Ch. 17).
    """
    return cfg.entropy_prod_coeff * inst.energy_throughput * (
        1.0 + inst.internal_entropy / cfg.critical_entropy
    )


def compute_entropy_export(inst: Institution, cfg: SystemConfig) -> float:
    """Entropy export rate J_e,i through active dissipation channels.

    J_e = export_coeff * G_total * S * T

    where G_total is the sum of active channel conductances. When channels
    are blocked, G_total decreases, reducing the institution's ability
    to export entropy — the core mechanism of inversion.
    """
    g_total = inst.total_conductance
    return cfg.export_coeff * g_total * inst.internal_entropy * inst.temperature


def apply_inversions(
    institutions: list[Institution], tick: int, cfg: SystemConfig, rng: random.Random,
) -> int:
    """Stochastically block dissipation channels (model inversions).

    Returns the number of channels blocked this tick.
    """
    if tick < cfg.inversion_onset:
        return 0

    blocked_count = 0
    for inst in institutions:
        if inst.internal_entropy >= cfg.collapse_entropy:
            continue  # already collapsed, skip
        for ch in inst.channels:
            if ch.blocked:
                continue
            if inst.blocked_fraction >= cfg.inversion_max_fraction:
                break  # enough channels blocked for this institution
            if rng.random() < cfg.inversion_rate:
                ch.blocked = True
                ch.conductance = 0.0
                blocked_count += 1
    return blocked_count


def entropy_coupling(
    institutions: list[Institution], cfg: SystemConfig,
) -> list[float]:
    """Compute entropy transfer between coupled institutions.

    High-entropy institutions "leak" disorder to their neighbors.
    This models institutional contagion: when one institution becomes
    dysfunctional, it degrades the institutions it interacts with.

    Uses a mean-field coupling: each institution feels the average
    entropy of all others, weighted by coupling strength.

    ΔS_i = coupling * (S_mean - S_i)

    This drives entropy toward equalization — a thermodynamic
    equilibration process.
    """
    n = len(institutions)
    if n <= 1:
        return [0.0] * n

    active = [inst for inst in institutions if inst.internal_entropy < cfg.collapse_entropy]
    if not active:
        return [0.0] * n

    s_mean = sum(inst.internal_entropy for inst in active) / len(active)

    transfers = []
    for inst in institutions:
        if inst.internal_entropy >= cfg.collapse_entropy:
            transfers.append(0.0)
        else:
            transfers.append(cfg.coupling_strength * (s_mean - inst.internal_entropy))
    return transfers


def measure_system(
    tick: int, institutions: list[Institution], env_entropy: float, cfg: SystemConfig,
) -> SystemState:
    """Compute system-wide metrics."""
    inst_data = []
    total_s = env_entropy
    total_sigma = 0.0
    total_f = 0.0
    n_collapsed = 0
    n_active = 0

    for inst in institutions:
        collapsed = inst.internal_entropy >= cfg.collapse_entropy
        if collapsed:
            n_collapsed += 1
        else:
            n_active += 1

        inst.free_energy = inst.energy_throughput - inst.temperature * inst.internal_entropy
        total_s += inst.internal_entropy
        total_sigma += inst.entropy_production
        total_f += max(0.0, inst.free_energy)

        inst_data.append({
            "name": inst.name,
            "S": round(inst.internal_entropy, 4),
            "sigma": round(inst.entropy_production, 4),
            "J_e": round(inst.entropy_export, 4),
            "F": round(inst.free_energy, 4),
            "blocked": round(inst.blocked_fraction, 3),
            "collapsed": collapsed,
        })

    blocked_fracs = [inst.blocked_fraction for inst in institutions
                     if inst.internal_entropy < cfg.collapse_entropy]
    mean_blocked = sum(blocked_fracs) / len(blocked_fracs) if blocked_fracs else 0.0

    return SystemState(
        tick=tick,
        institutions=inst_data,
        total_entropy=round(total_s, 4),
        environment_entropy=round(env_entropy, 4),
        total_entropy_production=round(total_sigma, 4),
        total_free_energy=round(total_f, 4),
        mean_blocked_fraction=round(mean_blocked, 3),
        n_collapsed=n_collapsed,
        n_active=n_active,
    )


def run_simulation(cfg: SystemConfig, quiet: bool = False) -> list[SystemState]:
    """Run the dissipative systems simulation.

    Each tick:
      1. Compute internal entropy production σ_i for each institution.
      2. Compute entropy export J_e,i through active dissipation channels.
      3. Apply entropy coupling between institutions.
      4. Update internal entropy: dS_i = (σ_i - J_e,i + coupling_i) · dt
      5. Update environment entropy: dS_env = Σ J_e,i · dt
      6. Stochastically block channels (apply inversions).
      7. Detect phase transitions (collapse).
    """
    rng = random.Random(cfg.seed)
    institutions = create_institutions(cfg, rng)
    env_entropy = 0.0  # entropy absorbed by the environment

    history: list[SystemState] = []
    state = measure_system(0, institutions, env_entropy, cfg)
    history.append(state)

    if not quiet:
        print("=" * 95)
        print("  DISSIPATIVE SYSTEMS SIMULATION — Institutional Thermodynamics")
        print(f"  {cfg.n_institutions} institutions, {cfg.n_channels} channels each, {cfg.ticks} ticks")
        print(f"  Inversions: onset=t{cfg.inversion_onset}, rate={cfg.inversion_rate}/tick/channel")
        print("=" * 95)
        _print_tick(state, verbose=False)

    for tick in range(1, cfg.ticks + 1):
        # 1-2. Entropy production and export
        for inst in institutions:
            if inst.internal_entropy >= cfg.collapse_entropy:
                inst.entropy_production = 0.0
                inst.entropy_export = 0.0
                continue
            inst.entropy_production = compute_entropy_production(inst, cfg)
            inst.entropy_export = compute_entropy_export(inst, cfg)

        # 3. Coupling
        coupling = entropy_coupling(institutions, cfg)

        # 4-5. Update entropies
        total_exported = 0.0
        for i, inst in enumerate(institutions):
            if inst.internal_entropy >= cfg.collapse_entropy:
                continue
            ds = (inst.entropy_production - inst.entropy_export + coupling[i]) * cfg.dt
            inst.internal_entropy = max(0.0, inst.internal_entropy + ds)
            total_exported += inst.entropy_export * cfg.dt

        env_entropy += total_exported  # environment absorbs exported entropy

        # 6. Apply inversions (block channels)
        apply_inversions(institutions, tick, cfg, rng)

        # 7. Detect collapses
        for inst in institutions:
            if inst.internal_entropy >= cfg.collapse_entropy:
                # Collapse: dump remaining entropy to environment
                if inst.entropy_production > 0:  # first time collapsing
                    env_entropy += inst.internal_entropy * 0.5  # catastrophic release
                    inst.entropy_production = 0.0
                    inst.entropy_export = 0.0

        state = measure_system(tick, institutions, env_entropy, cfg)
        history.append(state)

        if not quiet and (tick % 20 == 0 or state.n_collapsed != history[-2].n_collapsed):
            _print_tick(state, verbose=False)

        if state.n_active == 0:
            if not quiet:
                print(f"\n  *** ALL INSTITUTIONS COLLAPSED at t={tick} ***")
                print(f"  Total system entropy: {state.total_entropy:.4f}")
                print(f"  Environment entropy:  {state.environment_entropy:.4f}")
            break

    if not quiet and state.n_active > 0:
        print(f"\n  Simulation completed: {cfg.ticks} ticks")
        print(f"  Active: {state.n_active}, Collapsed: {state.n_collapsed}")
        print(f"  Total entropy: {state.total_entropy:.4f}")
        print(f"  Total free energy: {state.total_free_energy:.4f}")
        print(f"  Environment entropy: {state.environment_entropy:.4f}")

    return history


def _print_tick(state: SystemState, verbose: bool = True) -> None:
    """Print a single tick's state."""
    active_str = f"active={state.n_active}"
    collapsed_str = f"collapsed={state.n_collapsed}" if state.n_collapsed > 0 else ""
    line = (
        f"  t={state.tick:>4}  "
        f"S_total={state.total_entropy:>7.3f}  "
        f"σ_total={state.total_entropy_production:>6.3f}  "
        f"F_total={state.total_free_energy:>7.3f}  "
        f"blocked={state.mean_blocked_fraction:.2f}  "
        f"{active_str}"
    )
    if collapsed_str:
        line += f"  {collapsed_str}"
    print(line)

    if verbose:
        for d in state.institutions:
            status = "COLLAPSED" if d["collapsed"] else "active"
            print(
                f"    {d['name']:>15}: S={d['S']:>6.3f}  "
                f"σ={d['sigma']:>5.3f}  J_e={d['J_e']:>5.3f}  "
                f"F={d['F']:>7.3f}  blocked={d['blocked']:.2f}  [{status}]"
            )


def run_comparison(cfg: SystemConfig) -> None:
    """Compare scenarios: no inversions, moderate inversions, aggressive inversions."""
    scenarios = [
        ("No inversions (control)", 0.0, 0.0),
        ("Moderate inversions", 0.02, 0.6),
        ("Aggressive inversions", 0.06, 0.9),
    ]

    print("=" * 95)
    print("  SCENARIO COMPARISON — Dissipative Institutional Systems")
    print("=" * 95)

    for name, rate, max_frac in scenarios:
        scfg = SystemConfig(
            **{
                **cfg.__dict__,
                "inversion_rate": rate,
                "inversion_max_fraction": max_frac,
            }
        )
        history = run_simulation(scfg, quiet=True)
        final = history[-1]

        if final.n_active == 0:
            outcome = f"ALL COLLAPSED at t={final.tick}"
        elif final.n_collapsed > 0:
            outcome = f"{final.n_collapsed}/{cfg.n_institutions} collapsed"
        else:
            outcome = "All institutions stable"

        # Find peak entropy production
        peak_sigma = max(s.total_entropy_production for s in history)
        peak_sigma_tick = next(
            s.tick for s in history if s.total_entropy_production == peak_sigma
        )

        print(f"\n  {name}")
        print(f"    Outcome:           {outcome}")
        print(f"    Final S_total    = {final.total_entropy:.4f}")
        print(f"    Final F_total    = {final.total_free_energy:.4f}")
        print(f"    S_environment    = {final.environment_entropy:.4f}")
        print(f"    Peak σ           = {peak_sigma:.4f} at t={peak_sigma_tick}")
        print(f"    Mean blocked     = {final.mean_blocked_fraction:.2f}")

        # Show per-institution final state
        for d in final.institutions:
            status = "COLLAPSED" if d["collapsed"] else f"S={d['S']:.3f}"
            print(f"      {d['name']:>15}: {status}")

    print()


def run_json_output(cfg: SystemConfig) -> None:
    """Output full simulation history as JSON."""
    history = run_simulation(cfg, quiet=True)
    output = {
        "config": {
            "n_institutions": cfg.n_institutions,
            "ticks": cfg.ticks,
            "dt": cfg.dt,
            "inversion_onset": cfg.inversion_onset,
            "inversion_rate": cfg.inversion_rate,
            "critical_entropy": cfg.critical_entropy,
            "collapse_entropy": cfg.collapse_entropy,
        },
        "history": [
            {
                "tick": s.tick,
                "total_entropy": s.total_entropy,
                "environment_entropy": s.environment_entropy,
                "total_entropy_production": s.total_entropy_production,
                "total_free_energy": s.total_free_energy,
                "mean_blocked_fraction": s.mean_blocked_fraction,
                "n_active": s.n_active,
                "n_collapsed": s.n_collapsed,
                "institutions": s.institutions,
            }
            for s in history
        ],
    }
    json.dump(output, sys.stdout, indent=2)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Dissipative systems simulation: models institutions as open "
            "thermodynamic systems that maintain order through entropy export. "
            "Inversions block dissipation channels, causing entropy accumulation "
            "and eventual phase transitions (collapse)."
        ),
    )
    parser.add_argument(
        "--institutions", type=int, default=5,
        help="Number of institutions (default: 5)",
    )
    parser.add_argument(
        "--channels", type=int, default=5,
        help="Dissipation channels per institution (default: 5)",
    )
    parser.add_argument(
        "--ticks", type=int, default=300,
        help="Simulation time steps (default: 300)",
    )
    parser.add_argument(
        "--dt", type=float, default=0.1,
        help="Time step size (default: 0.1)",
    )
    parser.add_argument(
        "--inversion-onset", type=int, default=50,
        help="Tick when inversions begin (default: 50)",
    )
    parser.add_argument(
        "--inversion-rate", type=float, default=0.03,
        help="Probability per tick per channel of blockage (default: 0.03)",
    )
    parser.add_argument(
        "--critical-entropy", type=float, default=5.0,
        help="Entropy threshold for accelerating instability (default: 5.0)",
    )
    parser.add_argument(
        "--collapse-entropy", type=float, default=10.0,
        help="Entropy threshold for institutional collapse (default: 10.0)",
    )
    parser.add_argument(
        "--coupling", type=float, default=0.02,
        help="Inter-institutional entropy coupling strength (default: 0.02)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Compare three inversion scenarios side-by-side",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output full history as JSON",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-tick output",
    )
    args = parser.parse_args()

    cfg = SystemConfig(
        n_institutions=args.institutions,
        n_channels=args.channels,
        ticks=args.ticks,
        dt=args.dt,
        inversion_onset=args.inversion_onset,
        inversion_rate=args.inversion_rate,
        critical_entropy=args.critical_entropy,
        collapse_entropy=args.collapse_entropy,
        coupling_strength=args.coupling,
        seed=args.seed,
    )

    if args.compare:
        run_comparison(cfg)
    elif args.json:
        run_json_output(cfg)
    else:
        run_simulation(cfg, quiet=args.quiet)


if __name__ == "__main__":
    main()
